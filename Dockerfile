FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt --no-cache-dir

COPY . .

RUN export  FLASK_APP=src.app

ENTRYPOINT ["flask", "run"]
