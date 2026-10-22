import logging

from events import play_turn

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("quest")
play_turn(logger)
