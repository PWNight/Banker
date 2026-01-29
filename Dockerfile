FROM python:3.14

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

RUN mkdir -p /usr/src/bot
WORKDIR /usr/src/bot

COPY . .

CMD [ "python3", "bot.py" ] 