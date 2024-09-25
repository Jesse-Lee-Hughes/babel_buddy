import os
import uuid

import dotenv
from flask import Flask, render_template, request, jsonify

from library.base.log_handler import get_logger
from library.speech import SpeechTranscriber, SpeechSynthesizer, SpeechTranscriberException

dotenv.load_dotenv()

# Configuration
app = Flask(__name__)
app.config['UPLOADS_FOLDER'] = '/tmp/'
app.config['DOCUMENTS_FOLDER'] = '/tmp/'
app.config['SPEECH_REGION'] = os.getenv('SPEECH_REGION')
app.config['SPEECH_API_KEY'] = os.getenv('SPEECH_API_KEY')
logger = get_logger(__name__)


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process_audio', methods=['POST'])
def process_audio():
    synth_api = SpeechSynthesizer(
        api_key=app.config['SPEECH_API_KEY'],
        region=app.config['SPEECH_REGION']
    )
    if 'audio' not in request.files or not request.files['audio'].filename:
        return jsonify({"error": "Invalid audio file"}), 400

    file = request.files['audio']
    input_language = request.form.get('input_language', 'en-US')
    output_language = request.form.get('output_language', 'yue')

    # Generate a unique file name using UUID
    unique_filename = f"{uuid.uuid4()}"
    rel_file_path = os.path.join(app.config['UPLOADS_FOLDER'], f"{unique_filename}.wav")

    # Save and Convert Audio File
    file.save(rel_file_path)
    logger.debug(f"File saved to {rel_file_path}")
    synth_api.convert_to_pcm_wav(rel_file_path)

    # Transcribe Audio
    speech_api = SpeechTranscriber(
        api_key=app.config['SPEECH_API_KEY'],
        region=app.config['SPEECH_REGION'],
        audio_file_path=rel_file_path,
        input_language=input_language,
        output_language=output_language
    )
    try:
        result = speech_api.transcribe()
    except SpeechTranscriberException as e:
        return jsonify({"error": str(e)}), 422

    if result is None:
        return jsonify({"error": "Transcription failed"}), 400

    output_path = os.path.join(app.config['UPLOADS_FOLDER'], f'synthesized_audio_{unique_filename}.wav')
    synth_api.synthesize_speech(
        text=result,
        target_language=output_language,
        output_path=output_path
    )

    # Read the audio file to return as response
    with open(output_path, 'rb') as audio_file:
        audio_data = audio_file.read()

    # Clean up the temporary files
    os.remove(rel_file_path)
    os.remove(output_path)

    # Return both audio and transcription
    response = {
        "transcription": result,
        "synthesized_audio": audio_data.decode('latin1'),  # Encode the bytes to string for JSON
    }

    return jsonify(response), 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
