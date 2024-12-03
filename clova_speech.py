import os
import requests
import json
import time
from typing import Optional

class ClovaSpeech:
    """CLOVA Speech API wrapper"""
    
    def __init__(self):
        """Initialize with environment variables"""
        self.base_url = "https://clovaspeech-gw.ncloud.com"
        self.secret_key = os.getenv("CLOVA_SECRET_KEY")
        
        if not self.secret_key:
            raise ValueError("CLOVA_SECRET_KEY must be set in environment variables")
    
    def request_transcription(self, audio_file, language="ko-KR", completion_timeout=100) -> Optional[str]:
        """
        Request speech-to-text transcription from CLOVA Speech
        
        Args:
            audio_file: File object or path to audio file
            language: Language code (default: ko-KR)
            completion_timeout: Timeout in seconds for completion check (default: 100)
            
        Returns:
            Transcribed text if successful, None otherwise
        """
        headers = {
            "X-CLOVASPEECH-API-KEY": self.secret_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        # Prepare request body
        request_body = {
            "language": language,
            "completion": "sync",
            "callback": None,
            "userdata": None,
            "wordAlignment": True,
            "fullText": True,
            "script": {
                "context": None,
                "contextSize": 0,
                "customVocab": None,
            }
        }
        
        # Send request
        files = {
            'media': ('media', audio_file, 'application/octet-stream'),
            'params': (None, json.dumps(request_body, ensure_ascii=False).encode('UTF-8'), 'application/json')
        }
        
        response = requests.post(
            f"{self.base_url}/speech/v1/recognition/upload",
            headers={"X-CLOVASPEECH-API-KEY": self.secret_key},
            files=files
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'segments' in result:
                return ' '.join(segment['text'] for segment in result['segments'])
            return result.get('text')
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
        
        return None

    def transcribe_file(self, file_path: str) -> Optional[str]:
        """
        Transcribe an audio file from file path
        
        Args:
            file_path: Path to audio file
            
        Returns:
            Transcribed text if successful, None otherwise
        """
        try:
            with open(file_path, 'rb') as audio_file:
                return self.request_transcription(audio_file)
        except Exception as e:
            print(f"Error transcribing file: {e}")
            return None
