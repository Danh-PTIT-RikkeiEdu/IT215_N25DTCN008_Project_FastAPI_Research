from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings

class Base(DeclarativeBase):
    pass

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)

LocalSession = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine
)

def get_db():
    db = LocalSession()
    try: 
        yield db
    finally:
        db.close()