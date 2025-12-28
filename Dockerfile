FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV ANALYSER_PATH=/data/

EXPOSE 8000

CMD ["python", "-m", "shiny", "run", "--reload", "--host", "0.0.0.0", "app.py"]