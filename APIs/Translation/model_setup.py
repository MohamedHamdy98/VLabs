# Setup script for Roop and dependencies

import os
import subprocess

def setup_environment():
    # Clone the repository
    os.chdir("/content")
    subprocess.run(["git", "clone", "-b", "dev", "https://github.com/camenduru/xtts2-hf"], check=True)
    
    os.chdir("/content/xtts2-hf")
    
    # Install required packages
    subprocess.run(["pip", "install", "--ignore-installed", "blinker"], check=True)
    subprocess.run(["pip", "install", "-q", "TTS==0.21.1", "langid", "unidic-lite", "unidic", "deepspeed"], check=True)
    subprocess.run(["pip", "install", "-q", '"numpy<2.0.0"', "-U"], check=True)
    
    # Download required files
    subprocess.run(["wget", "https://huggingface.co/spaces/coqui/xtts/resolve/main/examples/female.wav", "-O", "/content/xtts2-hf/examples/female.wav"], check=True)
    subprocess.run(["wget", "https://huggingface.co/spaces/coqui/xtts/resolve/main/examples/male.wav", "-O", "/content/xtts2-hf/examples/male.wav"], check=True)
    subprocess.run(["wget", "https://huggingface.co/spaces/coqui/xtts/resolve/main/ffmpeg.zip", "-O", "/content/xtts2-hf/ffmpeg.zip"], check=True)
    
    # Install additional packages
    subprocess.run(["pip", "install", "SpeechRecognition"], check=True)
    subprocess.run(["pip", "install", "googletrans"], check=True)
    subprocess.run(["pip", "install", "deep-translator"], check=True)
    subprocess.run(["pip", "install", "langid"], check=True)
    subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
    subprocess.run(["pip", "install", "flask-ngrok"], check=True)
    subprocess.run(["pip", "install", "pyngrok"], check=True)

