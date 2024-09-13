# app.py

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from face_swapper import FaceSwapper
import os

app = Flask(__name__)

UPLOAD_FOLDER = '/srv/uploads'  # Directory for uploading files
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the upload directory exists


"""

For Runing model without API

"""
def lip_sync(face_bg_video, translated_audio, padding_input):

    if not face_bg_video or not translated_audio:
        return 'No face video or audio file uploaded.'
    
    try:
        # Convert padding_input to a list of integers
        pads = list(map(int, padding_input.split()))
        
        # Convert padding values to a string with space-separated values
        pads_str = ' '.join(map(str, pads))
    except ValueError:
        return 'Invalid padding input. Must be space-separated integers.'

    face_file  = face_bg_video
    audio_file = translated_audio
    output_filename = 'output_lip_sync.mp4'
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)

    # Save the uploaded files
    if face_file and audio_file:
        face_path = os.path.join(UPLOAD_FOLDER, secure_filename(face_file.filename))
        audio_path = os.path.join(UPLOAD_FOLDER, secure_filename(audio_file.filename))
        face_file.save(face_path)
        audio_file.save(audio_path)

        # Initialize and run the FaceSwapper
        swapper = FaceSwapper(face_path, audio_path, output_path, pads_str)
        try:
            swapper.run()  # Perform the face swapping process
            return  output_path
        except Exception as e:
            return {'error': str(e)}

    return {'error': 'Invalid file type'}



"""

For Runing model with API

"""

@app.route('/lip_sync', methods=['POST'])
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
    app.run(debug=True, host='0.0.0.0', port=5005)  
