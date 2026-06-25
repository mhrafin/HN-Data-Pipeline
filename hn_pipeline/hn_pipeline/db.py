# Database engine/session management
from sqlalchemy import create_engine
from scrapy.settings import Settings
from sqlalchemy.orm import sessionmaker
from scrapy.utils.project import get_project_settings

settings = get_project_settings()

engine = create_engine(settings.get("DATABASE_URL"), echo=True, future=True)

Session = sessionmaker(bind=engine)


def init_db():
    from .models import Base

    Base.metadata.create_all(engine)
