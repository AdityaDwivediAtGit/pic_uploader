import os
import logging
from PIL import Image, ImageEnhance
import cv2
import numpy as np
from src.core.database import SessionLocal, ImageRecord

logger = logging.getLogger(__name__)

def enhance_image(source_path: str, dest_path: str):
    """
    Applies basic auto-enhancement to make it look like a DSLR shot.
    - Slight contrast boost
    - Slight color saturation boost
    - Very mild sharpening
    """
    try:
        # Load image with Pillow for color enhancements
        img = Image.open(source_path)
        
        # Contrast
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.1)
        
        # Color (Saturation)
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.15)
        
        # Convert to OpenCV for sharpening
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        # Unsharp mask for subtle sharpening
        gaussian = cv2.GaussianBlur(img_cv, (0, 0), 2.0)
        sharpened = cv2.addWeighted(img_cv, 1.5, gaussian, -0.5, 0)
        
        # Save enhanced image
        cv2.imwrite(dest_path, sharpened)
        return True
    except Exception as e:
        logger.error(f"Failed to enhance {source_path}: {e}")
        return False

def run_enhancement():
    logger.info("Running auto-enhancements...")
    db = SessionLocal()
    try:
        # Get selected images that haven't been enhanced yet (status = selected)
        # We will keep status as selected, but check if the enhanced file exists
        images = db.query(ImageRecord).filter(ImageRecord.status == "selected").all()
        
        enhanced_count = 0
        for img_record in images:
            source = os.path.join("1 Selected Pics", img_record.filename)
            dest = os.path.join("2 Enhanced Pics", img_record.filename)
            
            if not os.path.exists(dest) and os.path.exists(source):
                logger.info(f"Enhancing {img_record.filename}...")
                success = enhance_image(source, dest)
                if success:
                    enhanced_count += 1
                    
        logger.info(f"Enhanced {enhanced_count} images.")
    except Exception as e:
        logger.error(f"Error in enhancement: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_enhancement()
