# setup.py

import os
import subprocess

def setup_environment():
    # Check CUDA availability
    print('Checking CUDA availability...')
    subprocess.run(['nvidia-smi'], check=True)
    
    # Install system dependencies
    print('Installing system dependencies...')
    subprocess.run(['apt-get', 'update'], check=True)  # Update package lists
    subprocess.run(['apt', 'install', 'ffmpeg', '-y'], check=True)  # Install FFmpeg

    # Clone the project repository and install Python requirements
    print('Cloning project and installing requirements...')
    subprocess.run(['git', 'clone', 'https://github.com/vinthony/video-retalking.git'], check=True)  # Clone repo
    os.chdir('video-retalking')  # Change directory to the cloned repo
    subprocess.run(['pip', 'install', '-r', 'requirements.txt'], check=True)  # Install dependencies

    # Download pre-trained models
    print('Downloading pre-trained models...')
    os.makedirs('./checkpoints', exist_ok=True)  # Create directory for models
    model_urls = [
        ('https://github.com/vinthony/video-retalking/releases/download/v0.0.1/30_net_gen.pth', './checkpoints/30_net_gen.pth'),
        # Add more URLs here for other models...
    ]
    for url, path in model_urls:
        subprocess.run(['wget', url, '-O', path], check=True)  # Download each model file
    subprocess.run(['unzip', '-d', './checkpoints/BFM', './checkpoints/BFM.zip'], check=True)  # Unzip model files

if __name__ == '__main__':
    setup_environment()  # Run the setup function when this script is executed
