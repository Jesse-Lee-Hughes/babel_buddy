import os

import dotenv
import ffmpeg
from flask import Flask, render_template, request, jsonify, send_file

from library.speech.speech import AzureSpeechTranscribe

dotenv.load_dotenv()

speech_region = os.getenv('SPEECH_REGION')
speech_key = os.getenv('SPEECH_API_KEY')

app = Flask(__name__)
app.config['UPLOADS_FOLDER'] = 'uploads/'
app.config['DOCUMENTS_FOLDER'] = 'documents/'


@app.route('/')
def index():
    return render_template('index.html')


def convert_to_pcm_wav(input_path):
    temp_output_path = f"{input_path}.tmp.wav"
    try:
        # Perform the conversion to the temporary file
        ffmpeg.input(input_path).output(temp_output_path, acodec='pcm_s16le', ac=1, ar='16000').run()

        # Replace the original file with the converted file
        os.replace(temp_output_path, input_path)

    except ffmpeg.Error as e:
        print(f'An error occurred during conversion: {e.stderr.decode()}')
        raise
    except Exception as e:
        print(f'An unexpected error occurred: {e}')
        raise


@app.route('/audio', methods=['GET'])
def get_synthesized_audio():
    try:
        file_path = os.path.abspath('uploads/synthesized_audio.wav')
        print(f"Serving file from: {file_path}")

        if not os.path.isfile(file_path):
            return jsonify({"error": "File does not exist"}), 404

        return send_file(
            file_path,
            as_attachment=True,
            mimetype='audio/wav'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/text', methods=['GET'])
def get_transcription():
    try:
        return send_file(
            'documents/translate.txt',
            as_attachment=True,
            download_name='translated.txt',
            mimetype='text/plain'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/upload', methods=['POST'])
def transcribe_audio():
    # try:
    # Check for the audio file in the request
    if 'audio' not in request.files:
        return jsonify({"error": "Audio file not present."}), 400

    file = request.files['audio']
    if file.filename == '':
        return jsonify({"error": "Unable to load audio file"}), 400

    input_language = request.form.get('input_language', 'en-US')
    output_language = request.form.get('output_language', 'yue')

    # Save the file to a temporary location
    rel_file_path = os.path.join(app.config['UPLOADS_FOLDER'], file.filename)
    file.save(rel_file_path)
    print(f"File saved to {rel_file_path}")

    # Convert to PCM WAV if needed
    convert_to_pcm_wav(rel_file_path)
    print("File converted to PCM WAV format")

    # Ensure the file exists
    if not os.path.isfile(rel_file_path):
        return jsonify({"error": f"The audio file does not exist at {rel_file_path}"}), 400

    # Initialize and use AzureSpeechTranscribe
    speech_api = AzureSpeechTranscribe(
        speech_key,
        speech_region,
        rel_file_path,
        input_language=input_language,
        output_language=output_language
    )
    result = speech_api.transcribe()
    print(f"Transcription result: {result}")

    # Ensure transcription result is not None
    if result is None:
        return jsonify({"error": "Transcription result is None"}), 500

    # Save the transcription result
    txt_path = os.path.join(app.config['DOCUMENTS_FOLDER'], 'translate.txt')
    with open(txt_path, 'w+') as f:
        f.write(result)

    # Synthesize speech from the result
    synthesized_audio_path = os.path.expanduser('~/repos/canto/uploads/synthesized_audio.wav')
    speech_api.synthesize_speech(result, target_language=output_language, output_path=synthesized_audio_path)

    # Send the synthesized audio file as an attachment
    return send_file(
        synthesized_audio_path,
        as_attachment=True,
        mimetype='audio/wav'
    )


if __name__ == '__main__':
    app.run(debug=True)
