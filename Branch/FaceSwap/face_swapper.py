import onnxruntime as ort
import cv2
import subprocess
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FaceSwapper:
    def __init__(self, model_path, roop_directory='roop'):
        # Initialize ONNX model session
        self.session = ort.InferenceSession(model_path)
        self.roop_directory = roop_directory

    def run_external_command(self, target_path, source_path, output_path):
        # Change to the Roop directory
        original_directory = os.getcwd()
        os.chdir(self.roop_directory)
        
        # Define the command to run
        command = [
            "python", "run.py",
            "--target", target_path,
            "--source", source_path,
            "-o", output_path,
            "--execution-provider", "cuda",
            "--frame-processor", "face_swapper"
        ]
        
        try:
            # Run the command
            logger.info(f"Running command: {' '.join(command)}")
            subprocess.run(command, check=True)
            logger.info("Face swapping completed successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed with error: {e}")
            raise
        finally:
            # Return to the original directory
            os.chdir(original_directory)

    def swap_faces(self, target_path, source_path, output_path):
        # Example: Using the external command (Roop face swapper)
        self.run_external_command(target_path, source_path, output_path)
