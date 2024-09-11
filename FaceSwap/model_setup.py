# model_setup.py

import os
import subprocess

def setup_environment():
    # Clone the repository
    subprocess.run(["git", "clone", "https://github.com/s0md3v/roop.git"], check=True)
    os.chdir("roop")

    # Install requirements
    subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)

    # Download and move model
    subprocess.run(["wget", "https://huggingface.co/ezioruan/inswapper_128.onnx/resolve/main/inswapper_128.onnx", "-O", "inswapper_128.onnx"], check=True)
    os.makedirs("models", exist_ok=True)
    subprocess.run(["mv", "inswapper_128.onnx", "./models"], check=True)

    # Reinstall PyTorch and ONNX Runtime
    subprocess.run(["pip", "uninstall", "onnxruntime", "onnxruntime-gpu", "-y"], check=True)
    subprocess.run(["pip", "install", "torch", "torchvision", "torchaudio", "--force-reinstall", "--index-url", "https://download.pytorch.org/whl/cu118"], check=True)
    subprocess.run(["pip", "install", "onnxruntime-gpu"], check=True)
