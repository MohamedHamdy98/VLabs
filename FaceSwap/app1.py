import requests
from flask import Flask, request, jsonify
import os
import json
from werkzeug.utils import secure_filename
import logging

app = Flask(__name__)

# Directories for server-stored files
VIDEOS_DIR = '/content/srv/videos'
BACKGROUNDS_DIR = '/content/srv/backgrounds'
UPLOAD_FOLDER = '/content/srv/uploads'
METADATA_FILE = '/content/srv/uploads/metadata.json'

# Configure logging
LOG_FILE = '/content/srv/logs/app1.log'
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Make sure directories exist
os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(BACKGROUNDS_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(METADATA_FILE), exist_ok=True)

# Allowed extensions for files
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp3', 'wav', 'mp4'}

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_metadata(data):
    if not os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'w') as f:
            json.dump([], f)  # Initialize empty list in file

    with open(METADATA_FILE, 'r+') as f:
        metadata = json.load(f)
        metadata.append(data)
        f.seek(0)
        json.dump(metadata, f, indent=4)
    logging.info(f"Metadata saved: {data}")

def get_ngrok_url(port):
    """Retrieve the current ngrok public URL for a given port."""
    ngrok_api_url = f'http://localhost:4040/api/tunnels'
    try:
        response = requests.get(ngrok_api_url)
        tunnels = response.json().get('tunnels', [])
        for tunnel in tunnels:
            if tunnel['config']['addr'].endswith(f':{port}'):
                return tunnel['public_url']
    except Exception as e:
        logging.error(f"Error retrieving ngrok URL: {e}")
    return None

@app.route('/upload', methods=['POST'])
def upload():
    image_file = request.files.get('image')
    text_data = request.form.get('text')
    audio_file = request.files.get('audio')
    chosen_video = request.form.get('chosen_video')
    chosen_background = request.form.get('chosen_background')

    if not image_file or not text_data or not audio_file or not chosen_video or not chosen_background:
        logging.error('All inputs (image, text, audio, video, and background) are required.')
        return jsonify({'error': 'All inputs (image, text, audio, video, and background) are required.'}), 400

    if image_file and allowed_file(image_file.filename):
        image_filename = secure_filename(image_file.filename)
        image_path = os.path.join(UPLOAD_FOLDER, image_filename)
        image_file.save(image_path)
        logging.info(f"Image file saved: {image_path}")
    else:
        logging.error('Invalid image file.')
        return jsonify({'error': 'Invalid image file.'}), 400

    if audio_file and allowed_file(audio_file.filename):
        audio_filename = secure_filename(audio_file.filename)
        audio_path = os.path.join(UPLOAD_FOLDER, audio_filename)
        audio_file.save(audio_path)
        logging.info(f"Audio file saved: {audio_path}")
    else:
        logging.error('Invalid audio file.')
        return jsonify({'error': 'Invalid audio file.'}), 400

    chosen_video_path = os.path.join(VIDEOS_DIR, chosen_video)
    chosen_background_path = os.path.join(BACKGROUNDS_DIR, chosen_background)

    if not os.path.exists(chosen_video_path):
        logging.error(f'Chosen video {chosen_video} does not exist on server.')
        return jsonify({'error': f'Chosen video {chosen_video} does not exist on server.'}), 400

    if not os.path.exists(chosen_background_path):
        logging.error(f'Chosen background {chosen_background} does not exist on server.')
        return jsonify({'error': f'Chosen background {chosen_background} does not exist on server.'}), 400

    data = {
        'image_path': image_path,
        'text_data': text_data,
        'audio_path': audio_path,
        'chosen_video_path': chosen_video_path,
        'chosen_background_path': chosen_background_path
    }
    save_metadata(data)

    # Get the ngrok URL for app2
    app2_url = get_ngrok_url(5001)
    if not app2_url:
        return jsonify({"error": "Unable to retrieve ngrok URL for App 2."}), 500

    try:
        response = requests.post(f"{app2_url}/swap", json={'data': data})
        response_data = response.json()
        return jsonify(response_data), response.status_code
    except Exception as e:
        logging.error(f"Failed to contact second Flask app: {e}")
        return jsonify({"error": "Failed to contact second Flask app."}), 500

@app.route('/get_uploaded_data', methods=['GET'])
def get_uploaded_data():
    if not os.path.exists(METADATA_FILE):
        logging.error('No metadata found.')
        return jsonify({'error': 'No metadata found.'}), 404

    with open(METADATA_FILE, 'r') as f:
        metadata = json.load(f)
    logging.info('Metadata retrieved successfully.')
    return jsonify(metadata), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)