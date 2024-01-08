from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from myproject.spiders.myspider import OpggSpider # A REVOIR

# Initialisez le spider
spider = OpggSpider()

# Définissez l'URL de départ en utilisant set_start_url
spider.set_start_url("https://www.op.gg/summoners/euw/NewSummoner")

# Créez un objet CrawlerProcess avec les paramètres du projet
process = CrawlerProcess(get_project_settings())

# Ajoutez le spider à la file d'attente du processus
process.crawl(spider)

# Exécutez le processus (le script peut être bloqué ici jusqu'à ce que le spider soit terminé)
process.start()

# Une fois le spider terminé, vous pouvez appeler parse_another_url avec une nouvelle URL
new_url = "https://www.op.gg/summoners/euw/AnotherSummoner"
spider.parse_another_url(response=None, new_url=new_url)
