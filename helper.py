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
        # response.raise_for_status()
        html = json.loads(response.text)
        html_data = html["data"]
        script = ""
        match html_data["templateType"]:
            case "STRUCTUREDCONTENT":
                text_list = html_data["pages"]["list"][0]["contents"]["list"]
                # add title
                script += html_data["title"]
                # add article text
                for text in text_list:
                    if text["type"] == "HTML":
                        script += text["data"]["html"]
            case "LISTSC":
                # add title
                script += html_data["title"]
                # add intro
                intros = html_data["intro"]["list"]
                for intro in intros:
                    if intro["type"] == "HTML":
                        script += intro["data"]["html"]
                # add list
                items = html_data["items"]["list"]
                for item in items:
                    contents = item["contents"]["list"]
                    for content in contents:
                        match content["type"]:
                            case "HEADING":
                                script += content["data"]["text"]
                            case "HTML":
                                script += content["data"]["html"]
            case "RECIPESC":
                #add title
                script += html_data["title"]
                # add intro
                intros = html_data["intro"]["list"]
                for intro in intros:
                    match intro["type"]:
                        case "HEADING":
                            script += intro["data"]["text"]
                        case "HTML":
                            script += intro["data"]["html"]
                # add ingredients
                ingredients = html_data["ingredient"]["list"]
                script += "Ingredients: "
                for ingredient in ingredients:
                    script += ingredient + " "
                # add instructions
                instructions = html_data["instruction"]["list"]
                script += "Directions: "
                for i, instruction in enumerate(instructions):
                    match instruction["type"]:
                        case "HTML":
                            script += f"Step {i + 1}: " + instruction["data"]["html"]
            case "TAXONOMYSC":
                # add title
                script += html_data["title"]
                # add intro
                intros = html_data["intro"]["list"]
                for intro in intros:
                    match intro["type"]:
                        case "HEADING":
                            script += intro["data"]["text"]
                        case "HTML":
                            script += intro["data"]["html"]


        
        CLEANR = re.compile('<.*?>')
        cleaned = BeautifulSoup(script, "html.parser")
        cleaned = re.sub(CLEANR, '', f"{cleaned}")

        return cleaned

def get_cleaned_script(script_str, language):
    client = OpenAI(api_key=environ.get("OPENAI_SECRET"))
    messages = [
                    {"role": "system", "content": "You are a copy editor"},
                    {"role": "user", "content": "I would like you to take the following text and remove any extraneous white space. Make sure each sentence is followed by exactly one space."},
                    {"role": "user", "content": "Text: " + script_str}
                ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    if language != "english":
       response_text = response.choices[0].message.content
       response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages = [
                {"role": "user", "content": f"Translate the following text into {language}"},
                {"role": "user", "content": f"Text: {response_text}"}
           ]
       )

    script_raw = response.choices[0].message.content
    script_chunks = []
    sentences = split_into_sentences(script_raw)
    temp_chunk = ""

    for i, sentence in enumerate(sentences):
        length = len(sentence)
        if len(temp_chunk) + length < 4096:
            temp_chunk += " " + sentence
        else:
            script_chunks.append(temp_chunk)
            temp_chunk = ""
    
    if len(temp_chunk) > 0:
        script_chunks.append(temp_chunk)

    
    return script_chunks

def create_audio(doc_id, script_chunks, voice="shimmer", language="english"):
    client = OpenAI(api_key=environ.get("OPENAI_SECRET"))
    parent_path = Path(__file__).parent
    full_file_path = parent_path / f"clips/{doc_id}-{language}.mp3"

    if not Path(parent_path / "clips").is_dir():
        Path(parent_path / "clips").mkdir(parents=True, exist_ok=True)
    for i, chunk in enumerate(script_chunks):
        speech_file_path = parent_path / f"clips/clip-{i}.mp3"
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=chunk
        )

        response.stream_to_file(speech_file_path)
    
    if len(script_chunks) > 1:
        sound = AudioSegment.empty()

        for i, chunk in enumerate(script_chunks):
            # Join audio clips
            clip_path = parent_path / f"clips/clip-{i}.mp3"
            clip = AudioSegment.from_file(clip_path, format="mp3")
            sound = sound + clip
                
        # Export the full audio file
        sound.export(full_file_path, format="mp3")

        for i, chunk in enumerate(script_chunks):
            # Delete temporary audio clips
            clip_path = parent_path / f"clips/clip-{i}.mp3"
            remove(clip_path)
        
        return full_file_path
    else:
        sound = AudioSegment.from_file(parent_path / "clips/clip-0.mp3")
        sound.export(full_file_path, format="mp3")
        remove(parent_path / "clips/clip-0.mp3")
    
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
