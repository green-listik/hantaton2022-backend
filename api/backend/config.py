import os

def _get_env(name: str) -> str:
    val = os.getenv(name)
    if val is None:
        raise RuntimeError(f"`{name} is not set`")
    return val

SECRET_KEY_JWT = _get_env("SECRET_KEY_JWT")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(_get_env("ACCESS_TOKEN_EXPIRE_MINUTES"))
