# model_setup.py

import os
import subprocess
from tqdm import tqdm 


# Helper function to check if a package is installed
def is_package_installed(package_name):
    try:
        subprocess.run(["pip", "show", package_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError:
        return False
    
def setup_environment():
    # Clone the repository
    subprocess.run(["git", "clone", "https://github.com/s0md3v/roop.git"], check=True)
    os.chdir("roop")

    ROOP_DIR = os.chdir("roop")
    MODEL_PATH = os.path.join(ROOP_DIR, "models/inswapper_128.onnx")

    # Install requirements
    subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
    # Check if the model has already been downloaded
    if not os.path.exists(MODEL_PATH):
        print("Model not found. Downloading inswapper_128.onnx...")
        with tqdm(total=100, desc="Downloading model") as pbar:
            subprocess.run(["wget", "https://huggingface.co/ezioruan/inswapper_128.onnx/resolve/main/inswapper_128.onnx", "-O", "inswapper_128.onnx"])
            pbar.update(100)  # Assume the download is 100% when completed
        os.makedirs("models", exist_ok=True)
        subprocess.run(["mv", "inswapper_128.onnx", "./models/"])
    else:
        print("Model is already downloaded.")

    # Check if onnxruntime-gpu is installed
    if is_package_installed("onnxruntime-gpu"):
        print("onnxruntime-gpu is already installed.")
    else:
        print("Installing onnxruntime-gpu...")
        with tqdm(total=100, desc="Installing onnxruntime-gpu") as pbar:
            subprocess.run(["pip", "install", "onnxruntime-gpu"])
            pbar.update(100)

    # Check if torch, torchvision, and torchaudio are installed
    if is_package_installed("torch") and is_package_installed("torchvision") and is_package_installed("torchaudio"):
        print("Torch packages are already installed.")
    else:
        print("Installing torch, torchvision, and torchaudio...")
        with tqdm(total=100, desc="Installing PyTorch") as pbar:
            subprocess.run(["pip", "uninstall", "onnxruntime", "onnxruntime-gpu", "-y"])
            subprocess.run(["pip", "install", "torch", "torchvision", "torchaudio", "--force-reinstall", "--index-url", "https://download.pytorch.org/whl/cu118"])
            pbar.update(100)       