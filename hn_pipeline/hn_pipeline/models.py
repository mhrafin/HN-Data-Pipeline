# SQLAlchemy ORM models
from sqlalchemy import CheckConstraint, func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime, Integer, String
from sqlalchemy_utils import URLType


class Base(DeclarativeBase):
    pass


class Story(Base):
    __tablename__ = "stories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hn_id = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    url = Column(URLType, unique=True, nullable=False)
    domain = Column(String, nullable=True)
    points = Column(Integer, nullable=True)
    submitted_by = Column(String, nullable=True)
    submitted_time = Column(DateTime, nullable=False)
    comment_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())

    __table_args__ = (CheckConstraint("points >= 0", name="check_points_non_negative"),)


class StoryDedupLog(Base):
    __tablename__ = "story_dedup_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hn_id = Column(String, nullable=False)
    url = Column(URLType, nullable=False)
    title = Column(String, nullable=False)
    crawl_timestamp = Column(DateTime, nullable=False, default=func.now())
