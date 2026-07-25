import os
import json
import logging
from PIL import Image, ImageDraw, ImageFont
from src.core.database import SessionLocal, ImageRecord

logger = logging.getLogger(__name__)

def add_text_to_image(source_path: str, dest_path: str, text: str):
    """
    Adds aesthetic text over the image for Stories.
    """
    try:
        img = Image.open(source_path).convert("RGBA")
        
        # Create a dark gradient overlay for text readability
        overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        height = img.size[1]
        width = img.size[0]
        
        # Add a subtle dark gradient at the bottom
        for y in range(int(height * 0.6), height):
            alpha = int(((y - (height * 0.6)) / (height * 0.4)) * 200)
            draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
            
        img = Image.alpha_composite(img, overlay)
        img = img.convert("RGB")
        
        # Draw text
        draw = ImageDraw.Draw(img)
        
        # Fallback font size based on image height
        font_size = int(height * 0.05)
        try:
            # Try to load a nice font if available on the system
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
            
        # Draw text at the bottom center
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        x = (width - text_width) / 2
        y = height - (height * 0.15)
        
        # White text with slight shadow
        draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0))
        draw.text((x, y), text, font=font, fill=(255, 255, 255))
        
        img.save(dest_path)
        return True
    except Exception as e:
        logger.error(f"Failed to add text to {source_path}: {e}")
        return False

def run_story_generation():
    logger.info("Generating story images with text...")
    db = SessionLocal()
    try:
        images = db.query(ImageRecord).filter(ImageRecord.status == "selected").all()
        
        count = 0
        for img_record in images:
            # We use the enhanced picture if available, else selected
            enhanced_path = os.path.join("2 Enhanced Pics", img_record.filename)
            selected_path = os.path.join("1 Selected Pics", img_record.filename)
            source = enhanced_path if os.path.exists(enhanced_path) else selected_path
            
            dest = os.path.join("3 Text Added Pics", img_record.filename)
            
            if not os.path.exists(dest) and os.path.exists(source):
                try:
                    quotes = json.loads(img_record.quotes_json)
                    text = quotes[0] if quotes else "Aesthetic Vibes"
                except:
                    text = "Aesthetic Vibes"
                    
                logger.info(f"Adding text to {img_record.filename}...")
                if add_text_to_image(source, dest, text):
                    count += 1
                    
        logger.info(f"Generated text overlays for {count} images.")
    except Exception as e:
        logger.error(f"Error in story generation: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_story_generation()
