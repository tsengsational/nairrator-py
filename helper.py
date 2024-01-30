import httpx
import json
import re
from bs4 import BeautifulSoup

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
