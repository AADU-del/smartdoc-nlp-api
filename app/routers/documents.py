from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import io

from app.databases import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.models.document import Document, AnalysisResult
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentStatusResponse

router = APIRouter()

def extract_text_from_file(filename: str, content_bytes: bytes) -> str:
    """
    Extracts plain text content from uploaded file bytes.
    Supports .txt, .md, .csv, .json, .pdf (if pypdf installed), etc.
    """
    lower_name = filename.lower()
    
    if lower_name.endswith('.pdf'):
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(content_bytes))
            text = ""
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            if text.strip():
                return text
        except ImportError:
            try:
                import PyPDF2
                reader = PyPDF2.PdfReader(io.BytesIO(content_bytes))
                text = ""
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
                if text.strip():
                    return text
            except ImportError:
                pass
        except Exception as e:
            print(f"Error parsing PDF file {filename}: {e}")

    # Fallback to UTF-8 decoding with fallback error handling for text-based formats
    return content_bytes.decode("utf-8", errors="ignore")


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
            summary=results.get("summary", ""),
            keywords=results.get("keywords", []),
            sentiment=results.get("sentiment", "NEUTRAL"),
            sentiment_score=results.get("sentiment_score", 0.5),
            entities=results.get("entities", [])
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
    Uploads document text content (JSON body) and triggers NLP analysis in background.
    Returns 202 Accepted.
    """
    if not doc_data.content or not doc_data.content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document content cannot be empty."
        )

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


@router.post("/upload-file", response_model=DocumentResponse, status_code=202)
async def upload_document_file(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    POST /api/v1/documents/upload-file
    Uploads a physical document file (.txt, .pdf, .md, etc.), extracts text, and triggers NLP analysis.
    Returns 202 Accepted.
    """
    content_bytes = await file.read()
    if not content_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty."
        )

    text_content = extract_text_from_file(file.filename, content_bytes)

    if not text_content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract text content from the uploaded file."
        )

    document = Document(
        user_id=current_user.id,
        filename=file.filename,
        content=text_content,
        status="pending"
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    background_tasks.add_task(
        run_nlp_analysis,
        document_id=document.id,
        text=text_content
    )

    return document


@router.get("/", response_model=List[DocumentResponse])
def get_my_documents(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of records to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GET /api/v1/documents/
    Returns paginated documents belonging to the current user.
    """
    documents = db.query(Document).filter(
        Document.user_id == current_user.id
    ).order_by(Document.created_at.desc()).offset(skip).limit(limit).all()
    
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