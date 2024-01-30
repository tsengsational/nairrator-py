from flask import Flask, request, jsonify
from helper import parse_selene


app = Flask(__name__)

@app.route('/get-audio/<doc_id>')
def get_audio(doc_id):
    response = parse_selene(doc_id)

    payload = {
        "doc_id": doc_id,
        "response": response
    }
    
    # print(payload)

    return jsonify(payload), 200


if __name__ == '__main__':
    app.run(debug=True)