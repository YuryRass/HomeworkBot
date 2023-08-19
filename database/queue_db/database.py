from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import settings


Base = declarative_base()
engine = create_engine(settings.QUEUE_DB_URL)

Session = sessionmaker(bind=engine)


def create_db():
    Base.metadata.create_all(bind=engine)