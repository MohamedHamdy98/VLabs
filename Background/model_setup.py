import subprocess



def install_dependencies():
    """
    Installs the required dependencies for the project.
    """
    # Install Python packages using pip
    subprocess.run(["pip", "install", "pillow"], check=True)
    subprocess.run(["pip", "install", "ffmpeg-python"], check=True)
    subprocess.run(["pip", "install", "tqdm"], check=True)
    subprocess.run(["pip", "install", "rembg"], check=True)
    subprocess.run(["pip", "install", "flask"], check=True)  
    subprocess.run(["pip", "install", "flask-ngrok"], check=True)
    subprocess.run(["pip", "install", "pyngrok"], check=True)
    subprocess.run(["pip", "install", "opencv-python"], check=True)
    subprocess.run(["pip", "install", "gdown"], check=True)
    
    # Install system package for ffmpeg
    subprocess.run(["apt-get", "install", "-y", "ffmpeg"], check=True)

    print("All dependencies installed successfully.")

