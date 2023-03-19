import datetime
import os
import re
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
        start = datetime.time(7)
        end = datetime.time(17)
        if start <= timestamp <= end:
            if submission.id not in posts_replied_to:
                process_submission(submission)
                with open("posts_replied_to.txt", "a") as f:
                    f.write(submission.id + "\n")
                sleep(randint(700, 800))
                # sleep(randint(3, 9))


def process_submission(submission):
    title = submission.title.strip()
    for top_level_comment in submission.comments:
        if re.search('deleted|I am a bot', top_level_comment.body):
            continue
        else:
            comment = " ".join(top_level_comment.body.split())
            print("Title:", title)
            print("    -:", comment)
            prompt = "write a short slightly cynical yet reassuring reply in less than 30 words to the comment '{}' in the " \
                     "context of the title '{}' without using the words 'Oh', " \
                     "'Wow', " \
                     "and 'Great'".format(comment, title)
            completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                      messages=[{"role": "user", "content": prompt}])
            reply = completion.choices[0].message.content.replace('"', '').strip()
            if re.search('AI|language model', reply):
                print("Reply leaks AI usage")
                return
            print("   --:", reply)
            print()
            top_level_comment.reply(reply)
            break


if __name__ == "__main__":
    main()
