from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import load_config, Config


config: Config = load_config()
Base = declarative_base()
engine = create_engine(f'sqlite:///{config.db.queue_db_name}.sqlite')

Session = sessionmaker(bind=engine)


def create_db():
    Base.metadata.create_all(bind=engine)