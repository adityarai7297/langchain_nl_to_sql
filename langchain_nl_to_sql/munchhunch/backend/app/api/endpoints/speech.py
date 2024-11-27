from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.speech_utils import transcribe_audio, save_audio_file
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/speech-to-text/")
async def speech_to_text(audio: UploadFile = File(...)):
    """
    Convert speech to text using OpenAI Whisper
    """
    # Check file format
    if not audio.filename.lower().endswith(('.wav', '.mp3', '.m4a', '.mp4', '.mpeg', '.mpga', '.m4a', '.ogg', '.webm')):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a supported audio format."
        )
    
    try:
        # Read and save the audio file
        contents = await audio.read()
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")
            
        temp_file_path = save_audio_file(contents)
        logger.info(f"Saved audio file to: {temp_file_path}")
        
        # Transcribe the audio
        text = transcribe_audio(temp_file_path)
        if not text:
            raise HTTPException(status_code=500, detail="Failed to transcribe audio")
        
        # Cleanup
        import os
        os.remove(temp_file_path)
        
        return {"text": text}
        
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))