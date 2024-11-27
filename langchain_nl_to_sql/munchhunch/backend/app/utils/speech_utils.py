from typing import Optional
import openai
import tempfile
import os
from pathlib import Path
import logging
from pydub import AudioSegment

logger = logging.getLogger(__name__)

def ensure_valid_audio_format(input_path: str) -> str:
    """
    Validates and converts audio file to ensure compatibility with OpenAI's Whisper.
    Returns path to the validated/converted audio file.
    """
    try:
        # Load the audio file
        audio = AudioSegment.from_file(input_path)
        
        # Convert to WAV with specific parameters known to work with Whisper
        output_path = input_path.rsplit('.', 1)[0] + '_converted.wav'
        
        # Export with specific parameters
        audio.export(
            output_path,
            format='wav',
            parameters=[
                '-ar', '16000',  # Sample rate
                '-ac', '1',      # Mono
                '-bits_per_raw_sample', '16'  # Bit depth
            ]
        )
        
        return output_path
    except Exception as e:
        logger.error(f"Error converting audio format: {e}")
        raise RuntimeError(f"Error converting audio format: {e}")

def transcribe_audio(audio_file_path: str, language: Optional[str] = None) -> str:
    """
    Transcribe audio file to text using OpenAI's Whisper model.
    
    Args:
        audio_file_path (str): Path to the audio file
        language (Optional[str]): Optional language code (e.g., 'en', 'es')
    
    Returns:
        str: Transcribed text
    """
    try:
        if not os.path.exists(audio_file_path):
            raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
        
        # Ensure valid format
        converted_path = ensure_valid_audio_format(audio_file_path)
        
        with open(converted_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=language,
                response_format="text"
            )
        
        # Cleanup converted file if it's different from input
        if converted_path != audio_file_path:
            os.remove(converted_path)
            
        return transcript
        
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        raise
    finally:
        # Ensure cleanup of converted file in case of error
        if 'converted_path' in locals() and converted_path != audio_file_path:
            try:
                os.remove(converted_path)
            except:
                pass

def save_audio_file(audio_data: bytes) -> str:
    """
    Save audio data to a temporary file.
    
    Args:
        audio_data (bytes): Raw audio data
    
    Returns:
        str: Path to the saved audio file
    """
    try:
        # Create a temporary file with .wav extension
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"audio_{os.urandom(8).hex()}.wav")
        
        with open(temp_path, "wb") as temp_file:
            temp_file.write(audio_data)
            
        return temp_path
        
    except Exception as e:
        logger.error(f"Error saving audio file: {e}")
        raise RuntimeError(f"Error saving audio file: {e}")

def cleanup_audio_file(file_path: str) -> None:
    """
    Clean up temporary audio file.
    
    Args:
        file_path (str): Path to the audio file to delete
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error cleaning up audio file: {e}") 