from flask import Flask, jsonify, request, render_template, session
from helper import parse_selene, get_cleaned_script, create_audio
from flask_wtf import FlaskForm
from wtforms import (StringField, SelectField,SubmitField)
from wtforms.validators import DataRequired
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = 'mysecretkey'


def get_audio(doc_id, voice, language):
    response = parse_selene(doc_id)
    cleaned = get_cleaned_script(response, language)
    create_audio(doc_id, cleaned, voice, language)

    payload = {
        "doc_id": doc_id,
        "response": cleaned,
    }
    
    return jsonify(payload), 200


class InfoForm(FlaskForm):
    doc_id = StringField('Please enter docId:',validators=[DataRequired()])
    voice_option = SelectField(u'Choose Your Favorite Voice:',
                          choices=[('Alloy', 'Alloy'), ('Echo', 'Echo'),
                                   ('Fable', 'Fable'), ('Onyx', 'Onyx'),
                                   ('Nova', 'Shimmer')])
    language_option = SelectField(u'Choose Your Favorite Language:',
                          choices=[('English', 'Englis'), ('French', 'Franch'),
                                   ('Spanish', 'Spanish'), ('Chinese', 'Chinese')])
    submit = SubmitField('Submit')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = InfoForm()
    if form.validate_on_submit():
        session['doc_id'] = form.doc_id.data
        session['voice_option'] = form.voice_option.data
        session['language_option'] = form.language_option.data
        result_text = create_audio(session['doc_id'], session['voice_option'], session['language_option'])
        return render_template('result.html', result_text=result_text)

    return render_template('01-home.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)