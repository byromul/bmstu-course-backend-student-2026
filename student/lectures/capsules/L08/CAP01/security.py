TOKENS = {"opaque-irina": "irina", "opaque-anton": "anton"}


def authenticate(header):
    scheme, separator, token = header.partition(" ")
    if scheme != "Bearer" or not separator or not token or token not in TOKENS:
        return None
    return TOKENS[token]


def read_scene(header, scene, visible_ids):
    user = authenticate(header)
    if user is None:
        return 401
    if scene["id"] not in visible_ids:
        return 404
    if scene["owner"] != user:
        return 403
    return 200
