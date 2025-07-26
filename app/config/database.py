
from sqlalchemy import create_engine
from app.utils.enviroment import settings
from sqlalchemy.orm import sessionmaker, declarative_base

# Configuración síncrona
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=True,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
