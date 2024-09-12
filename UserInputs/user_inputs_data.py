import json
import logging
import os

# Get the script name without the .py extension
script_name = os.path.splitext(os.path.basename(__file__))[0]

# Define the log file path based on the script name
LOG_FILE = os.path.join('/srv/logs', f'{script_name}.log')

# Ensure the log directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

METADATA_FILE = '/srv/uploads/metadata.json'

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_uploaded_data():
    try:
        with open(METADATA_FILE, 'r') as f:
            metadata = json.load(f)
        logging.info(f"Successfully loaded {len(metadata)} entries from metadata.")
        return metadata
    except FileNotFoundError:
        logging.error(f"Metadata file not found at {METADATA_FILE}.")
        return []
    except json.JSONDecodeError:
        logging.error("Error decoding JSON from metadata file.")
        return []
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return []

# Example usage of uploaded data paths
uploaded_data = get_uploaded_data()
if uploaded_data:
    for data in uploaded_data:
        IMAGE_PATH = data.get('image_path', 'Not available')
        TEXT_SCRIPT = data.get('text_data', 'Not available')
        AUDIO_PATH = data.get('audio_path', 'Not available')
        CHOSEN_VIDEO_PATH = data.get('chosen_video_path', 'Not available')
        CHOSEN_BACKGROUND_PATH = data.get('chosen_background_path', 'Not available')
        logging.info(f"Image Path: {IMAGE_PATH}, Audio Path: {AUDIO_PATH}, "
                     f"Chosen Video Path: {CHOSEN_VIDEO_PATH}, Chosen Background Path: {CHOSEN_BACKGROUND_PATH}")
else:
    logging.info("No uploaded data available.")


"""

Alternatively, you could use the 

                 /get_uploaded_data

API endpoint to fetch uploaded data dynamically from another script

"""

import requests

response = requests.get('http://<your-server-ip>:<port>/get_uploaded_data')

if response.status_code == 200:
    uploaded_data = response.json()
    for data in uploaded_data:
        print(f"Image Path: {data['image_path']}")
        print(f"Audio Path: {data['audio_path']}")
        print(f"Chosen Video Path: {data['chosen_video_path']}")
        print(f"Chosen Background Path: {data['chosen_background_path']}")
else:
    print("Error retrieving uploaded data.")
