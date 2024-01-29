import scrapy
import json
import requests
import time
from .data_fct import main

class OpggSpider(scrapy.Spider):
    name = "opgg"
    allowed_domains = ['op.gg']
    start_urls=["https://www.op.gg/summoners/euw/NPC Kerina-Coach",
"https://www.op.gg/summoners/euw/NPC Honthagr-01530",
"https://www.op.gg/summoners/euw/NPC FoxSilver-NPC",
"https://www.op.gg/summoners/euw/NPC Reintack-EUW",
"https://www.op.gg/summoners/euw/NPC bebe-NPC",
"https://www.op.gg/summoners/euw/NPC Azaba-EUW",
"https://www.op.gg/summoners/euw/NPC Kog Mawtivé-EUW",
"https://www.op.gg/summoners/euw/NPC Yato-EUW",
"https://www.op.gg/summoners/euw/Caps-45555",
"https://www.op.gg/summoners/kr/Hide on bush-KR1",
"https://www.op.gg/summoners/euw/GoldenRetriever-NPC"]

    custom_settings = {
        'LOG_FILE': 'spider_logs.txt',  # Specify the log file name
    }

    def system_request(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            return scrapy.Request(url, headers=headers, callback=self.parse)
        except requests.RequestException as e:
            self.log(f"An error occurred during system_request: {e}")
            return None

    def start_requests(self):
        """
        for url in self.start_urls:
            yield self.system_request(url)"""
        while True:
            for url in self.start_urls:
                yield self.system_request(url)
            time.sleep(30)

    def start_requests_for_new_url(self, new_url):
        yield self.system_request(new_url)

    def parse(self, response):

        data_content = response.css('#__NEXT_DATA__::text').get()
        self.log(f"parsing {response.url})")

        if data_content:
            try:
                json_data = json.loads(data_content)
                main(json_data)  # Passer json_data à la fonction main dans data_fct.py
            except json.JSONDecodeError as e:
                self.log(f"Failed to decode JSON: {e}")





