import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Text
from sqlalchemy.orm import sessionmaker, declarative_base

# Use the metadata folder for the SQLite DB
DB_PATH = os.path.join("6 Metadata", "studio.db")
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ImageRecord(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    original_path = Column(String)
    
    # Analysis Scores
    face_quality = Column(Float, default=0.0)
    smile_score = Column(Float, default=0.0)
    composition_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    
    # State tracking
    is_duplicate = Column(Boolean, default=False)
    is_selected = Column(Boolean, default=False)
    status = Column(String, default="raw") # raw, selected, enhanced, final
    
    # AI Generated Content
    captions_json = Column(Text, default="[]") # JSON list of captions
    quotes_json = Column(Text, default="[]") # JSON list of quotes
    hashtags = Column(Text, default="")
    recommended_song = Column(String, default="")
    posting_time = Column(String, default="")

def init_db():
    # Ensure the metadata folder exists first (handled by folders.py but safe to ensure path)
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
