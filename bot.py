import datetime
import os
import re
from random import randint
from time import sleep

import openai
import praw as praw
import redis

import paris

logger = paris.logger


def main():
    r = redis.Redis(host=os.environ.get("REDIS_HOST"), port=os.environ.get("REDIS_PORT"), db=0,
                    password=os.environ.get("REDIS_PASSWORD"))

    reddit = praw.Reddit("cc")
    subreddit = reddit.subreddit("CryptoCurrency")
    for submission in subreddit.stream.submissions():
        timestamp = datetime.datetime.now().time()
        start = datetime.time(13)
        end = datetime.time(23)
        if start <= timestamp <= end:
            if r.exists(submission.id):
                logger.warning("Submission already processed")
                continue
            elif re.search('safemoon', submission.title):
                logger.warning("Submission has banned words")
                continue
            else:
                r.set(submission.id, 1)
                process_submission(submission)
                sleep(randint(700, 800))
        else:
            logger.info("Outside of processing window")
            sleep(randint(700, 800))


def process_submission(submission):
    title = submission.title.strip()
    for top_level_comment in submission.comments:
        if top_level_comment.stickied or top_level_comment.author.is_mod:
            continue
        if re.search('deleted|I am a bot|GPT|chatGPT|gpt', top_level_comment.body):
            continue
        else:
            comment = " ".join(top_level_comment.body.split())
            logger.info("  > %s", title)
            logger.info(" >> %s", comment)
            prompt = "write a short slightly cynical reply in less than 30 words with one sentence to the comment '{}' in the " \
                     "context of the title '{}' without using the words 'Oh', " \
                     "'Wow', " \
                     "and 'Great'".format(comment, title)

            try:
                completion = openai.ChatCompletion.create(model="gpt-3.5-turbo",
                                                          messages=[{"role": "user", "content": prompt}])
            except Exception as error:
                logger.error(error)
                return

            if not completion.choices:
                logger.warning("No reply found")
                return
            else:
                reply = completion.choices[0].message.content.replace('"', '').strip()
                if re.search('AI|language model', reply):
                    logger.warning("Reply leaks AI usage")
                    return
                elif re.search('Oh|Wow|Great|Sherlock', reply):
                    logger.warning("Reply has banned words")
                    return
                logger.info(">>> %s", reply)
                top_level_comment.reply(reply)
                break


if __name__ == "__main__":
    main()
