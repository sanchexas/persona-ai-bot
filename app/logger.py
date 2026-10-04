import logging
import sys
import os

def setup_logger():
    logger = logging.getLogger("persona_bot")
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    is_debug = int(os.getenv("IS_DEBUG", 0))
    console_handler.setLevel(logging.DEBUG if is_debug == 1 else logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger

logger = setup_logger()