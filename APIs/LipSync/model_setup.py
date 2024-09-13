import subprocess
import os
import sys

def is_package_installed(package_name):
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False

def install_package(package_name):
    subprocess.run([sys.executable, "-m", "pip", "install", package_name], check=True)

def setup_environment():
    # Check if required packages are installed, and install if necessary
    packages = ["flask", "gdown"]
    for package in packages:
        if not is_package_installed(package):
            print(f"{package} not found. Installing...")
            install_package(package)
        else:
            print(f"{package} is already installed.")

    # Clone the repository
    subprocess.run(["git", "clone", "https://github.com/vinthony/video-retalking.git"], check=True)
    os.chdir("video-retalking")  # Change to the video-retalking directory

    # Install necessary packages
    subprocess.run([sys.executable, "-m", "pip", "install", "flask", "gdown"], check=True)
    subprocess.run(["apt-get", "update"], check=True)
    subprocess.run(["apt", "install", "ffmpeg", "-y"], check=True)

    # Install the dependencies for video-retalking
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)

    # Create checkpoints directory
    subprocess.run(["mkdir", "-p", "./checkpoints"], check=True)

    # Download pre-trained models
    urls = [
        ("https://github.com/vinthony/video-retalking/releases/download/v0.0.1/30_net_gen.pth", "./checkpoints/30_net_gen.pth"),
        ("https://github.com/vinthony/video-retalking/releases/download/v0.0.1/BFM.zip", "./checkpoints/BFM.zip"),
        ("https://github.com/vinthony/video-retalking/releases/download/v0.0.1/DNet.pt", "./checkpoints/DNet.pt"),
        ("https://github.com/vinthony/video-retalking/releases/download/v0.0.1/ENet.pth", "./checkpoints/ENet.pth"),
        ("https://github.com/vinthony/video-retalking/releases/download/v0.0.1/expression.mat", "./checkpoints/expression.mat"),
        ("https://github.com/vinthony/video-retalking/releases/download/v0.0.1/face3d_pretrain_epoch_20.pth", "./checkpoints/face3d_pretrain_epoch_20.pth"),
        ("https://github.com/vinthony/video-retalking/releases/download/v0.0.1/GFPGANv1.3.pth", "./checkpoints/GFPGANv1.3.pth"),
        ("https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth", "./checkpoints/GFPGANv1.4.pth"),
        ("https://carimage-1253226081.cos.ap-beijing.myqcloud.com/gpen/GPEN-BFR-1024.pth", "./checkpoints/GPEN-BFR-1024.pth"),
        ("https://github.com/vinthony/video-retalking/releases/download/v0.0.1/GPEN-BFR-512.pth", "./checkpoints/GPEN-BFR-512.pth"),
        ("https://github.com/vinthony/video-retalking/releases/download/v0.0.1/LNet.pth", "./checkpoints/LNet.pth"),
        ("https://github.com/vinthony/video-retalking/releases/download/v0.0.1/ParseNet-latest.pth", "./checkpoints/ParseNet-latest.pth"),
        ("https://github.com/vinthony/video-retalking/releases/download/v0.0.1/RetinaFace-R50.pth", "./checkpoints/RetinaFace-R50.pth"),
        ("https://github.com/vinthony/video-retalking/releases/download/v0.0.1/shape_predictor_68_face_landmarks.dat", "./checkpoints/shape_predictor_68_face_landmarks.dat"),
    ]

    for url, output in urls:
        subprocess.run(["wget", url, "-O", output], check=True)

    # Unzip BFM.zip
    subprocess.run(["unzip", "-d", "./checkpoints/BFM", "./checkpoints/BFM.zip"], check=True)

