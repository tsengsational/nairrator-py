from flask import Flask, jsonify, render_template
from helper import parse_selene, get_cleaned_script, create_audio
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'

@app.route('/get-audio/<doc_id>')
def get_audio(doc_id):
    response = parse_selene(doc_id)
    cleaned = get_cleaned_script(response)
    cleaned = get_cleaned_script("this is just for testing!")
    create_audio(cleaned)

    payload = {
        "doc_id": doc_id,
        "response": cleaned,
    }
    
    return jsonify(payload), 200

# @app.route('/')
# def index():
#     # Connecting to a template (html file)
#     return render_template('basic.html')


class InfoForm(FlaskForm):
    docId = StringField('Please enter docId')
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def index():
    docId = False
    # Create instance of the form.
    form = InfoForm()
    # If the form is valid on submission (we'll talk about validation next)
    if form.validate_on_submit():
        # Grab the data from the docId on the form.
        docId = form.docId.data
        docId2 = docId
        docId = False
        # Reset the form's docId data to be False
        # form.docId.data = ''
        cleaned = get_cleaned_script("this is just for testing!")
        create_audio(cleaned)
        result_text = "this is just for testing {}".format(docId2)
        return render_template('result.html', result_text=result_text)

    return render_template('home.html', form=form, docId=docId)


if __name__ == '__main__':
    app.run(debug=True)