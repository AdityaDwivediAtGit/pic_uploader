import os
import json
import shutil
import zipfile
import logging
from src.core.database import SessionLocal, ImageRecord

logger = logging.getLogger(__name__)

def export_approved_images():
    """
    Exports all approved images with their metadata and captions into a final zip archive.
    """
    logger.info("Running export for approved images...")
    db = SessionLocal()
    try:
        images = db.query(ImageRecord).filter(ImageRecord.status == "approved").all()
        if not images:
            logger.info("No approved images to export.")
            return

        export_folder = os.path.join("7 Final Export", "latest_export")
        os.makedirs(export_folder, exist_ok=True)
        
        metadata_list = []
        
        for img in images:
            # Source is ideally the text added pic, fallback to enhanced, fallback to selected
            text_path = os.path.join("3 Text Added Pics", img.filename)
            enhanced_path = os.path.join("2 Enhanced Pics", img.filename)
            selected_path = os.path.join("1 Selected Pics", img.filename)
            
            source = None
            if os.path.exists(text_path): source = text_path
            elif os.path.exists(enhanced_path): source = enhanced_path
            elif os.path.exists(selected_path): source = selected_path
            
            if source:
                dest = os.path.join(export_folder, img.filename)
                shutil.copy2(source, dest)
                
                metadata = {
                    "filename": img.filename,
                    "score": img.overall_score,
                    "hashtags": img.hashtags,
                    "song": img.recommended_song,
                    "posting_time": img.posting_time,
                }
                
                try: metadata["captions"] = json.loads(img.captions_json)
                except: metadata["captions"] = []
                
                try: metadata["quotes"] = json.loads(img.quotes_json)
                except: metadata["quotes"] = []
                
                metadata_list.append(metadata)
                
                # Write individual caption txt for easy copy-pasting
                txt_path = os.path.join(export_folder, img.filename.rsplit('.', 1)[0] + ".txt")
                with open(txt_path, 'w', encoding='utf-8') as f:
                    f.write(f"Hashtags: {metadata['hashtags']}\n\n")
                    if metadata["captions"]:
                        f.write(f"Caption: {metadata['captions'][0]}\n")
                        
        # Write master metadata json
        with open(os.path.join(export_folder, "metadata.json"), 'w', encoding='utf-8') as f:
            json.dump(metadata_list, f, indent=4)
            
        # Create ZIP archive
        zip_path = os.path.join("7 Final Export", "export.zip")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(export_folder):
                for file in files:
                    zipf.write(os.path.join(root, file), arcname=file)
                    
        logger.info(f"Successfully exported {len(images)} images to {zip_path}")
    except Exception as e:
        logger.error(f"Error during export: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    export_approved_images()
