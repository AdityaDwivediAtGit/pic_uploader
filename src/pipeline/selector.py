import os
import shutil
import logging
from src.core.database import SessionLocal, ImageRecord

logger = logging.getLogger(__name__)

def run_selection(threshold: float = 20.0):
    """
    Selects the best non-duplicate images and copies them to '1 Selected Pics'.
    A higher threshold means stricter selection based on overall_score.
    """
    logger.info("Running selection...")
    db = SessionLocal()
    try:
        # Get raw, non-duplicate images that have been scored
        images = db.query(ImageRecord).filter(
            ImageRecord.status == "raw",
            ImageRecord.is_duplicate == False,
            ImageRecord.overall_score > threshold
        ).order_by(ImageRecord.overall_score.desc()).all()
        
        selected_count = 0
        for img_record in images:
            source_path = img_record.original_path
            dest_path = os.path.join("1 Selected Pics", img_record.filename)
            
            # Copy file
            shutil.copy2(source_path, dest_path)
            
            # Update DB
            img_record.status = "selected"
            img_record.is_selected = True
            selected_count += 1
            
            logger.info(f"Selected {img_record.filename} with score {img_record.overall_score:.2f}")
            
        db.commit()
        logger.info(f"Selection complete. {selected_count} images moved to '1 Selected Pics'.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error during selection: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_selection()
