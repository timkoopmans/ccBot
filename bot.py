import datetime
import os
from random import randint
from time import sleep

import openai
import praw as praw


def main():
    if not os.path.isfile("posts_replied_to.txt"):
        posts_replied_to = []
    else:
        with open("posts_replied_to.txt", "r") as f:
            posts_replied_to = f.read()
            posts_replied_to = posts_replied_to.split("\n")
            posts_replied_to = list(filter(None, posts_replied_to))
    reddit = praw.Reddit("cc")
    subreddit = reddit.subreddit("CryptoCurrency")
    for submission in subreddit.stream.submissions():
        timestamp = datetime.datetime.now().time()
        start = datetime.time(8)
        end = datetime.time(17)
        if start <= timestamp <= end:
            if submission.id not in posts_replied_to:
                process_submission(submission)
                with open("posts_replied_to.txt", "a") as f:
                    f.write(submission.id + "\n")
                sleep(randint(300, 900))


def process_submission(submission):
    title = submission.title.lower()
    print("Title: ", title)
    prompt = "write a short cynical reply in less than 30 words to '{}' without using the words 'Oh', 'Wow', " \
             "and 'Great'".format(title)
    completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}])
    reply = completion.choices[0].message.content.replace('"', '')
    print("Reply: ", reply)
    submission.reply(reply)


if __name__ == "__main__":
    main()
