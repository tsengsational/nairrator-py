from flask import Flask, jsonify, request
from helper import parse_selene, get_cleaned_script, create_audio
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/get-audio/<doc_id>')
def get_audio(doc_id):
    language = request.args.get('lang')
    voice = request.args.get('voice')
    response = parse_selene(doc_id)
    cleaned = get_cleaned_script(response, language)
    create_audio(doc_id, cleaned, voice, language)

    payload = {
        "doc_id": doc_id,
        "response": cleaned,
    }
    
    return jsonify(payload), 200

if __name__ == '__main__':
    app.run(debug=True)