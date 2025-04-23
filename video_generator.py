import os
import cv2
import numpy as np
from moviepy.editor import ImageClip, VideoFileClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
from PIL import Image
import tempfile
from avatar_generator import create_avatar_video

class VideoGenerator:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.temp_dir = os.path.join(output_dir, "temp")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Video settings
        self.slide_size = (1920, 1080)
        self.avatar_size = (640, 360)
        self.slide_position = (0, 0)
        self.avatar_position = (self.slide_size[0] - self.avatar_size[0] - 50, 50)
        
    def create_avatar_video(self, text, duration, output_path, avatar_style="professional", did_api_key=None):
        """Create a video with an avatar speaking the text"""
        return create_avatar_video(text, duration, output_path, avatar_style, did_api_key)
    
    def combine_slide_and_avatar(self, slide_path, avatar_video_path, audio_path, output_path, slide_duration=10):
        """Combine slide, avatar video, and audio into final video"""
        # Load components
        slide_clip = ImageClip(slide_path).set_duration(slide_duration)
        avatar_clip = VideoFileClip(avatar_video_path)
        audio_clip = AudioFileClip(audio_path)
        
        # Resize avatar to be proportional to slide
        avatar_clip = avatar_clip.resize(width=slide_clip.w // 4)  # 1/4 of slide width
        
        # Position avatar in bottom right with padding
        avatar_x = slide_clip.w - avatar_clip.w - 50  # 50px padding from right
        avatar_y = slide_clip.h - avatar_clip.h - 50  # 50px padding from bottom
        avatar_clip = avatar_clip.set_position((avatar_x, avatar_y))
        
        # Composite clips
        final_clip = CompositeVideoClip([slide_clip, avatar_clip])
        final_clip = final_clip.set_audio(audio_clip)
        
        # Write final video
        final_clip.write_videofile(output_path, fps=24)
        return output_path
    
    def process_slides(self, slide_paths, texts, audio_paths, avatar_style="professional", did_api_key=None):
        """Process all slides and create a final video"""
        processed_clips = []
        
        for i, (slide_path, text, audio_path) in enumerate(zip(slide_paths, texts, audio_paths)):
            try:
                # Get audio duration
                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration
                audio_clip.close()
                
                # Create avatar video
                avatar_video_path = os.path.join(self.temp_dir, f"avatar_{i}.mp4")
                self.create_avatar_video(text, duration, avatar_video_path, avatar_style, did_api_key)
                
                # Create final video for this slide
                slide_video_path = os.path.join(self.temp_dir, f"slide_{i}_final.mp4")
                self.combine_slide_and_avatar(
                    slide_path,
                    avatar_video_path,
                    audio_path,
                    slide_video_path,
                    duration
                )
                
                # Add to processed clips
                clip = VideoFileClip(slide_video_path)
                processed_clips.append(clip)
                
            except Exception as e:
                print(f"Error processing slide {i+1}: {str(e)}")
                continue
        
        if not processed_clips:
            raise Exception("No slides were successfully processed")
        
        # Concatenate all clips
        final_clip = concatenate_videoclips(processed_clips)
        
        # Save the final video
        final_video_path = os.path.join(self.output_dir, "final_presentation.mp4")
        final_clip.write_videofile(final_video_path, fps=30, codec='libx264')
        
        # Clean up
        for clip in processed_clips:
            clip.close()
        final_clip.close()
        
        # Clean up temporary files
        try:
            for file in os.listdir(self.temp_dir):
                file_path = os.path.join(self.temp_dir, file)
                if os.path.exists(file_path):
                    os.remove(file_path)
            os.rmdir(self.temp_dir)
        except:
            pass
        
        return final_video_path 