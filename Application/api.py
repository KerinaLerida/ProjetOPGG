from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

class URLPayload(BaseModel):
    url: str

@app.post("/scrape")
def trigger_scraping(url):
    payload = {"url": url}

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    api_url= "http://scrapy:8000/get_new_url"

    # Envoyez l'URL au conteneur Scrapy pour le scraping
    try:
        response = requests.post(api_url, json=payload, headers=headers)  # Assurez-vous que "scrapy" est le nom du service dans votre docker-compose
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}


