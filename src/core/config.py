import yaml
import os
from pydantic import BaseModel
from typing import List

class TargetAudience(BaseModel):
    age: List[int]
    gender: str

class EditingConfig(BaseModel):
    skin_smoothing: str
    sharpening: str
    crop: str

class CaptionsConfig(BaseModel):
    humour: str
    romance: str
    motivation: str

class SongsConfig(BaseModel):
    language: List[str]

class ApiConfig(BaseModel):
    gemini_api_key: str

class AppConfig(BaseModel):
    target_audience: TargetAudience
    editing: EditingConfig
    captions: CaptionsConfig
    songs: SongsConfig
    api: ApiConfig

def load_config(config_path: str = "config.yaml") -> AppConfig:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
    return AppConfig(**data)

# Global config instance (initialized when needed or at app startup)
config = None

def get_config() -> AppConfig:
    global config
    if config is None:
        config = load_config()
    return config
