import httpx
import json
import re
from bs4 import BeautifulSoup
from os import environ, remove
from openai import OpenAI
from pathlib import Path
from pydub import AudioSegment

def parse_selene(doc_id: str) -> str:
    with httpx.Client() as http_client:
        response = http_client.get(f"https://selene-k8s-prod.a-ue1.dotdash.com/document?docId={doc_id}")
        response.raise_for_status()
        html = json.loads(response.text)
        pages = html["data"]["pages"]["list"][0]["contents"]["list"]
        script = ""
        for page in pages:
            if page["type"] == "HTML":
                script += page["data"]["html"]
        
        CLEANR = re.compile('<.*?>')
        cleaned = BeautifulSoup(script, "html.parser")
        cleaned = re.sub(CLEANR, '', f"{cleaned}")

        return cleaned

def get_cleaned_script(script_str):
    client = OpenAI(api_key=environ.get("OPENAI_SECRET"))
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a copy editor"},
            {"role": "user", "content": "I would like you to take the following text and remove any extraneous white space. Make sure each sentence is followed by exactly one space. Do not change any of the actual words or sentences in the text."},
            {"role": "user", "content": "Text: " + script_str}
        ]
    )

    script_raw = response.choices[0].message.content
    script_chunks = []
    sentences = split_into_sentences(script_raw)
    temp_len = 0
    temp_chunk = ""

    for i, sentence in enumerate(sentences):
        length = len(sentence)
        if temp_len + length < 4096:
            temp_chunk += " " + sentence
            temp_len += len(sentence)
        else:
            script_chunks.append(temp_chunk)
            temp_chunk = ""
            temp_len = 0
    
    if temp_len > 0:
        script_chunks.append(temp_chunk)

    
    return script_chunks

def create_audio(script_chunks):
    client = OpenAI(api_key=environ.get("OPENAI_SECRET"))
    parent_path = Path(__file__).parent
    if not Path(parent_path / "clips").is_dir():
        Path(parent_path / "clips").mkdir(parents=True, exist_ok=True)
    for i, chunk in enumerate(script_chunks):
        speech_file_path = parent_path / f"clips/clip-{i}.mp3"
        response = client.audio.speech.create(
            model="tts-1",
            voice="shimmer",
            input=chunk
        )

        response.stream_to_file(speech_file_path)
    
    if len(script_chunks) > 1:
        sound = AudioSegment.empty()
        full_file_path = parent_path / f"clips/full-audio.mp3"
        print(full_file_path)

        for i, chunk in enumerate(script_chunks):
            # Join audio clips
            clip_path = parent_path / f"clips/clip-{i}.mp3"
            print(clip_path)
            clip = AudioSegment.from_file(clip_path, format="mp3")
            sound = sound + clip
                
        # Export the full audio file
        sound.export(full_file_path, format="mp3")

        for i, chunk in enumerate(script_chunks):
            # Delete temporary audio clips
            clip_path = parent_path / f"clips/clip-{i}.mp3"
            remove(clip_path)
        
        return full_file_path
    
def split_into_sentences(text: str):
    alphabets= "([A-Za-z])"
    prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
    suffixes = "(Inc|Ltd|Jr|Sr|Co)"
    starters = "(Mr|Mrs|Ms|Dr|Prof|Capt|Cpt|Lt|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
    acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
    websites = "[.](com|net|org|io|gov|edu|me)"
    digits = "([0-9])"
    multiple_dots = r'\.{2,}'

    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    text = re.sub(digits + "[.]" + digits,"\\1<prd>\\2",text)
    text = re.sub(multiple_dots, lambda match: "<prd>" * len(match.group(0)) + "<stop>", text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = [s.strip() for s in sentences]
    if sentences and not sentences[-1]: sentences = sentences[:-1]
    return sentences
