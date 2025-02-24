from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
import os

DATABASE_URL = "sqlite:///../database.db"
engine = create_engine(DATABASE_URL,echo=True)

Session = sessionmaker(bind=engine,autocommit=False,autoflush=False)


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()



