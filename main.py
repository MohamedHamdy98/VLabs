from flask import Flask, request, jsonify
import requests
import uuid
import logging
import os

# Get the script name without the .py extension
script_name = os.path.splitext(os.path.basename(__file__))[0]

# Define the log file path based on the script name
LOG_FILE = os.path.join('/srv/logs', f'{script_name}.log')

# Ensure the log directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Define URLs for individual APIs
FACE_SWAP_API = "http://localhost:5001/swap"
TRANSLATION_API = "http://localhost:5002/translate"
BACKGROUND_API = "http://localhost:5003/change_background"
LIP_SYNC_API = "http://localhost:5004/lip_sync"

USER_INPUT_API = requests.get("http://localhost:5005/get_uploaded_data")

if USER_INPUT_API.status_code == 200:
    uploaded_data = USER_INPUT_API.json()
    for data in uploaded_data:
        IMAGE_PATH = data.get('image_path', 'Not available')
        AUDIO_PATH = data.get('audio_path', 'Not available')
        CHOSEN_VIDEO_PATH = data.get('chosen_video_path', 'Not available')
        CHOSEN_BACKGROUND_PATH = data.get('chosen_background_path', 'Not available')
        logging.info(f"Image Path: {IMAGE_PATH}, Audio Path: {AUDIO_PATH}, "
                     f"Chosen Video Path: {CHOSEN_VIDEO_PATH}, Chosen Background Path: {CHOSEN_BACKGROUND_PATH}")
else:
    print("Error retrieving uploaded data.")

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

    # Step 1: Face Swap
    face_swap_response = requests.post(FACE_SWAP_API, files={'image': open(image, 'rb'), 'video': open(video, 'rb')})
    if face_swap_response.status_code != 200:
        return jsonify({'error': 'Face swap failed'}), 500
    face_swap_result = face_swap_response.json().get('output_video')

    # Step 2: Translation
    translation_response = requests.post(TRANSLATION_API, json={'text': text, 'audio': open(audio, 'rb')})
    if translation_response.status_code != 200:
        return jsonify({'error': 'Translation failed'}), 500
    translation_result = translation_response.json().get('translated_audio')

    # Step 3: Change Background
    background_response = requests.post(BACKGROUND_API, files={'background': open(background, 'rb'), 'face_swap_video': open(face_swap_result, 'rb')})
    if background_response.status_code != 200:
        return jsonify({'error': 'Background change failed'}), 500
    background_result = background_response.json().get('output_video')

    # Step 4: Lip Sync
    lip_sync_response = requests.post(LIP_SYNC_API, files={'background_video': open(background_result, 'rb'), 'translated_audio': open(translation_result, 'rb')})
    if lip_sync_response.status_code != 200:
        return jsonify({'error': 'Lip sync failed'}), 500
    lip_sync_result = lip_sync_response.json().get('output_video')

    return jsonify({'final_output': lip_sync_result}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
