import streamlit as st
import os
import tempfile
from utils import process_presentation
import time
import re
from avatar_generator import create_avatar_video

# Set page config
st.set_page_config(
    page_title="PPT to Video Converter",
    page_icon="🎥",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 3em;
        margin-top: 1em;
    }
    .success-message {
        padding: 1em;
        border-radius: 0.5em;
        background-color: #d4edda;
        color: #155724;
        margin: 1em 0;
    }
    .error-message {
        padding: 1em;
        border-radius: 0.5em;
        background-color: #f8d7da;
        color: #721c24;
        margin: 1em 0;
    }
    .progress-container {
        margin: 1em 0;
        padding: 1em;
        border-radius: 0.5em;
        background-color: #f8f9fa;
    }
    .progress-text {
        font-size: 1.1em;
        margin-bottom: 0.5em;
    }
    </style>
""", unsafe_allow_html=True)

def extract_progress(text):
    """Extract progress percentage from the processing output"""
    match = re.search(r'Processing slide \d+/\d+ \((\d+\.\d+)%\)', text)
    if match:
        return float(match.group(1))
    return 0

def main():
    st.title("🎥 PowerPoint to Video Converter")
    st.write("Transform your presentations into engaging video explanations with an AI avatar")
    
    # Sidebar for additional information
    with st.sidebar:
        st.header("About")
        st.write("""
        This tool converts PowerPoint presentations into engaging videos with:
        - AI-powered slide explanations
        - Professional voice-over
        - High-quality video output
        - Custom styling options
        """)
        
        st.header("Instructions")
        st.write("""
        1. Upload your PowerPoint file
        2. Configure video settings
        3. Click 'Generate Video'
        4. Wait for processing
        5. Download your video
        """)
        
        # GPT Configuration
        st.header("AI Explanation Settings")
        use_gpt = st.checkbox("Use GPT for detailed slide explanations", value=False)
        
        if use_gpt:
            gpt_api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                help="Enter your OpenAI API key for GPT-powered explanations"
            )
        
        # D-ID Avatar Settings
        st.header("Avatar Settings")
        use_did = st.checkbox("Use D-ID for realistic talking avatars", value=False)
        
        if use_did:
            did_api_key = st.text_input(
                "D-ID API Key",
                type="password",
                help="Enter your D-ID API key for realistic talking avatars"
            )
            
            avatar_style = st.selectbox(
                "Avatar Style",
                ["Professional", "Casual", "Educational"],
                help="Choose the avatar's appearance and behavior",
                key="did_avatar_style"
            )
        else:
            did_api_key = None
            avatar_style = st.selectbox(
                "Avatar Style",
                ["Professional", "Casual", "Educational"],
                help="Choose the avatar's appearance and behavior",
                key="simple_avatar_style"
            )
        
        # Voice settings
        st.header("Voice Settings")
        voice_type = st.selectbox(
            "Voice Type",
            ["Female", "Male"],
            help="Select the narrator's voice",
            key="voice_type"
        )
        
        speech_rate = st.slider(
            "Speech Rate",
            0.5, 2.0, 1.0,
            help="Adjust the speed of the voice"
        )
        
        speech_pitch = st.slider(
            "Speech Pitch",
            -50, 50, 0,
            help="Adjust the pitch of the voice"
        )
    
    # Main content
    uploaded_file = st.file_uploader("Upload your PowerPoint presentation", type=['pptx'])
    
    if uploaded_file is not None:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pptx') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            ppt_path = tmp_file.name
        
        # Video settings
        st.subheader("Video Settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            video_quality = st.selectbox(
                "Video Quality",
                ["720p", "1080p"],
                help="Select the output video resolution"
            )
            
            avatar_style = st.selectbox(
                "Avatar Style",
                ["Professional", "Casual", "Educational"],
                help="Choose the avatar's appearance and behavior"
            )
        
        with col2:
            language = st.selectbox(
                "Language",
                ["English"],  # Can be expanded in future
                help="Select the narration language"
            )
        
        # Advanced settings expander
        with st.expander("Advanced Settings"):
            transition_effect = st.selectbox(
                "Slide Transition Effect",
                ["Fade", "None"],
                help="Choose how slides transition"
            )
            
            min_slide_duration = st.slider(
                "Minimum Slide Duration (seconds)",
                5, 30, 10,
                help="Minimum time each slide will be shown"
            )
        
        if st.button("Generate Video"):
            if use_gpt and not gpt_api_key:
                st.warning("⚠️ Please enter your OpenAI API key for GPT-powered explanations")
                return
                
            try:
                # Create progress container
                progress_container = st.empty()
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Create output directory
                output_dir = "output"
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                # Process the presentation
                with st.spinner("Processing your presentation... This may take a few minutes."):
                    # Start processing in a separate thread to update progress
                    import threading
                    import queue
                    
                    output_queue = queue.Queue()
                    
                    def process_with_progress():
                        output_files = process_presentation(
                            ppt_path,
                            output_dir,
                            avatar_style.lower(),
                            voice_type.lower(),
                            speech_rate,
                            speech_pitch,
                            use_gpt,
                            gpt_api_key if use_gpt else None,
                            did_api_key if use_did else None
                        )
                        output_queue.put(output_files)
                    
                    # Start processing thread
                    process_thread = threading.Thread(target=process_with_progress)
                    process_thread.start()
                    
                    # Update progress while processing
                    last_progress = 0
                    while process_thread.is_alive():
                        # Get the latest output from the processing
                        try:
                            output = output_queue.get_nowait()
                            if output:
                                progress = extract_progress(str(output))
                                if progress > last_progress:
                                    progress_bar.progress(progress / 100)
                                    status_text.text(f"Processing: {progress:.1f}% complete")
                                    last_progress = progress
                        except queue.Empty:
                            pass
                        time.sleep(0.1)
                    
                    # Get final result
                    output_files = output_queue.get()
                    
                    if output_files:
                        final_video = output_files[-1]  # Get the last processed video
                        
                        # Update progress to 100%
                        progress_bar.progress(1.0)
                        status_text.text("Processing completed!")
                        
                        # Success message
                        st.markdown(
                            '<div class="success-message">✅ Video generated successfully!</div>',
                            unsafe_allow_html=True
                        )
                        
                        # Provide download button
                        with open(final_video, "rb") as file:
                            st.download_button(
                                label="Download Video",
                                data=file,
                                file_name="presentation_video.mp4",
                                mime="video/mp4"
                            )
                        
                        # Preview section
                        st.subheader("Video Preview")
                        st.video(final_video)
                        
                        # Create avatar video if D-ID key is provided
                        if did_api_key:
                            with st.spinner("Creating avatar video..."):
                                avatar_path = create_avatar_video(
                                    text="Your presentation is ready!",
                                    output_path=os.path.join(os.path.dirname(final_video), "avatar.mp4"),
                                    avatar_style=avatar_style,
                                    did_api_key=did_api_key
                                )
                                st.video(avatar_path)
                    
            except Exception as e:
                st.markdown(
                    f'<div class="error-message">❌ Error: {str(e)}</div>',
                    unsafe_allow_html=True
                )
            
            finally:
                # Cleanup with retry
                max_retries = 3
                retry_delay = 1  # seconds
                
                for i in range(max_retries):
                    try:
                        if os.path.exists(ppt_path):
                            os.remove(ppt_path)
                        break
                    except Exception as e:
                        if i < max_retries - 1:
                            time.sleep(retry_delay)
                        else:
                            print(f"Warning: Could not delete temporary file {ppt_path}: {str(e)}")

if __name__ == "__main__":
    main() 