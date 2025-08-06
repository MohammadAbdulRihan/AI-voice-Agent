import os
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import shutil
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# --- THIS IS THE DAY 1 CODE YOU NEED TO ADD BACK ---

app = FastAPI()

# This tells the server where to find your 'static' files (like script.js)
app.mount("/static", StaticFiles(directory="static"), name="static")

# This sets up the template engine to find your HTML files
templates = Jinja2Templates(directory="templates")

# This is the route that serves your HTML page
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Simple endpoint to prevent 404 errors from old cached requests
@app.get("/api/hello")
async def hello():
    return {"message": "TTS API is running", "status": "success"}

# Favicon endpoint to prevent 404 errors
@app.get("/favicon.ico")
async def favicon():
    return {"message": "No favicon configured"}

# --- END OF DAY 1 CODE ---


# --- THIS IS YOUR DAY 2/3 API ENDPOINT CODE (IT'S ALREADY GOOD) ---

# The Pydantic model for the incoming JSON
class TextRequest(BaseModel):
    text: str

MURF_API_KEY = os.getenv("MURF_API_KEY")
MURF_TTS_URL = "https://api.murf.ai/v1/speech/generate-with-key"

@app.post("/generate-audio")
def generate_audio(request: TextRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    headers = {
        "api-key": MURF_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "voiceId": "en-US-marcus",
        "text": request.text,
        "format": "mp3"
    }

    try:
        response = requests.post(MURF_TTS_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Murf TTS API call failed: {e}")

    audio_url = data.get("audioFile")

    if not audio_url:
        raise HTTPException(status_code=500, detail=f"Audio URL not found in Murf API response: {data}")

    return {"audio_url": audio_url}

# --- AUDIO UPLOAD ENDPOINT ---

# Create uploads directory if it doesn't exist
UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

@app.post("/upload-audio")
async def upload_audio(audio_file: UploadFile = File(...)):
    """
    Upload endpoint that receives audio files from the echo bot,
    saves them temporarily, and returns file information.
    """
    try:
        # Validate file type (basic check)
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Generate a unique filename
        import uuid
        file_extension = ".webm"  # Default for our recorder
        if audio_file.filename:
            file_extension = Path(audio_file.filename).suffix or ".webm"
        
        unique_filename = f"recording_{uuid.uuid4().hex[:8]}{file_extension}"
        file_path = UPLOADS_DIR / unique_filename
        
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
        
        # Get file size
        file_size = file_path.stat().st_size
        
        return {
            "status": "success",
            "message": "Audio file uploaded successfully",
            "filename": unique_filename,
            "content_type": audio_file.content_type,
            "size_bytes": file_size,
            "size_kb": round(file_size / 1024, 2),
            "upload_path": str(file_path)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# --- END OF UPLOAD ENDPOINT ---

# --- FILE MANAGEMENT ENDPOINTS ---

@app.get("/list-uploads")
async def list_uploads():
    """
    List all uploaded audio files with their details
    """
    try:
        files = []
        for file_path in UPLOADS_DIR.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "filename": file_path.name,
                    "size_bytes": stat.st_size,
                    "size_kb": round(stat.st_size / 1024, 2),
                    "upload_time": stat.st_mtime,
                    "file_path": str(file_path)
                })
        
        # Sort by upload time (newest first)
        files.sort(key=lambda x: x["upload_time"], reverse=True)
        
        return {
            "status": "success",
            "total_files": len(files),
            "files": files
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download a specific uploaded audio file
    """
    from fastapi.responses import FileResponse
    
    file_path = UPLOADS_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type='audio/webm'
    )

# --- END OF FILE MANAGEMENT ENDPOINTS ---

# --- WEB INTERFACE FOR UPLOADED FILES ---

@app.get("/files", response_class=HTMLResponse)
async def view_files(request: Request):
    """
    Web interface to view and play uploaded audio files
    """
    return templates.TemplateResponse("files.html", {"request": request})

# --- END OF WEB INTERFACE ---