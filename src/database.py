from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.config import POSTGRES_CREDS


url = URL.create(**POSTGRES_CREDS)

engine = create_engine(url)
Session = sessionmaker(bind=engine)
db = Session()
