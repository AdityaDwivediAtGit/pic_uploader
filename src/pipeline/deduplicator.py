import logging
import imagehash
from PIL import Image
from src.core.database import SessionLocal, ImageRecord

logger = logging.getLogger(__name__)

def run_deduplication():
    """Identifies duplicate and near-duplicate images using perceptual hashing."""
    logger.info("Running deduplication...")
    db = SessionLocal()
    try:
        # Only process images that are marked as 'raw' and not already checked for duplicates
        # For simplicity, we just grab all raw images that aren't marked duplicate
        images = db.query(ImageRecord).filter(
            ImageRecord.status == "raw",
            ImageRecord.is_duplicate == False
        ).all()
        
        hashes = {} # hash -> image_record.id
        duplicate_count = 0
        
        for img_record in images:
            try:
                pil_img = Image.open(img_record.original_path)
                # Compute average hash (fast and good for exact/near matches)
                img_hash = str(imagehash.average_hash(pil_img))
                
                if img_hash in hashes:
                    logger.info(f"Duplicate found: {img_record.filename} is duplicate of image ID {hashes[img_hash]}")
                    img_record.is_duplicate = True
                    duplicate_count += 1
                else:
                    hashes[img_hash] = img_record.id
            except Exception as e:
                logger.error(f"Error hashing {img_record.filename}: {e}")
                
        db.commit()
        logger.info(f"Deduplication complete. Marked {duplicate_count} as duplicates.")
    except Exception as e:
        db.rollback()
        logger.error(f"Error in deduplication: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_deduplication()
