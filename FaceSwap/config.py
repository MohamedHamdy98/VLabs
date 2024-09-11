# config.py

import logging
import os
import uuid
import tempfile
from UserInputs.user_inputs_data import IMAGE_PATH, CHOSEN_VIDEO_PATH

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure directory exists
output_dir = "/srv/faceSwapOutputsVideos/"
os.makedirs(output_dir, exist_ok=True)

# for keep the files in server
unique_id = str(uuid.uuid4())
output_path = os.path.join(output_dir, f"output_{unique_id}.mp4")

# for temporary files that auto cleaned up
"""with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4", dir="/srv/faceSwapOutputsVideos") as temp_file:
    output_path = temp_file.name
    logger.info(f"Temporary file created: {output_path}")"""


TARGET_PATH = CHOSEN_VIDEO_PATH
SOURCE_PATH = IMAGE_PATH
OUTPUT_PATH = output_path
MODEL_PATH = "./models/inswapper_128.onnx"



# For cleaning Files by Time
"""
import os
import time

def cleanup_temp_files(directory="/kaggle/working", age_limit_seconds=3600):
    current_time = time.time()
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_age = current_time - os.path.getmtime(file_path)
            if file_age > age_limit_seconds:
                os.remove(file_path)
                print(f"Deleted old file: {file_path}")

# Example usage
cleanup_temp_files("/kaggle/working", 3600)  # Clean up files older than 1 hour

"""