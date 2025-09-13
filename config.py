from os import getenv

public_key_file = getenv("PUBLIC_KEY")
private_key_file = getenv("PRIVATE_KEY")

if public_key_file is None or private_key_file is None:
    PUBLIC_KEY = None
    PRIVATE_KEY = None
else:
    with open(public_key_file) as f:
        PUBLIC_KEY = f.read()
    with open(private_key_file) as f:
        PRIVATE_KEY = f.read()

DB_URL = getenv("DB_URL", "sqlite+aiosqlite:///./test.db")
