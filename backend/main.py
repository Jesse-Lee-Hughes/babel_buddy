import os

import dotenv
import ffmpeg
from flask import Flask, render_template, request, jsonify

from library.base.log_handler import get_logger
from library.speech import SpeechTranscriber, SpeechSynthesizer, SpeechTranscriberException

dotenv.load_dotenv()

# Configuration
app = Flask(__name__)
app.config['UPLOADS_FOLDER'] = '/tmp/'
app.config['DOCUMENTS_FOLDER'] = '/tmp/'

logger = get_logger(__name__)

# Environment Variables
speech_region = os.getenv('SPEECH_REGION')
speech_key = os.getenv('SPEECH_API_KEY')


# Error Handling Decorator
def handle_exceptions(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            return jsonify({"error": str(e)}), 500

    wrapper.__name__ = func.__name__
    return wrapper


# Helper Functions
def convert_to_pcm_wav(input_path):
    temp_output_path = f"{input_path}.tmp.wav"
    try:
        ffmpeg.input(input_path).output(temp_output_path, acodec='pcm_s16le', ac=1, ar='16000').run()
        os.replace(temp_output_path, input_path)
    except ffmpeg.Error as e:
        logger.critical(f'Conversion error: {e.stderr.decode()}')
        raise
    except Exception as e:
        logger.critical(f'Unexpected error: {e}')
        raise


def save_transcription(result, folder):
    txt_path = os.path.join(folder, 'translate.txt')
    with open(txt_path, 'w+') as f:
        f.write(result)
    return txt_path


def synthesize_speech(api, text, output_language, folder):
    output_path = os.path.join(folder, 'synthesized_audio.wav')
    api.synthesize_speech(text, target_language=output_language, output_path=output_path)
    return output_path


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process_audio', methods=['POST'])
def process_audio():
    if 'audio' not in request.files or not request.files['audio'].filename:
        return jsonify({"error": "Invalid audio file"}), 400

    file = request.files['audio']
    input_language = request.form.get('input_language', 'en-US')
    output_language = request.form.get('output_language', 'yue')

    # Save and Convert Audio File
    rel_file_path = os.path.join(app.config['UPLOADS_FOLDER'], file.filename)
    file.save(rel_file_path)
    logger.debug(f"File saved to {rel_file_path}")
    convert_to_pcm_wav(rel_file_path)

    # Transcribe Audio
    speech_api = SpeechTranscriber(speech_key, speech_region, rel_file_path, input_language=input_language,
                                   output_language=output_language)
    try:
        result = speech_api.transcribe()
    except SpeechTranscriberException as e:
        return jsonify({"error": str(e)}), 422

    if result is None:
        return jsonify({"error": "Transcription failed"}), 400

    # Save Transcription
    txt_path = save_transcription(result, app.config['DOCUMENTS_FOLDER'])

    # Synthesize Speech
    audio_path = synthesize_speech(SpeechSynthesizer(speech_key, speech_region), result, output_language,
                                   app.config['UPLOADS_FOLDER'])

    # Read the audio file to return as response
    with open(audio_path, 'rb') as audio_file:
        audio_data = audio_file.read()

    # Return both audio and transcription
    response = {
        "transcription": result,
        "synthesized_audio": audio_data.decode('latin1'),  # Encode the bytes to string for JSON
    }

    return jsonify(response), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
