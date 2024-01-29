FROM python:3.9
LABEL authors="keren couton & matthieu constantin"

WORKDIR /ApplicationDocker

COPY ./Application/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8050

COPY ./Application/ .

CMD ["python", "dashboard.py"]
