import logging

from events import play_turn

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s %(name)s: %(message)s",
    filename="game.log",
    encoding="utf-8",
    filemode="a",
)
logger = logging.getLogger("quest")
play_turn(logger)
