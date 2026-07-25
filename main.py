import os
import json
from fastapi import FastAPI, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.core.folders import init_folders
from src.core.config import get_config
from src.core.database import init_db, get_db, ImageRecord

# Configure logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler(os.path.join("logs", "app.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize application structure
init_folders()
init_db()

# Load config to verify it works
try:
    config = get_config()
    logger.info("Configuration loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load config: {e}")

# FastAPI Setup
app = FastAPI(title="AI Instagram Content Studio")

# Static files (serve generated folders if needed for the UI)
app.mount("/static", StaticFiles(directory="web"), name="static")
app.mount("/raw", StaticFiles(directory="0 Raw Pics"), name="raw")
app.mount("/selected", StaticFiles(directory="1 Selected Pics"), name="selected")
app.mount("/enhanced", StaticFiles(directory="2 Enhanced Pics"), name="enhanced")
app.mount("/text_added", StaticFiles(directory="3 Text Added Pics"), name="text_added")

templates = Jinja2Templates(directory="web/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    # Fetch all selected images for review
    images = db.query(ImageRecord).filter(ImageRecord.status == "selected").all()
    
    # Parse JSON strings back to python objects for the template
    for img in images:
        try:
            img.parsed_captions = json.loads(img.captions_json)
        except:
            img.parsed_captions = []
        try:
            img.parsed_quotes = json.loads(img.quotes_json)
        except:
            img.parsed_quotes = []

    return templates.TemplateResponse(
        request=request, name="index.html", context={"images": images, "title": "AI Studio Dashboard"}
    )

@app.post("/api/images/{image_id}/approve")
async def approve_image(image_id: int, db: Session = Depends(get_db)):
    img = db.query(ImageRecord).filter(ImageRecord.id == image_id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    img.status = "approved"
    db.commit()
    return {"status": "success", "message": "Image approved"}

@app.post("/api/images/{image_id}/reject")
async def reject_image(image_id: int, db: Session = Depends(get_db)):
    img = db.query(ImageRecord).filter(ImageRecord.id == image_id).first()
    if not img:
        raise HTTPException(status_code=404, detail="Image not found")
    img.status = "rejected"
    db.commit()
    return {"status": "success", "message": "Image rejected"}

if __name__ == "__main__":
    import uvicorn
    # Start the application
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
