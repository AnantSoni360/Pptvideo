import os
import requests
import json
import time
from typing import Optional

class DIDAvatar:
    """Class to handle D-ID API integration for creating talking avatars"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize D-ID API client"""
        self.api_key = api_key or os.getenv('DID_API_KEY')
        if not self.api_key:
            raise ValueError("D-ID API key is required. Set it via constructor or DID_API_KEY environment variable.")
        
        self.base_url = "https://api.d-id.com"
        self.headers = {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_talking_avatar(self, text: str, output_path: str, avatar_id: str = "anna_costume1") -> str:
        """Create a talking avatar video using D-ID API"""
        try:
            # Prepare the request payload
            payload = {
                "script": {
                    "type": "text",
                    "input": text,
                    "subtitles": False,
                    "provider": {
                        "type": "microsoft",
                        "voice_id": "en-US-JennyNeural",
                        "voice_config": {
                            "style": "chat",
                            "rate": 1.0,
                            "pitch": 0
                        }
                    }
                },
                "config": {
                    "fluent": True,
                    "pad_audio": 0
                },
                "source_url": f"https://create-images-results.d-id.com/DefaultPresenters/{avatar_id}/image.jpg"
            }
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/talks",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            # Get the talk ID from response
            talk_id = response.json()["id"]
            
            # Wait for the video to be ready
            video_url = self._wait_for_video(talk_id)
            
            # Download the video
            self._download_video(video_url, output_path)
            
            return output_path
            
        except Exception as e:
            print(f"Error in D-ID API: {str(e)}")
            raise
    
    def _wait_for_video(self, talk_id: str, timeout: int = 60) -> str:
        """Wait for the video to be ready and return its URL"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            response = requests.get(
                f"{self.base_url}/talks/{talk_id}",
                headers=self.headers
            )
            response.raise_for_status()
            
            status = response.json()["status"]
            if status == "done":
                return response.json()["result_url"]
            elif status == "error":
                raise Exception(f"Error creating video: {response.json().get('error', 'Unknown error')}")
            
            time.sleep(1)
        
        raise TimeoutError("Timeout waiting for video creation")
    
    def _download_video(self, url: str, output_path: str):
        """Download the video from URL to the specified path"""
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk) 