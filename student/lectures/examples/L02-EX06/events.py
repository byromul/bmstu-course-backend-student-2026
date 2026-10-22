"""События одного учебного хода без чтения файлов проекта."""


def play_turn(logger):
    scene_id = "SCN007"
    hp = 6
    logger.debug("Исходные данные: hp=%s", hp)
    logger.info("Ход начат: scene_id=%s", scene_id)
    damage = 2
    hp -= damage
    logger.info("Ход завершён: damage=%s hp=%s", damage, hp)
    if hp < 5:
        logger.warning("Мало здоровья: hp=%s", hp)
    return hp
