from flask import Flask, jsonify, request, render_template, Response
from flask_cors import CORS
from helper import parse_selene, get_cleaned_script, create_audio
from flask_wtf import FlaskForm
from wtforms import (StringField, SelectField,SubmitField)
from wtforms.validators import DataRequired
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = 'mysecretkey'

@app.route('/get-audio')
def get_audio():
    if request.args.get('doc_id'):
        doc_id = request.args.get('doc_id')
    else:
        return jsonify({"error": "doc_id parameter is required"}), 400
    if request.args.get('lang'):
        language = request.args.get('lang')
    else:
        language = "english"
    if request.args.get('voice'):
        voice = request.args.get('voice')
    else:
        voice = "shimmer"
    response = parse_selene(doc_id)
    cleaned = get_cleaned_script(response, language)
    create_audio(doc_id, cleaned, voice, language)

    payload = {
        "doc_id": doc_id,
        "response": cleaned,
        "language": language,
    }
    
    return jsonify(payload), 200

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/audio/<filename>')
def stream_audio(filename):
    dir = request.args.get('dir')
    def generate():
        with open(f'{dir}/{filename}', 'rb') as f:
            data = f.read(1024)
            while data:
                yield data
                data = f.read(1024)
    return Response(generate(), mimetype='audio/mpeg')

if __name__ == '__main__':
    app.run(debug=True)