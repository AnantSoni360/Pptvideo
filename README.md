# PowerPoint to Video Converter

A Streamlit application that converts PowerPoint presentations into engaging videos with AI avatars.

## Features

- Convert PowerPoint slides to video
- AI-powered avatar narration
- Multiple avatar styles
- Customizable voice settings
- High-quality video output

## Deployment

### Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```

### Streamlit Cloud Deployment

1. Fork this repository to your GitHub account
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Sign in with your GitHub account
4. Click "New app"
5. Select your forked repository
6. Set the main file path as `app.py`
7. Click "Deploy"

## Environment Variables

The following environment variables can be set in Streamlit Cloud:

- `DID_API_KEY`: Your D-ID API key for AI avatars
- `AZURE_SPEECH_KEY`: Your Azure Speech Service key
- `AZURE_SPEECH_REGION`: Your Azure Speech Service region

## License

MIT License 