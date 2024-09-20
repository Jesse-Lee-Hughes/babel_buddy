import os

import dotenv
import ffmpeg
from flask import Flask, render_template, request, jsonify, send_file

from library.base.log_handler import get_logger
from library.speech import SpeechTranscriber, SpeechSynthesizer

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


@app.route('/audio', methods=['GET'])
@handle_exceptions
def get_synthesized_audio():
    file_path = os.path.abspath(os.path.join(app.config['UPLOADS_FOLDER'], 'synthesized_audio.wav'))
    logger.debug(f"Serving file from: {file_path}")
    if not os.path.isfile(file_path):
        return jsonify({"error": "File does not exist"}), 404
    return send_file(file_path, as_attachment=True, mimetype='audio/wav')


@app.route('/text', methods=['GET'])
@handle_exceptions
def get_transcription():
    file_path = os.path.join(app.config['DOCUMENTS_FOLDER'], 'translate.txt')
    return send_file(file_path, as_attachment=True, download_name='translated.txt', mimetype='text/plain')


@app.route('/upload', methods=['POST'])
@handle_exceptions
def transcribe_audio():
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
    result = speech_api.transcribe()

    if result is None:
        return jsonify({"error": "Transcription failed"}), 500

    # Save Transcription and Synthesize Speech
    txt_path = save_transcription(result, app.config['DOCUMENTS_FOLDER'])
    audio_path = synthesize_speech(SpeechSynthesizer(speech_key, speech_region), result, output_language,
                                   app.config['UPLOADS_FOLDER'])

    # Send Synthesized Audio File
    return send_file(audio_path, as_attachment=True, mimetype='audio/wav')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)