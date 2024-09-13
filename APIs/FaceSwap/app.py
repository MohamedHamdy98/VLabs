from flask import Flask, request, jsonify
import os
import subprocess
import gdown
from flask_cors import CORS
from tqdm import tqdm  # Import tqdm for progress tracking
from APIs.FaceSwap.model_setup import setup_environment

app = Flask(__name__)
CORS(app)

# Directory for the Roop model and the face swapper
ROOP_DIR = os.chdir("roop")  # Change the directory to where your Roop files are located

# Setup the Roop environment and dependencies
setup_environment()

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
        # Extract the file ID from the Google Drive URL
        file_id = url.split("/d/")[1].split("/view")[0]
        download_url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(download_url, output_path, quiet=False)
        print(f"File downloaded successfully to {output_path}")
    except Exception as e:
        print(f"Failed to download file from {url}. Error: {str(e)}")

@app.route('/face_swap', methods=['POST'])
def face_swap():
    """
    Endpoint for performing face swapping using provided Google Drive links for the target video and source image.

    Expects form data with the following fields:
        - target_url (str): Google Drive link to the target video.
        - source_url (str): Google Drive link to the source image.

    Returns:
        JSON response with the status of the face swapping operation and the path to the output file.

    Raises:
        Exception: If the face swapping process fails.
    """
    try:
        # Change to the Roop directory
        os.chdir(ROOP_DIR)

        # Retrieve URLs from the request
        target_url = request.form.get('target_url')  # Google Drive link for the target video
        source_url = request.form.get('source_url')  # Google Drive link for the source image
        output_path = '/tmp/uploaded_data/outputs/output_face_swap.mp4'  # Default output path

        # Define paths to save the downloaded files
        target_path = "/tmp/uploaded_data/videos/target_video.mp4"
        source_path = "/tmp/uploaded_data/images/source_image.jpg"

        # Ensure directories exist
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        os.makedirs(os.path.dirname(source_path), exist_ok=True)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Download the files from Google Drive with progress reporting
        print("Downloading target video...")
        download_from_google_drive(target_url, target_path)
        print("Downloading source image...")
        download_from_google_drive(source_url, source_path)

        # Prepare and run the face swapping command
        print("Performing face swapping...")
        command = f"python run.py --target {target_path} --source {source_path} -o {output_path} --execution-provider cuda --frame-processor face_swapper"
        
        # Mock progress bar since subprocess is blocking
        with tqdm(total=100, desc="Face swapping") as pbar:
            process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            pbar.update(100)

        # Check if subprocess ran successfully
        if process.returncode != 0:
            raise Exception(f"Face swapping failed: {process.stderr.decode('utf-8')}")

        return jsonify({
            'status': 'success',
            'message': 'Face swapping completed',
            'output_path': output_path
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

    finally:
        # Optionally clean up the temporary files after the process
        if os.path.exists(target_path):
            os.remove(target_path)
        if os.path.exists(source_path):
            os.remove(source_path)

@app.route('/get_path_face_swap', methods=['GET'])
def get_path_face_swap():
    """
    Endpoint to retrieve the path of the output file from the face swap operation.

    Returns:
        JSON response with the status and the path to the output file, if it exists.

    Raises:
        Exception: If there is an error retrieving the file path.
    """
    try:
        # Path to the output video from the face swap
        output_path = '/tmp/uploaded_data/outputs/output_face_swap.mp4'

        # Check if the output file exists
        if os.path.exists(output_path):
            return jsonify({
                'status': 'success',
                'message': 'Output file path retrieved successfully',
                'output_path': output_path
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

# Test route to verify the API is working
@app.route('/')
def index():
    """
    Test route to check if the API is running.

    Returns:
        A simple message indicating the API is operational.
    """
    return "Roop Face Swapping API is running!"

if __name__ == "__main__":
    app.run()  
