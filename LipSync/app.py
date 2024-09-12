# app.py

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from face_swapper import FaceSwapper
import os

app = Flask(__name__)

UPLOAD_FOLDER = '/srv/uploads'  # Directory for uploading files
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the upload directory exists

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Endpoint to handle file uploads and initiate face swapping.

    :return: JSON response with status and output file path.
    """
    # Check for required files and form data
    if 'face' not in request.files or 'audio' not in request.files:
        return jsonify({'error': 'No face or audio file uploaded'}), 400

    face_file = request.files['face']
    audio_file = request.files['audio']
    pads = request.form.get('pads', '0 10 0 0')  # Default padding values
    output_filename = 'output.mp4'
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)

    # Save the uploaded files
    if face_file and audio_file:
        face_path = os.path.join(UPLOAD_FOLDER, secure_filename(face_file.filename))
        audio_path = os.path.join(UPLOAD_FOLDER, secure_filename(audio_file.filename))
        face_file.save(face_path)
        audio_file.save(audio_path)

        # Initialize and run the FaceSwapper
        swapper = FaceSwapper(face_path, audio_path, output_path, list(map(int, pads.split())))
        try:
            swapper.run()  # Perform the face swapping process
            return jsonify({'message': 'Processing complete', 'output': output_path}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file type'}), 400

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5)  
