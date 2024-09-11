# app.py

from flask import Flask, request, jsonify
from face_swapper import FaceSwapper
from config import TARGET_PATH, SOURCE_PATH, OUTPUT_PATH, MODEL_PATH
import model_setup

app = Flask(__name__)

# Setup environment and models
model_setup.setup_environment()

# Initialize face swapper
face_swapper = FaceSwapper(MODEL_PATH, roop_directory="roop")

@app.route('/swap', methods=['POST'])
def swap_faces():
    try:
        # Run face swapping process
        face_swapper.swap_faces(TARGET_PATH, SOURCE_PATH, OUTPUT_PATH)
        return jsonify({"message": "Face swapping completed", "output_path": OUTPUT_PATH}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "Server is running"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False, port=5001)





    # # Start Flask app
    # ngrok_tunnel = ngrok.connect()
    # print(ngrok_tunnel)
    # app.run(port=81)
