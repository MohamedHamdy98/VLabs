# main.py

from flask import Flask, request, jsonify
import requests
import logging

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# API endpoints
FACE_SWAP_API = "http://localhost:5001/swap"
TRANSLATION_API = "http://localhost:5002/translate"
BACKGROUND_API = "http://localhost:5003/change_background"
LIP_SYNC_API = "http://localhost:5004/lip_sync"

@app.route('/process', methods=['POST'])
def process_request():
    """
    Orchestrate the workflow for processing user input.
    Expects a JSON payload with the following fields:
    - image: Path to input image file.
    - video: Path to input video file.
    - text: Text input for translation.
    - audio: Path to input audio file.
    - background: Path to background image.
    """

    data = request.json

    # Extract user inputs
    image = data.get('image')
    video = data.get('video')
    text = data.get('text')
    audio = data.get('audio')
    background = data.get('background')

    if not (image and video and text and audio and background):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # Step 1: Face Swap
        face_swap_response = requests.post(FACE_SWAP_API, json={'image': image, 'video': video})
        face_swap_response.raise_for_status()  # Raise exception for HTTP errors
        face_swap_result = face_swap_response.json().get('output_path_video_faceswap')

        # Step 2: Translation
        translation_response = requests.post(TRANSLATION_API, json={'text': text, 'audio': audio})
        translation_response.raise_for_status()  # Raise exception for HTTP errors
        translation_result = translation_response.json().get('output_audio_translated')

        # Step 3: Change Background
        background_response = requests.post(BACKGROUND_API, json={'background': background, 'face_swap_video': face_swap_result})
        background_response.raise_for_status()  # Raise exception for HTTP errors
        background_result = background_response.json().get('output_path_video_background')

        # Step 4: Lip Sync
        lip_sync_response = requests.post(LIP_SYNC_API, json={'background_video': background_result, 'translated_audio': translation_result})
        lip_sync_response.raise_for_status()  # Raise exception for HTTP errors
        lip_sync_result = lip_sync_response.json().get('output_path_video_lipSync')

        return jsonify({'final_output': lip_sync_result}), 200

    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return jsonify({'error': 'An error occurred during processing'}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
