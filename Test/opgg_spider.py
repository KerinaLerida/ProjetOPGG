import scrapy
import json
import requests

from Scrapy.crawler.crawler.spiders.data_fct import main


class OpggSpider(scrapy.Spider):
    name = "opgg"
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
        for url in self.start_urls:
            yield self.system_request(url)

    def parse(self, response):
        data_content = response.css('#__NEXT_DATA__::text').get()

        if data_content:
            try:
                json_data = json.loads(data_content)
                with open('opgg_project/spiders/output.json', 'w', encoding='utf-8') as json_file:
                    json.dump(json_data, json_file, ensure_ascii=False, indent=2)
                main()
            except json.JSONDecodeError as e:
                self.log(f"Failed to decode JSON: {e}")

    def parse_another_url(self, response, new_url):
        yield self.system_request(new_url)

    """def url_exists(self, url):
        try:
            response = requests.head(url)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def set_start_url(self, url):
        # Ajoutez l'URL spécifiée à la liste des start_urls
        if url:
            self.start_urls = [url]
        else :
            self.log("Empty URL provided. Start URL list not updated.")

    def start_requests(self):
        #headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',}
        # Utilisez la liste des start_urls définie par set_start_url ou la valeur par défaut
        for url in self.start_urls or ["https://www.op.gg/summoners/euw/Caps-45555"]:
            #yield scrapy.Request(url, headers=headers, callback=self.parse)
            request=self.system_request(url)
            if request is not None:
                yield request

    def system_request(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }
        try:
            if self.url_exists(url):
                self.set_start_url(url)
                return scrapy.Request(url, headers=headers, callback=self.parse)
            else:
                self.log(f"URL '{url}' does not exist.")
                return None
        except Exception as e:
            self.log(f"An error occurred during system_request: {e}")
            return None

    def parse(self, response):
        data_content = response.css('#__NEXT_DATA__::text').get()

        if data_content:
            try:
                json_data = json.loads(data_content)
                with open('../Test/output.json', 'w', encoding='utf-8') as json_file:
                    json.dump(json_data, json_file, ensure_ascii=False, indent=2)
                main()
            except json.JSONDecodeError as e:
                self.log(f"Failed to decode JSON: {e}")

    def parse_another_url(self, response, new_url):
        # Appel de cette méthode depuis un autre script en passant une nouvelle URL : ReScrape l'url
        self.set_start_url(new_url)
        #yield scrapy.Request(new_url, callback=self.parse)
        request=self.system_request(new_url)
        if request is not None:
            yield request"""

