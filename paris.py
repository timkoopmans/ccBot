import logging

# Define emoji icons for each log level
LOG_ICONS = {
    'DEBUG': '🐞',
    'INFO': 'ℹ️',
    'WARNING': '⚠️',
    'ERROR': '🚨',
    'CRITICAL': '💥',
}


# Create a custom formatter that includes the emoji icon for the log level
class EmojiFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        if levelname in LOG_ICONS:
            levelname = LOG_ICONS[levelname]
        record.levelname = levelname
        return super().format(record)


# Create a custom logger that uses the emoji formatter
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(EmojiFormatter('%(levelname)s %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)
