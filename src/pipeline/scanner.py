import os
import glob
import logging
from src.core.database import SessionLocal, ImageRecord

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp')

def scan_raw_pics(raw_dir: str = "0 Raw Pics"):
    """Scans the raw pictures folder and adds new images to the database."""
    logger.info(f"Scanning {raw_dir} for new images...")
    
    db = SessionLocal()
    try:
        # Get all files with supported extensions
        files = []
        for ext in SUPPORTED_EXTENSIONS:
            # Case insensitive match by checking lowercase
            for file in os.listdir(raw_dir):
                if file.lower().endswith(ext):
                    files.append(os.path.join(raw_dir, file))
        
        new_count = 0
        for file_path in files:
            filename = os.path.basename(file_path)
            
            # Check if it exists in DB
            exists = db.query(ImageRecord).filter(ImageRecord.filename == filename).first()
            if not exists:
                new_record = ImageRecord(
                    filename=filename,
                    original_path=file_path,
                    status="raw"
                )
                db.add(new_record)
                new_count += 1
                
        db.commit()
        logger.info(f"Found {new_count} new images.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error during scan: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    scan_raw_pics()
