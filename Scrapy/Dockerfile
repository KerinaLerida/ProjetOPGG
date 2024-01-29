FROM python:3.9
LABEL authors="keren couton, matthieu constantin"

WORKDIR /ScrapyDocker

#COPY ./Scrapy/requirements.txt .
COPY ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

#COPY ./Scrapy/ .
COPY . .

CMD ["scrapy", "crawl", "opgg"]
