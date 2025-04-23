import os
import requests
import json
from typing import Optional
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip, ColorClip

def create_avatar_video(
    text: str,
    output_path: str,
    avatar_style: str = "default",
    did_api_key: Optional[str] = None
) -> str:
    """
    Create an avatar video using D-ID API or fallback to a simple avatar.
    
    Args:
        text: The text to be spoken by the avatar
        output_path: Path where the video will be saved
        avatar_style: Style of the avatar (default, professional, casual)
        did_api_key: D-ID API key for creating AI avatars
        
    Returns:
        str: Path to the generated video
    """
    if did_api_key:
        try:
            # D-ID API endpoint
            url = "https://api.d-id.com/talks"
            
            # Configure the avatar based on style
            avatar_config = {
                "default": {
                    "source_url": "https://create-images-results.d-id.com/DefaultPresenters/Emma_f/image.jpg",
                    "voice": "en-US-JennyNeural"
                },
                "professional": {
                    "source_url": "https://create-images-results.d-id.com/DefaultPresenters/John_f/image.jpg",
                    "voice": "en-US-GuyNeural"
                },
                "casual": {
                    "source_url": "https://create-images-results.d-id.com/DefaultPresenters/Sarah_f/image.jpg",
                    "voice": "en-US-AriaNeural"
                }
            }.get(avatar_style, avatar_config["default"])
            
            # Prepare the request payload
            payload = {
                "script": {
                    "type": "text",
                    "input": text
                },
                "source_url": avatar_config["source_url"],
                "voice": avatar_config["voice"]
            }
            
            # Make the API request
            headers = {
                "Authorization": f"Basic {did_api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            # Get the video URL from the response
            result = response.json()
            video_url = result["result_url"]
            
            # Download the video
            video_response = requests.get(video_url)
            video_response.raise_for_status()
            
            # Save the video
            with open(output_path, "wb") as f:
                f.write(video_response.content)
                
            return output_path
            
        except Exception as e:
            print(f"Error creating D-ID avatar: {str(e)}")
            # Fall back to simple avatar
            return _create_simple_avatar(text, output_path, avatar_style)
    else:
        # Create simple avatar if no API key is provided
        return _create_simple_avatar(text, output_path, avatar_style)

def _create_simple_avatar(text: str, output_path: str, avatar_style: str) -> str:
    """
    Create a simple avatar video with text overlay.
    
    Args:
        text: The text to display
        output_path: Path where the video will be saved
        avatar_style: Style of the avatar (default, professional, casual)
        
    Returns:
        str: Path to the generated video
    """
    # Style configurations
    styles = {
        "default": {
            "bg_color": (41, 128, 185),  # Blue
            "text_color": "white",
            "font_size": 40
        },
        "professional": {
            "bg_color": (44, 62, 80),  # Dark blue
            "text_color": "white",
            "font_size": 36
        },
        "casual": {
            "bg_color": (46, 204, 113),  # Green
            "text_color": "white",
            "font_size": 44
        }
    }
    
    style = styles.get(avatar_style, styles["default"])
    
    # Create background
    duration = 5  # seconds
    bg_clip = ColorClip(size=(640, 480), color=style["bg_color"])
    bg_clip = bg_clip.set_duration(duration)
    
    # Create text clip
    text_clip = TextClip(
        text,
        fontsize=style["font_size"],
        color=style["text_color"],
        font="Arial-Bold",
        size=(600, None),
        method="caption"
    ).set_duration(duration)
    
    # Center the text
    text_clip = text_clip.set_position("center")
    
    # Combine clips
    final_clip = CompositeVideoClip([bg_clip, text_clip])
    
    # Write the video file
    final_clip.write_videofile(output_path, fps=24)
    
    return output_path 