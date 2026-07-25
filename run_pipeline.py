import logging
from src.core.folders import init_folders
from src.core.database import init_db
from src.pipeline.scanner import scan_raw_pics
from src.pipeline.deduplicator import run_deduplication
from src.pipeline.analyzer import run_analysis
from src.pipeline.selector import run_selection
from src.pipeline.enhancer import run_enhancement
from src.pipeline.gemini_generator import run_gemini_generation
from src.pipeline.story_generator import run_story_generation
from src.pipeline.exporter import export_approved_images

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def main():
    logger.info("Initializing Studio...")
    init_folders()
    init_db()
    
    logger.info("--- Starting Pipeline ---")
    
    # 1. Scan for new images
    scan_raw_pics()
    
    # 2. Deduplicate
    run_deduplication()
    
    # 3. Analyze quality
    run_analysis()
    
    # 4. Select best images
    run_selection(threshold=10.0) # Adjust threshold as needed
    
    # 5. Auto enhance
    run_enhancement()
    
    # 6. Generate quotes, captions, tags (Requires Gemini API key)
    run_gemini_generation()
    
    # 7. Generate story text overlays
    run_story_generation()
    
    # Note: exporter is usually run AFTER user approves images in the web UI.
    # You can call export_approved_images() manually or add a button in the UI.
    # export_approved_images()
    
    logger.info("--- Pipeline Completed ---")
    logger.info("Start the web dashboard with: python main.py")

if __name__ == "__main__":
    main()
