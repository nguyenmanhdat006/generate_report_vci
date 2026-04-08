from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.base import Base
import app.models.report 

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=5,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base.metadata.create_all(bind=engine)
