from contextlib import contextmanager
from typing import Generator, Optional
from sqlalchemy.orm import Session
from app.infrastructure.database import SessionLocal


class BasePostgresRepository:
    def __init__(self, db: Optional[Session] = None):
        self._db = db

    @contextmanager
    def _get_db(self) -> Generator[Session, None, None]:
        if self._db is not None:
            yield self._db
        else:
            session: Session = SessionLocal()
            try:
                yield session
            finally:
                session.close()