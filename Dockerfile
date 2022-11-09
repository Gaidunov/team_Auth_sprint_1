FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt --no-cache-dir

COPY . .

ENTRYPOINT ["flask", "run", "--host=0.0.0.0", "--port=5000"] 