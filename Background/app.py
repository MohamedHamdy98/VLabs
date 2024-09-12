import cv2
import os
from rembg import remove
from tqdm import tqdm
import numpy as np
import gdown
from flask import Flask, request, jsonify, send_file
from clear_dir import clear_directory
from model_setup import install_dependencies

app = Flask(__name__)

# Setup environment
install_dependencies()

# Define paths
OUTPUT_FRAMES_DIR = '/content/output_frames'
OUTPUT_VIDEO_PATH = '/content/output_video.mp4'
PROCESSING_COMPLETE_FLAG = '/content/processing_complete.txt'

# Helper function to download file from Google Drive
def download_from_google_drive(url, output_path):
    file_id = url.split("/d/")[1].split("/view")[0]
    download_url = f"https://drive.google.com/uc?id={file_id}"
    gdown.download(download_url, output_path, quiet=False)

# Endpoint to process video
@app.route('/process_video', methods=['POST'])
def process_video():
    # Ensure output directory is clean
    clear_directory([OUTPUT_FRAMES_DIR])
    os.makedirs(OUTPUT_FRAMES_DIR, exist_ok=True)

    # Fetch Google Drive URLs from request
    video_url = request.form.get('video_url')
    background_url = request.form.get('background_url')

    if not video_url or not background_url:
        return jsonify({'error': 'Both video URL and background URL are required.'}), 400

    input_video_path = os.path.join('/content', 'input_video.mp4')
    new_background_path = os.path.join('/content', 'new_background.jpg')

    # Download video and background from Google Drive
    download_from_google_drive(video_url, input_video_path)
    download_from_google_drive(background_url, new_background_path)

    # Step 1: Extract frames from the video
    cap = cv2.VideoCapture(input_video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Check if the video was opened successfully
    if not cap.isOpened():
        return jsonify({'error': f'Could not open video {input_video_path}'}), 400

    # Step 2: Read new background and resize it to match the video frame dimensions
    new_background = cv2.imread(new_background_path)

    if new_background is None:
        return jsonify({'error': f'Could not load background image {new_background_path}'}), 400

    new_background_resized = cv2.resize(new_background, (frame_width, frame_height))

    # Step 3: Process frames
    for i in tqdm(range(frame_count), desc="Processing frames"):
        ret, frame = cap.read()
        if not ret:
            break

        # Remove background using rembg
        try:
            result = remove(frame)
        except Exception as e:
            print(f"Error removing background from frame {i}: {e}")
            continue

        # Convert result to RGBA if not already
        if result.shape[-1] != 4:
            result = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)

        # Create a copy of the result to avoid modifying read-only data
        result_copy = np.copy(result)

        # Overlay the new background using alpha channel
        alpha_channel = result_copy[:, :, 3] / 255.0
        for c in range(0, 3):
            result_copy[:, :, c] = result_copy[:, :, c] * alpha_channel + new_background_resized[:, :, c] * (1 - alpha_channel)

        # Remove alpha channel and save the processed frame
        frame_output_path = os.path.join(OUTPUT_FRAMES_DIR, f'{i:04d}.png')
        cv2.imwrite(frame_output_path, result_copy[:, :, :3])

    # Release video capture object
    cap.release()

    # Step 4: Reassemble frames into a new video
    frame_files = sorted([f for f in os.listdir(OUTPUT_FRAMES_DIR) if f.endswith('.png')])

    # Initialize VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 'mp4v' for MP4 format
    video_writer = cv2.VideoWriter(OUTPUT_VIDEO_PATH, fourcc, fps, (frame_width, frame_height))

    # Write frames to video with tqdm progress bar
    for frame_file in tqdm(frame_files, desc="Reassembling Video"):
        frame_path = os.path.join(OUTPUT_FRAMES_DIR, frame_file)
        frame = cv2.imread(frame_path)
        video_writer.write(frame)

    # Release the video writer object
    video_writer.release()

    # Create a flag file to indicate processing is complete
    with open(PROCESSING_COMPLETE_FLAG, 'w') as f:
        f.write('Processing complete')

    return jsonify({'message': 'Video processing started. Check the status for completion.'}), 202


# Endpoint to check processing status and get the video
@app.route('/status', methods=['GET'])
def status():
    if os.path.exists(PROCESSING_COMPLETE_FLAG):
        return send_file(OUTPUT_VIDEO_PATH, as_attachment=True, mimetype='video/mp4', download_name='output_video.mp4')
    else:
        return jsonify({'message': 'Processing is still in progress. Please wait.'}), 202


if __name__ == "__main__":
    # Run the Flask application
    app.run(host='0.0.0.0', port=5000)