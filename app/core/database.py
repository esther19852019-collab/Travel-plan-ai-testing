from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/travel_planner"

engine = create_engine(
    DATABASE_URL,
    echo=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

        