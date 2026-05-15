
from sqlalchemy import (Column, Integer, String, Text,
                        Enum, TIMESTAMP, Float, ForeignKey, JSON)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.databases import Base

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)

 
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    filename = Column(String(255), nullable=False)

   
    content = Column(Text, nullable=False)

   
    status = Column(
        Enum("pending", "processing", "done", "failed"),
        default="pending",
        nullable=False
    )

    created_at = Column(TIMESTAMP, server_default=func.now())

   
    analysis_result = relationship("AnalysisResult", back_populates="document", uselist=False)

    def __repr__(self):
        return f"<Document id={self.id} filename={self.filename} status={self.status}>"


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, autoincrement=True)

    
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, unique=True)

    
    summary = Column(Text, nullable=True)

    
    keywords = Column(JSON, nullable=True)

    sentiment = Column(String(20), nullable=True)      
    sentiment_score = Column(Float, nullable=True)     

    entities = Column(JSON, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())

    document = relationship("Document", back_populates="analysis_result")

    def __repr__(self):
        return f"<AnalysisResult id={self.id} sentiment={self.sentiment}>"