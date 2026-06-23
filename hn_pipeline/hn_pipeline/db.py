# Database engine/session management
from sqlalchemy import create_engine
from scrapy.settings import Settings
from sqlalchemy.orm import sessionmaker

engine = create_engine(Settings.get("DATABASE_URL"), echo=True, future=True)

Session = sessionmaker(bind=engine)


def init_db():
    from .models import Base

    Base.metadata.create_all(engine)
