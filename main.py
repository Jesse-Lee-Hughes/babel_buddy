import os

from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audio' not in request.files:
        return jsonify({"error": "No file part"})
    file = request.files['audio']
    if file.filename == '':
        return jsonify({"error": "No selected file"})
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print('debugging')
        print('debugging')
        print(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"message": "File uploaded successfully"})


@app.route('/uploads', methods=['GET'])
def play_file():
    path = os.path.join(app.config['UPLOAD_FOLDER'])
    contents = os.listdir(path)
    return jsonify({"message": "Current files: {contents}".format(contents=contents)})


if __name__ == '__main__':
    app.run(debug=True)
