import datetime
import os
import re
from random import randint
from time import sleep

import openai
import praw as praw
import redis
import fakeredis

import paris

logger = paris.logger

REDIS_HOST = os.environ.get("REDIS_HOST")
REDIS_PORT = os.environ.get("REDIS_PORT")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
DEBUG = os.environ.get("DEBUG", False)


def main():
    if DEBUG:
        logger.info("Debug mode enabled")
        r = fakeredis.FakeStrictRedis(version=7)
    else:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, password=REDIS_PASSWORD)

    reddit = praw.Reddit("cc")
    subreddit = reddit.subreddit("CryptoCurrency")

    me = reddit.user.me()
    for comment in me.comments.new(limit=None):
        if comment.created_utc < datetime.datetime.utcnow().timestamp() - 24*60*60:
            break
        if comment.score <= 0:
            logger.info(f'Deleting comment with score {comment.score}: {comment.body[:60]}...')
            comment.delete()

    for submission in subreddit.stream.submissions():
        timestamp = datetime.datetime.now().time()
        start = datetime.time(13)
        end = datetime.time(23)
        if DEBUG:
            logger.info("Processing submission")
            process_submission(submission)
            sleep(randint(5, 10))
        else:
            if start <= timestamp <= end:
                if r.exists(submission.id):
                    logger.warning("Submission already processed")
                    continue
                elif submission.link_flair_text in ["Comedy", "Advice"]:
                    logger.warning("Submission has banned flair")
                    continue
                elif re.search('safemoon', submission.title):
                    logger.warning("Submission has banned words")
                    continue
                else:
                    r.set(submission.id, 1)
                    process_submission(submission)
                    sleep(randint(500, 600))
            else:
                logger.info("Outside of processing window")
                sleep(randint(500, 600))


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
            prompt = "Write a short reply in less than 30 words " \
                     "with one sentence to the comment '{}' in the " \
                     "context of the title '{}'. " \
                     "Do not be overly negative. Try to be humorous and cynical." \
                     "Do not start sentences with 'Oh', 'Wow', 'Great', and 'Well'." \
                     "Do not use proper punctuation." \
                     "Do not be sarcastic with words like 'Sherlock'." \
                     "Be conversational".format(comment, title)

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
                if DEBUG:
                    logger.info("Skipping reply")
                else:
                    top_level_comment.reply(reply)
                break


if __name__ == "__main__":
    main()
