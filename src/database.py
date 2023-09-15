from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text

from src.config import POSTGRES_CREDS


url = URL.create(**POSTGRES_CREDS)

engine = create_engine(url)
Session = sessionmaker(bind=engine)
session = Session()


def get_db_version():
    query = text("SELECT version();")
    result = session.execute(query)
    return result.fetchone()[0]
