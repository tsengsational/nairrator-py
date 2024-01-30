# Text-to-Speech Flask App

This is a simple Flask application that takes in text and returns an audio file of the text being read aloud.

## Usage

The `/get-audio/<doc_id>` endpoint takes in a document ID, processes the text from that document, and returns a JSON response with the original text and the path to the generated audio file.

To use it:

1. Send a GET request to `/get-audio/<doc_id>` with a valid doc ID
2. The app will retrieve the text, process it, and generate an audio file
3. The JSON response will contain the original text and audio file path

## Processing

The text processing pipeline is:

1. Retrieve text from database based on doc_id
2. Clean/preprocess text (`get_cleaned_script()`) 
3. Generate audio file from text (`create_audio()`)

## Local Development

To run the app locally:

1. Clone the repo
2. Install dependencies with `pip install -r requirements.txt` 
3. Setup environment variables (.env file)
4. Run `python main.py`
5. Send requests to `http://localhost:5000/get-audio/<doc_id>`

## Next Steps

Possible improvements:

- Add authentication
- Improve text cleaning and processing
- Support more audio formats 
- Containerize with Docker