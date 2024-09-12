from flask import Flask, request, jsonify, send_file
from model_setup import setup_environment
from audio_processing import AudioProcessor
import os

app = Flask(__name__)

# Setup environment and models
setup_environment.setup_environment()

# Change to the correct directory for model files if needed
os.chdir("xtts2-hf")

audio_processor = AudioProcessor()

@app.route('/predict', methods=['POST'])
def predict_endpoint():
    """
    Endpoint to handle predictions based on provided input data.
    
    Expects a JSON payload with the following fields:
    - prompt: Text to be processed.
    - language: Language code for processing.
    - trans_lang: Target language code for translation.
    - audio_file_pth: Path to an audio file (optional).
    - mic_file_path: Path to a microphone recording file (optional).
    - use_mic: Boolean flag to indicate if microphone input should be used (optional).
    - voice_cleanup: Boolean flag to indicate if voice cleanup should be applied (optional).
    - no_lang_auto_detect: Boolean flag to skip automatic language detection (optional).

    Returns:
    - Processed audio file if successful.
    - JSON error message if there are any issues.
    """
    data = request.json

    # Extract parameters from the request
    prompt = data.get('prompt')
    language = data.get('language')
    trans_lang = data.get('trans_lang')
    audio_file_pth = data.get('audio_file_pth')
    mic_file_path = data.get('mic_file_path')
    use_mic = data.get('use_mic', False)
    voice_cleanup = data.get('voice_cleanup', False)
    no_lang_auto_detect = data.get('no_lang_auto_detect', False)

    # Validate input
    if not prompt or not language:
        return jsonify({'error': 'Prompt and language are required'}), 400

    # Translate the prompt text
    translated_text = audio_processor.translate_text(prompt, language, trans_lang)
    try:
        # Process the translated text and generate audio output
        merged_output_path = audio_processor.predict(
            translated_text,
            trans_lang,
            audio_file_pth=audio_file_pth,
            mic_file_path=mic_file_path,
            use_mic=use_mic,
            voice_cleanup=voice_cleanup,
            no_lang_auto_detect=no_lang_auto_detect
        )

        # Return the generated audio file if successful
        if merged_output_path:
            return send_file(merged_output_path, mimetype='audio/wav', as_attachment=True, download_name='output.wav')
        else:
            return jsonify({'error': 'Error processing the request'}), 500

    except Exception as e:
        # Handle unexpected errors
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    # Run the Flask application
    app.run(host='0.0.0.0', port=3)
