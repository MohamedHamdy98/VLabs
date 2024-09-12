# face_swapper.py

import subprocess
import os

class FaceSwapper:
    def __init__(self, face_path, audio_path, output_path, pads):
        """
        Initialize the FaceSwapper with the necessary file paths and padding.

        :param face_path: Path to the face video file.
        :param audio_path: Path to the audio file.
        :param output_path: Path where the output video will be saved.
        :param pads: List of padding values.
        """
        self.face_path = face_path
        self.audio_path = audio_path
        self.output_path = output_path
        self.pads = pads

    def run(self):
        """
        Run the face swapping process using the inference script.
        """
        os.chdir("video-retalking")  # Ensure the working directory is set to the project directory

        # Command to run the face swapping script
        command = [
            'python3', 'inference.py',
            '--face', self.face_path,
            '--audio', self.audio_path,
            '--pads', ' '.join(map(str, self.pads)),
            '--outfile', self.output_path
        ]

        # Execute the command
        subprocess.run(command, check=True)
