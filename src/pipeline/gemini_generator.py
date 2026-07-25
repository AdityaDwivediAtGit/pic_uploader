import logging
import json
import google.generativeai as genai
from PIL import Image
from src.core.config import get_config
from src.core.database import SessionLocal, ImageRecord

logger = logging.getLogger(__name__)

def setup_gemini():
    config = get_config()
    api_key = config.api.gemini_api_key
    if not api_key or api_key == "YOUR_GEMINI_API_KEY_HERE":
        logger.warning("Gemini API key is missing or invalid in config.yaml.")
        return False
    genai.configure(api_key=api_key)
    return True

def generate_creative_content(image_path: str):
    """
    Uses Gemini API to analyze the image and generate quotes, captions, tags, and song recommendations.
    Returns a dictionary with the results.
    """
    if not setup_gemini():
        return None
        
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        img = Image.open(image_path)
        
        prompt = """
        You are a social media expert and creative agency for Instagram. 
        Look at this image and provide a JSON response with the following keys:
        - "quotes": A list of 3 aesthetic/deep quotes for this image.
        - "captions": A list of 3 Instagram captions (one short, one long, one funny).
        - "hashtags": A string of 10 relevant and trending hashtags (space separated).
        - "song": A recommended song for an Instagram Reel or Story (Artist - Title).
        - "posting_time": The recommended best time to post this.
        
        Return ONLY raw JSON, no markdown formatting blocks.
        """
        
        response = model.generate_content([prompt, img])
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:-3]
            
        return json.loads(text)
    except Exception as e:
        logger.error(f"Error generating content for {image_path}: {e}")
        return None

def run_gemini_generation():
    logger.info("Running Gemini creative generation...")
    db = SessionLocal()
    try:
        # Generate content for selected images that don't have captions yet
        images = db.query(ImageRecord).filter(
            ImageRecord.status == "selected",
            ImageRecord.captions_json == "[]"
        ).all()
        
        for img_record in images:
            logger.info(f"Generating content for {img_record.filename}...")
            content = generate_creative_content(img_record.original_path)
            if content:
                img_record.quotes_json = json.dumps(content.get("quotes", []))
                img_record.captions_json = json.dumps(content.get("captions", []))
                img_record.hashtags = content.get("hashtags", "")
                img_record.recommended_song = content.get("song", "")
                img_record.posting_time = content.get("posting_time", "")
                
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Error in Gemini generation: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_gemini_generation()
