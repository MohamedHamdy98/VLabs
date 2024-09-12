import os
import subprocess

def setup_environment():
    """
    Set up the environment by cloning the repository, installing dependencies,
    and downloading necessary files.
    """
    # Clone the repository
    subprocess.run(["git", "clone", "-b", "dev", "https://github.com/camenduru/xtts2-hf.git"], check=True)
    
    # Change to the repository directory
    os.chdir("xtts2-hf")

    # Install core requirements
    subprocess.run(["pip", "install", "--ignore-installed", "blinker"], check=True)
    subprocess.run(["pip", "install", "-q", "TTS==0.21.1", "langid", "unidic-lite", "unidic", "deepspeed"], check=True)
    subprocess.run(["pip", "install", "-q", "numpy<2.0.0", "-U"], check=True)

    # Download required files
    subprocess.run(["wget", "https://huggingface.co/spaces/coqui/xtts/resolve/main/examples/female.wav", "-O", "examples/female.wav"], check=True)
    subprocess.run(["wget", "https://huggingface.co/spaces/coqui/xtts/resolve/main/examples/male.wav", "-O", "examples/male.wav"], check=True)
    subprocess.run(["wget", "https://huggingface.co/spaces/coqui/xtts/resolve/main/ffmpeg.zip", "-O", "ffmpeg.zip"], check=True)

    # Install additional packages
    subprocess.run(["pip", "install", "SpeechRecognition", "googletrans", "deep-translator", "langid"], check=True)
    subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
    subprocess.run(["pip", "install", "flask-ngrok", "pyngrok"], check=True)

    # Extract ffmpeg if needed
    subprocess.run(["unzip", "ffmpeg.zip"], check=True)

    print("Environment setup complete.")


