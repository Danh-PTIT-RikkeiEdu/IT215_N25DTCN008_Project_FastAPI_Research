from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine

class Base(DeclarativeBase):
    pass

DATABASE_URL = "mysql+pymysql://root:1234@localhost:3306/research_management"

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