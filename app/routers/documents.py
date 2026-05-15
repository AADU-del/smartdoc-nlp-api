

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List
from app.databases import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.models.document import Document, AnalysisResult
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentStatusResponse

router = APIRouter()

def run_nlp_analysis(document_id: int, text: str):
    """
    Background task — runs AFTER the HTTP response is sent.
    The client gets 202 instantly, NLP runs here in the background.
    This is how Notion AI, Google Docs, etc. handle slow operations.
    """
    
    from app.databases import SessionLocal
    from app.services.nlp_service import full_analysis

   
    db = SessionLocal()
    try:
      
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            return

        doc.status = "processing"
        db.commit()

     
        results = full_analysis(text)

    
        analysis = AnalysisResult(
            document_id=document_id,
            summary=results["summary"],
            keywords=results["keywords"],
            sentiment=results["sentiment"],
            sentiment_score=results["sentiment_score"],
            entities=results["entities"]
        )
        db.add(analysis)
        doc.status = "done"
        db.commit()

    except Exception as e:
        
        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc:
            doc.status = "failed"
            db.commit()
        print(f"NLP Analysis failed for document {document_id}: {e}")
    finally:
        
        db.close()


@router.post("/", response_model=DocumentResponse, status_code=202)
def upload_document(
    doc_data: DocumentCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    POST /api/v1/documents/
    Uploads a document and triggers NLP analysis in the background.
    Returns 202 Accepted — meaning "got it, working on it"
    The client should poll /documents/{id}/status to check progress
    """
   
    document = Document(
        user_id=current_user.id,
        filename=doc_data.filename,
        content=doc_data.content,
        status="pending"
    )
    db.add(document)
    db.commit()
    db.refresh(document)

   
    background_tasks.add_task(
        run_nlp_analysis,
        document_id=document.id,
        text=doc_data.content
    )

    return document


@router.get("/", response_model=List[DocumentResponse])
def get_my_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GET /api/v1/documents/
    Returns all documents belonging to the current user.
    Users can ONLY see their own documents — enforced by user_id filter.
    """
    documents = db.query(Document).filter(
        Document.user_id == current_user.id
    ).all()
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GET /api/v1/documents/{document_id}
    Returns a single document with its analysis results if ready.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id  
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    return document


@router.get("/{document_id}/status", response_model=DocumentStatusResponse)
def get_document_status(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GET /api/v1/documents/{document_id}/status
    Lightweight endpoint to check NLP processing status.
    Client polls this every few seconds after uploading.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    messages = {
        "pending": "Document uploaded. Analysis queued.",
        "processing": "NLP analysis in progress. Please wait.",
        "done": "Analysis complete. Results ready.",
        "failed": "Analysis failed. Please try uploading again."
    }

    return {
        "id": document.id,
        "filename": document.filename,
        "status": document.status,
        "message": messages.get(document.status, "Unknown status")
    }


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    DELETE /api/v1/documents/{document_id}
    Deletes a document and its analysis results (CASCADE handles DB cleanup).
    204 No Content = success with no response body
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    db.delete(document)
    db.commit()
    return None