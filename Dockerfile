FROM python:3.9

WORKDIR /code
RUN pip install praw openai redis

COPY . .
CMD ["python", "bot.py"]