FROM python:3.8-slim-buster

WORKDIR /opt/bot

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
