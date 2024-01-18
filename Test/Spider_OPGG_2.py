import scrapy
import json
from data_fct import main

class OpggSpider(scrapy.Spider):
    name = "opgg_scraper"
    #start_urls = []
    start_urls=["https://www.op.gg/summoners/euw/NPC Kerina-Coach",
"https://www.op.gg/summoners/euw/NPC Honthagr-01530",
"https://www.op.gg/summoners/euw/NPC FoxSilver-NPC",
"https://www.op.gg/summoners/euw/NPC Reintack-EUW",
"https://www.op.gg/summoners/euw/NPC bebe-NPC",
"https://www.op.gg/summoners/euw/NPC Azaba-EUW",
"https://www.op.gg/summoners/euw/NPC Kog Mawtivé-EUW",
"https://www.op.gg/summoners/euw/NPC Yato-EUW",
"https://www.op.gg/summoners/euw/Caps-45555",
"https://www.op.gg/summoners/kr/Hide on bush-KR1"]

    def set_start_url(self, url):
        # Ajoutez l'URL spécifiée à la liste des start_urls
        self.start_urls = [url]

    def start_requests(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        # Utilisez la liste des start_urls définie par set_start_url ou la valeur par défaut
        for url in self.start_urls or ["https://www.op.gg/summoners/euw/Caps-45555"]:
            yield scrapy.Request(url, headers=headers, callback=self.parse)

    def parse(self, response):
        data_content = response.css('#__NEXT_DATA__::text').get()

        if data_content:
            try:
                json_data = json.loads(data_content)
                with open('output.json', 'w', encoding='utf-8') as json_file:
                    json.dump(json_data, json_file, ensure_ascii=False, indent=2)
                main()
            except json.JSONDecodeError as e:
                self.log(f"Failed to decode JSON: {e}")

    def parse_another_url(self, response, new_url):
        # Appel de cette méthode depuis un autre script en passant une nouvelle URL : ReScrape l'url
        self.set_start_url(new_url)
        yield scrapy.Request(new_url, callback=self.parse)
