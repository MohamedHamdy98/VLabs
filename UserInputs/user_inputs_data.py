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
        return metadata
    except FileNotFoundError:
        logging.error("Metadata file not found.")
        return []
    except json.JSONDecodeError:
        logging.error("Error decoding JSON from metadata file.")
        return []

# Example usage of uploaded data paths
uploaded_data = get_uploaded_data()
for data in uploaded_data:
    image_path = data.get('image_path', 'Not available')
    audio_path = data.get('audio_path', 'Not available')
    chosen_video_path = data.get('chosen_video_path', 'Not available')
    chosen_background_path = data.get('chosen_background_path', 'Not available')
    logging.info(f"Image Path: {image_path}")
    logging.info(f"Audio Path: {audio_path}")
    logging.info(f"Chosen Video Path: {chosen_video_path}")
    logging.info(f"Chosen Background Path: {chosen_background_path}")


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
