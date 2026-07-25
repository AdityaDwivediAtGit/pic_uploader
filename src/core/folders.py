import os
import logging

logger = logging.getLogger(__name__)

# Required project directories based on requirements
REQUIRED_FOLDERS = [
    "0 Raw Pics",
    "1 Selected Pics",
    "2 Enhanced Pics",
    "3 Text Added Pics",
    "4 Captions",
    "5 Stories",
    "6 Metadata",
    "7 Final Export",
    "web",
    "config",
    "logs",
]

def init_folders(base_path: str = "."):
    """Creates all required folders if they don't exist."""
    for folder in REQUIRED_FOLDERS:
        folder_path = os.path.join(base_path, folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            logger.info(f"Created folder: {folder}")
        else:
            logger.debug(f"Folder already exists: {folder}")
