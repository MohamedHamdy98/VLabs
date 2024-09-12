import os
import uuid
import re
import subprocess
import time
import langid
from pydub import AudioSegment
import torchaudio
import torch
from speech_recognition import Recognizer, AudioFile
from deep_translator import GoogleTranslator
from model_manager import ModelManagerWrapper

class AudioProcessor:
    def __init__(self):
        # Change to the directory where the repository is cloned
        os.chdir("xtts2-hf")

        # Initialize the speech recognizer and the model manager
        self.recognizer = Recognizer()
        self.model_manager = ModelManagerWrapper()
        # Define supported languages and maximum text length for each language
        self.supported_languages = self.model_manager.config.languages
        self.MAX_TEXT_LENGTH = {
            'en': 1000, 'es': 1000, 'fr': 1000, 'de': 1000, 'it': 1000,
            'pt': 1000, 'pl': 1000, 'tr': 1000, 'ru': 1000, 'nl': 1000,
            'cs': 1000, 'ar': 500, 'zh-cn': 500, 'ja': 500
        }

    def transcribe_audio(self, audio_file, language):
        """
        Transcribe audio from a file into text using Google Speech Recognition.
        
        :param audio_file: Path to the audio file.
        :param language: Language code for speech recognition.
        :return: Transcribed text or None if an error occurs.
        """
        try:
            with AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio, language=language)
                return text
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return None

    def translate_text(self, text, src_lang, trans_lang):
        """
        Translate text from source language to target language using Google Translator.
        
        :param text: Text to be translated.
        :param src_lang: Source language code.
        :param trans_lang: Target language code.
        :return: Translated text or None if an error occurs.
        """
        try:
            translator = GoogleTranslator(source=src_lang, target=trans_lang)
            return translator.translate(text)
        except Exception as e:
            print(f"Error translating text: {e}")
            return None

    def predict(self, prompt, language, audio_file_pth=None, mic_file_path=None, use_mic=False, voice_cleanup=False, no_lang_auto_detect=False):
        """
        Generate audio output based on the given prompt and language.
        
        :param prompt: Text prompt to be processed.
        :param language: Target language code.
        :param audio_file_pth: Path to the audio file for reference.
        :param mic_file_path: Path to the microphone recording file (if using mic).
        :param use_mic: Boolean flag to indicate if mic input should be used.
        :param voice_cleanup: Boolean flag to indicate if voice cleanup should be applied.
        :param no_lang_auto_detect: Boolean flag to skip automatic language detection.
        :return: Path to the merged output audio file or None if an error occurs.
        """
        # Change to the directory where the repository is cloned
        os.chdir("xtts2-hf")

        # Check if the provided language is supported
        if language not in self.supported_languages:
            print(f"Language {language} is not supported.")
            return None

        # Detect the language of the prompt
        language_predicted = langid.classify(prompt)[0].strip()
        if language_predicted == "zh":
            language_predicted = "zh-cn"

        # Validate language match if language auto-detection is not disabled
        if len(prompt) > 15 and language_predicted != language and not no_lang_auto_detect:
            print("Detected language does not match chosen language.")
            return None

        # Split the prompt into chunks if it exceeds the maximum length
        max_length = self.MAX_TEXT_LENGTH.get(language, 200)
        chunks = [prompt[i:i + max_length] for i in range(0, len(prompt), max_length)] if len(prompt) > max_length else [prompt]

        # Validate microphone file path if using mic input
        if use_mic and not mic_file_path:
            print("Please record your voice with Microphone.")
            return None

        # Clean up the audio if required, otherwise use the provided path
        if voice_cleanup:
            speaker_wav = self.clean_audio(mic_file_path if use_mic else audio_file_pth)
        else:
            speaker_wav = mic_file_path if use_mic else audio_file_pth

        all_outputs = []
        for chunk in chunks:
            try:
                # Measure the time to calculate conditioning latents
                t_latent = time.time()
                gpt_cond_latent, speaker_embedding = self.model_manager.model.get_conditioning_latents(
                    audio_path=speaker_wav, gpt_cond_len=30, gpt_cond_chunk_len=4, max_ref_length=60
                )
                latent_calculation_time = time.time() - t_latent

                # Clean up the chunk text for processing
                chunk = re.sub("([^\x00-\x7F]|\w)(\.|\。|\?)", r"\1 \2\2", chunk)
                t0 = time.time()
                # Generate audio from the text prompt using the model
                out = self.model_manager.model.inference(
                    chunk, language, gpt_cond_latent, speaker_embedding,
                    repetition_penalty=5.0, temperature=0.75
                )
                inference_time = time.time() - t0

                if out is None or "wav" not in out or out["wav"] is None:
                    print("No audio data returned.")
                    continue

                # Save the generated audio to a file
                real_time_factor = (time.time() - t0) / out["wav"].shape[-1] * 24000
                output_path = f"/content/output_{uuid.uuid4()}.wav"
                torchaudio.save(output_path, torch.tensor(out["wav"]).unsqueeze(0), 24000)
                all_outputs.append(output_path)
            except RuntimeError as e:
                print("RuntimeError:", str(e))
                return None

        # Combine all generated audio files into one
        combined = AudioSegment.empty()
        for audio_file in all_outputs:
            audio = AudioSegment.from_wav(audio_file)
            combined += audio

        # Export the combined audio to a single file
        merged_output_path = "/content/merged_output.wav"
        combined.export(merged_output_path, format="wav")
        return merged_output_path

    def clean_audio(self, audio_file):
        """
        Clean up the audio file using FFmpeg to remove noise and unwanted parts.
        
        :param audio_file: Path to the audio file to be cleaned.
        :return: Path to the cleaned audio file.
        """
        # Change to the directory where the repository is cloned
        os.chdir("xtts2-hf")

        out_filename = f"/content/{uuid.uuid4()}.wav"
        # FFmpeg command to process the audio file
        shell_command = f"ffmpeg -y -i {audio_file} -af lowpass=8000,highpass=75,areverse,silenceremove=start_periods=1:start_silence=0:start_threshold=0.02,areverse,silenceremove=start_periods=1:start_silence=0:start_threshold=0.02 {out_filename}"
        subprocess.run(shell_command, shell=True, check=True)
        return out_filename
 