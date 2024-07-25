import os

import dotenv
import ffmpeg
from flask import Flask, render_template, request, jsonify
from library.speech.speech import AzureSpeechTranscribe

dotenv.load_dotenv()

speech_region = os.getenv('SPEECH_REGION')
speech_key = os.getenv('SPEECH_API_KEY')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'


@app.route('/')
def index():
    return render_template('index.html')


def convert_to_pcm_wav(input_path):
    # Create a temporary file path for the converted output with .wav extension
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


@app.route('/upload', methods=['POST'])
def transcribe_audio():
    try:
        # Check for the audio file in the request
        if 'audio' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['audio']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        # Save the file to a temporary location
        rel_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(rel_file_path)

        # Convert to PCM WAV if needed (implement the actual logic)
        convert_to_pcm_wav(rel_file_path)

        # Ensure the file exists
        if not os.path.isfile(rel_file_path):
            return jsonify({"error": f"The audio file does not exist at {rel_file_path}"}), 400

        # Initialize and use AzureSpeechTranscribe
        speech_api = AzureSpeechTranscribe(speech_key, speech_region, rel_file_path)
        result = speech_api.transcribe()
        return jsonify({"success": True, "result": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
[]

if __name__ == '__main__':
    app.run(debug=True)
