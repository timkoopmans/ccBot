FROM python:3.9

WORKDIR /code
RUN pip install praw openai

COPY . .
CMD ["python", "bot.py"]