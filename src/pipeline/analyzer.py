import logging
import cv2
import numpy as np
from src.core.database import SessionLocal, ImageRecord

logger = logging.getLogger(__name__)

def analyze_image_quality(image_path: str):
    """
    Returns a dictionary of quality metrics for an image using OpenCV.
    - sharpness (variance of laplacian)
    - brightness
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            return None
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Sharpness
        sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Brightness (average pixel intensity)
        brightness = np.mean(gray)
        
        # Very basic composition score based on sharpness and optimal brightness (around 120-140)
        brightness_score = 100 - abs(brightness - 130)
        # Normalize sharpness a bit (just a heuristic for this example)
        sharpness_score = min(sharpness / 10.0, 100.0) 
        
        overall = (brightness_score * 0.4) + (sharpness_score * 0.6)
        
        return {
            "sharpness": sharpness,
            "brightness": brightness,
            "overall_score": overall
        }
    except Exception as e:
        logger.error(f"Failed to analyze {image_path}: {e}")
        return None

def run_analysis():
    logger.info("Running image analysis...")
    db = SessionLocal()
    try:
        # Process non-duplicate raw images that haven't been scored
        images = db.query(ImageRecord).filter(
            ImageRecord.status == "raw",
            ImageRecord.is_duplicate == False,
            ImageRecord.overall_score == 0.0
        ).all()
        
        for img_record in images:
            metrics = analyze_image_quality(img_record.original_path)
            if metrics:
                img_record.composition_score = metrics.get("brightness", 0)
                img_record.overall_score = metrics.get("overall_score", 0)
                logger.info(f"Analyzed {img_record.filename}: Score={img_record.overall_score:.2f}")
                
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error in analysis: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_analysis()
