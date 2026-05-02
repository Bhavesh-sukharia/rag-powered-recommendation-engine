from collections.abc import Generator

from db.session import SessionLocal


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user() -> dict[str, str]:
    return {"user_id": "demo-user", "role": "demo"}