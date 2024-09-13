# app.py

from flask import Flask, request, jsonify
from face_swapper import FaceSwapper
from config import TARGET_PATH, SOURCE_PATH, OUTPUT_PATH, MODEL_PATH
import model_setup
import os
import json
from werkzeug.utils import secure_filename
import logging
import gdown

app = Flask(__name__)

# Get the script name without the .py extension
script_name = os.path.splitext(os.path.basename(__file__))[0]

# Define the log file path based on the script name
LOG_FILE = os.path.join('/srv/logs', f'{script_name}.log')

# Ensure the log directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Configure logging
LOG_FILE = '/srv/logs/app.log'
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Setup environment and models
model_setup.setup_environment()

# Initialize face swapper
face_swapper = FaceSwapper(MODEL_PATH, roop_directory="roop")

"""

For Runing model with API

"""
# For User Inputs Data 

# Path to store uploaded file metadata (file paths, etc.)
METADATA_FILE = '/srv/uploads/metadata_faceSwap.json'
# Make sure directories exist
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

# Helper function to download file from Google Drive
def download_from_google_drive(url, output_path):
    file_id = url.split("/d/")[1].split("/view")[0]
    download_url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(download_url, output_path, quiet=False)

# Endpoint to handle uploads and user selections
@app.route('/user_input_data_faceSwap', methods=['POST'])
def upload():
    # Retrieve uploaded files and user selections
    image_file = request.form.get('image_url')
    chosen_video = request.form.get('chosen_video_url')

    # Error handling for missing fields
    if not image_file or not chosen_video :
        logging.error('All inputs (image and video) are required.')
        return jsonify({'error': 'All inputs (image and video) are required.'}), 400

    input_image_path = os.path.join('/srv/input_images', 'input_image.jpg')
    input_video_path = os.path.join('/srv/input_videos', 'input_video.mp4')

    # Download video and background from Google Drive
    download_from_google_drive(image_file, input_image_path)
    download_from_google_drive(chosen_video, input_video_path)

    # Save metadata to JSON
    data = {
        'image_path': input_image_path,
        'chosen_video_path': input_video_path,
    }
    save_metadata(data)

    return jsonify(data), 200


# With API
@app.route('/swap', methods=['POST'])
def swap_faces():
    try:
        # Run face swapping process
        face_swapper.swap_faces(TARGET_PATH, SOURCE_PATH, OUTPUT_PATH)
        return jsonify({"message": "Face swapping completed", "output_path": OUTPUT_PATH}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "Server is running"}), 200



"""

For Runing model without API

"""

# Without API
def run_face_swap_loacl(TARGET_PATH, SOURCE_PATH):
    try:
        face_swapper.swap_faces(TARGET_PATH, SOURCE_PATH, OUTPUT_PATH)
        print({"message": "Face swapping completed", "output_path": OUTPUT_PATH})
        return OUTPUT_PATH
    except Exception as e:
        print('Error at FaceSwap: ' + str(e))




if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False, port=5001)


