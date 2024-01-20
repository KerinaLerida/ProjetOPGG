import scrapy
import json
import os

class OpggSpider(scrapy.Spider):
    name = "opgg_scraper"
    #start_urls = ["https://www.op.gg/summoners/euw/NPC%20Kerina-Coach", "https://www.op.gg/summoners/euw/Caps-45555","https://www.op.gg/summoners/euw/NPC%20Princess-Coach"]
    start_urls = ["https://www.op.gg/summoners/euw/Caps-45555"]
    def start_requests(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        }

        for url in self.start_urls:
            yield scrapy.Request(url, headers=headers, callback=self.parse)

    def parse(self, response):

        # Sélectionnez la balise select par son ID
        select_element = response.css('#AUTOCOMPLETE-REGION')

        # Obtenez toutes les valeurs data-value
        data_values = select_element.css('option::attr(data-value)').getall()

        # Imprimez les valeurs récupérées
        print(data_values)

        # Extraire le texte de la balise title
        #region = response.css('#pageview_variables_params::text').get()

        #print(region)
        title_text = response.css("title::text").get()

        #rank_element = response.css('.css-1kw4425 > div:nth-child(2)')
        #player_rank = rank_element.css('::text').get()
        #print(player_rank) # ça marche

        #image=response.css(".css-1kw4425 > div:nth-child(2) > div:nth-child(1) > img:nth-child(1)")
        #url_image=image.css('::attr(src)').get()
        #print(url_image)
        # if none alors unranked

        data_content = response.css('#__NEXT_DATA__::text').get()

        if data_content:
            # Load the JSON content
            try:
                json_data = json.loads(data_content)
                # Process the JSON data as needed
                #self.log(json_data)

                # Save the JSON data to a file (e.g., output.json)
                with open('../opgg_project/output.json', 'w', encoding='utf-8') as json_file:
                    json.dump(json_data, json_file, ensure_ascii=False, indent=2)
            except json.JSONDecodeError as e:
                self.log(f"Failed to decode JSON: {e}")

        # Assurez-vous que le texte de la balise title existe
        if title_text:
            # Divisez le texte en utilisant le caractère '#'
            name_and_tag = title_text.split('#', 1)

            # Assurez-vous qu'il y a au moins deux éléments après la division
            if len(name_and_tag) == 2:
                player_name = name_and_tag[0].strip()
                player_tag = name_and_tag[1].replace(' - Summoner Stats - League of Legends', '').strip()

                # Construire le dictionnaire
                player_data = {
                    'player_name': player_name,
                    'player_tag': player_tag,
                }

                # Créer un fichier JSON temporaire pour chaque joueur
                temp_filename = f'{player_name}_{player_tag}.json'
                with open(temp_filename, 'w', encoding='utf-8') as temp_file:
                    json.dump(player_data, temp_file, ensure_ascii=False, indent=2)





