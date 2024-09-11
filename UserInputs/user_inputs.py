from flask import Flask, request, jsonify
import os
import json
from werkzeug.utils import secure_filename
import logging

# Get the script name without the .py extension
script_name = os.path.splitext(os.path.basename(__file__))[0]

# Define the log file path based on the script name
LOG_FILE = os.path.join('/srv/logs', f'{script_name}.log')

# Ensure the log directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

app = Flask(__name__)

# Directories for server-stored videos and backgrounds
VIDEOS_DIR = '/srv/videos'  # Adjust based on your server's directory structure
BACKGROUNDS_DIR = '/srv/backgrounds'  # Adjust based on your server's directory structure
UPLOAD_FOLDER = '/srv/uploads'  # Adjust based on your server's directory structure

# Path to store uploaded file metadata (file paths, etc.)
METADATA_FILE = '/srv/uploads/metadata.json'

# Configure logging
LOG_FILE = '/srv/logs/app.log'
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Make sure directories exist
os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(BACKGROUNDS_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(METADATA_FILE), exist_ok=True)

# Allowed extensions for files
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp3', 'wav', 'mp4'}

# Helper function to check if file type is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper function to store file metadata
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

# Endpoint to handle uploads and user selections
@app.route('/upload', methods=['POST'])
def upload():
    # Retrieve uploaded files and user selections
    image_file = request.files.get('image')
    text_data = request.form.get('text')
    audio_file = request.files.get('audio')
    chosen_video = request.form.get('chosen_video')
    chosen_background = request.form.get('chosen_background')

    # Error handling for missing fields
    if not image_file or not text_data or not audio_file or not chosen_video or not chosen_background:
        logging.error('All inputs (image, text, audio, video, and background) are required.')
        return jsonify({'error': 'All inputs (image, text, audio, video, and background) are required.'}), 400

    # Save image and audio files
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

    # Check if chosen video and background exist
    chosen_video_path = os.path.join(VIDEOS_DIR, chosen_video)
    chosen_background_path = os.path.join(BACKGROUNDS_DIR, chosen_background)

    if not os.path.exists(chosen_video_path):
        logging.error(f'Chosen video {chosen_video} does not exist on server.')
        return jsonify({'error': f'Chosen video {chosen_video} does not exist on server.'}), 400

    if not os.path.exists(chosen_background_path):
        logging.error(f'Chosen background {chosen_background} does not exist on server.')
        return jsonify({'error': f'Chosen background {chosen_background} does not exist on server.'}), 400

    # Save metadata to JSON
    data = {
        'image_path': image_path,
        'text_data': text_data,
        'audio_path': audio_path,
        'chosen_video_path': chosen_video_path,
        'chosen_background_path': chosen_background_path
    }
    save_metadata(data)

    return jsonify(data), 200

# New endpoint to retrieve file paths from metadata file
@app.route('/get_uploaded_data', methods=['GET'])
def get_uploaded_data():
    if not os.path.exists(METADATA_FILE):
        logging.error('No metadata found.')
        return jsonify({'error': 'No metadata found.'}), 404

    with open(METADATA_FILE, 'r') as f:
        metadata = json.load(f)
    logging.info('Metadata retrieved successfully.')
    return jsonify(metadata), 200

if __name__ == '__main__':
    app.run(debug=False, port=5000)
