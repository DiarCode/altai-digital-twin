import httpx
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class STTService:
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.url = "https://api.elevenlabs.io/v1/speech-to-text"

    async def transcribe(self, file_content: bytes, filename: str = "audio.wav") -> str:
        if not self.api_key:
            logger.warning("ELEVENLABS_API_KEY is not set. Skipping transcription.")
            return ""

        headers = {
            "xi-api-key": self.api_key
        }
        
        data = {
            "model_id": "scribe_v1",
            # "tag_audio_events": "true", # Optional
            # "diarize": "true" # Optional
        }

        files = {
            "file": (filename, file_content, "audio/wav") # Adjust mime type if needed, but wav/mp3 usually works
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.url, headers=headers, data=data, files=files, timeout=60.0)
                response.raise_for_status()
                result = response.json()
                return result.get("text", "")
            except httpx.HTTPStatusError as e:
                logger.error(f"ElevenLabs STT Error: {e.response.text}")
                return ""
            except Exception as e:
                logger.error(f"Failed to transcribe audio: {str(e)}")
                return ""

stt_service = STTService()
