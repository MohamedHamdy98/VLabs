import os
import sys
# Add the root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from APIs.ChangeBackground.model_setup import setup_environment
setup_environment()

import shutil
import cv2
import numpy as np
from rembg import remove
from tqdm import tqdm
import gdown
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS


app = Flask(__name__)
CORS(app=app)  # Enable Cross-Origin Resource Sharing (CORS) for the Flask app

# Define paths for output frames, video, and processing status
OUTPUT_FRAMES_DIR = '/tmp/change_bg/output_frames'
OUTPUT_VIDEO_PATH = '/tmp/change_bg/output_video.mp4'
PROCESSING_COMPLETE_FLAG = '/tmp/change_bg/processing_complete.txt'

# Helper function to clear directories
def clear_directories(paths):
    """
    Clears all files and subdirectories in the given list of directory paths.

    Args:
        paths (list): List of directory paths to clear.

    Returns:
        None
    """
    for path in paths:
        if os.path.exists(path):
            for file_name in os.listdir(path):
                file_path = os.path.join(path, file_name)
                try:
                    # Delete files or directories
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')
            print(f"Directory {path} cleared successfully.")
        else:
            print(f"Directory {path} does not exist.")

# Helper function to download a file from Google Drive
def download_from_google_drive(url, output_path):
    """
    Downloads a file from Google Drive using its URL and saves it to the specified output path.

    Args:
        url (str): Google Drive URL of the file to be downloaded.
        output_path (str): Local path where the downloaded file will be saved.

    Raises:
        Exception: If the file download fails.
    """
    try:
        file_id = url.split("/d/")[1].split("/view")[0]
        download_url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(download_url, output_path, quiet=False)
        print(f"File downloaded successfully to {output_path}")
    except Exception as e:
        print(f"Failed to download file from {url}. Error: {str(e)}")

# Endpoint to process video
@app.route('/change_background', methods=['POST'])
def change_background():
    """
    Endpoint to start the background change process for a video.

    Expects form data with the following fields:
        - video_url (str): Google Drive link to the input video.
        - background_url (str): Google Drive link to the new background image.

    Returns:
        JSON response indicating the status of the processing and instructions for checking completion.

    Raises:
        Exception: If an error occurs during processing.
    """
    try:
        # Clear and create the output frames directory
        clear_directories([OUTPUT_FRAMES_DIR])
        os.makedirs(OUTPUT_FRAMES_DIR, exist_ok=True)

        # Retrieve URLs from the request
        video_url = request.form.get('video_url')
        background_url = request.form.get('background_url')

        # Check if URLs are provided
        if not video_url or not background_url:
            return jsonify({'error': 'Both video URL and background URL are required.'}), 400

        # Define paths for the downloaded files
        input_video_path = os.path.join('/content', 'input_video.mp4')
        new_background_path = os.path.join('/content', 'new_background.jpg')

        # Download files from Google Drive
        download_from_google_drive(video_url, input_video_path)
        download_from_google_drive(background_url, new_background_path)

        # Open the input video
        cap = cv2.VideoCapture(input_video_path)
        if not cap.isOpened():
            return jsonify({'error': f'Could not open video {input_video_path}'}), 400

        # Retrieve video properties
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Load and resize the new background
        new_background = cv2.imread(new_background_path)
        if new_background is None:
            return jsonify({'error': f'Could not load background image {new_background_path}'}), 400
        new_background_resized = cv2.resize(new_background, (frame_width, frame_height))

        # Process each frame
        for i in tqdm(range(frame_count), desc="Processing frames"):
            ret, frame = cap.read()
            if not ret:
                break

            try:
                result = remove(frame)
            except Exception as e:
                print(f"Error removing background from frame {i}: {e}")
                continue

            # Ensure result has an alpha channel
            if result.shape[-1] != 4:
                result = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)

            # Composite the result with the new background
            alpha_channel = result[:, :, 3] / 255.0
            for c in range(0, 3):
                result[:, :, c] = result[:, :, c] * alpha_channel + new_background_resized[:, :, c] * (1 - alpha_channel)

            # Save processed frame
            frame_output_path = os.path.join(OUTPUT_FRAMES_DIR, f'{i:04d}.png')
            cv2.imwrite(frame_output_path, result[:, :, :3])

        cap.release()

        # Reassemble the frames into a video
        frame_files = sorted([f for f in os.listdir(OUTPUT_FRAMES_DIR) if f.endswith('.png')])
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(OUTPUT_VIDEO_PATH, fourcc, fps, (frame_width, frame_height))

        for frame_file in tqdm(frame_files, desc="Reassembling Video"):
            frame_path = os.path.join(OUTPUT_FRAMES_DIR, frame_file)
            frame = cv2.imread(frame_path)
            video_writer.write(frame)

        video_writer.release()

        # Create a flag file to indicate processing completion
        with open(PROCESSING_COMPLETE_FLAG, 'w') as f:
            f.write('Processing complete')

        return jsonify({'message': 'Video processing started. Check the status for completion.'}), 202

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_path_change_bg', methods=['GET'])
def get_path_change_bg():
    """
    Endpoint to retrieve the path of the output video from the background change operation.

    Returns:
        JSON response with the status and path to the output video, if it exists.

    Raises:
        Exception: If there is an error retrieving the file path.
    """
    try:
        # Path to the output video from the background change
        OUTPUT_VIDEO_PATH = '/tmp/change_bg/output_video.mp4'

        # Check if the output file exists
        if os.path.exists(OUTPUT_VIDEO_PATH):
            return jsonify({
                'status': 'success',
                'message': 'Output file path retrieved successfully',
                'output_path': OUTPUT_VIDEO_PATH
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Output file not found'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

@app.route('/get_video_output_bg', methods=['GET'])
def get_video_output_bg():
    """
    Endpoint to check processing status and get the video output if processing is complete.

    Returns:
        A video file if processing is complete, otherwise a message indicating that processing is still in progress.
    """
    if os.path.exists(PROCESSING_COMPLETE_FLAG):
        return send_file(OUTPUT_VIDEO_PATH, as_attachment=True, mimetype='video/mp4', download_name='output_video.mp4')
    else:
        return jsonify({'message': 'Processing is still in progress. Please wait.'}), 202

if __name__ == "__main__":
    app.run()  # Start the Flask application
