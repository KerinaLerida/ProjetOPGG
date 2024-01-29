from fastapi import FastAPI
from pydantic import BaseModel
import requests

app = FastAPI()

class URLPayload(BaseModel):
    url: str

@app.post("/scrape")
def trigger_scraping(payload: URLPayload):
    url = payload.url

    # Envoyez l'URL au conteneur Scrapy pour le scraping
    response = requests.post("http://scrapy:8000/scrape", json={"url": url})  # Assurez-vous que "scrapy" est le nom du service dans votre docker-compose
    return response.json()

