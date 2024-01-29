FROM python:3.9
LABEL authors="keren couton & matthieu constantin"

WORKDIR /ScrapyDocker

COPY ./Scrapy/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

COPY ./Scrapy/ .

CMD ["scrapy", "crawl", "opgg"]
