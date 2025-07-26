
from sqlalchemy import create_engine
from app.utils.enviroment import settings
from sqlalchemy.orm import sessionmaker, declarative_base

# Configuración síncrona
engine = create_engine(settings.database_url,
                       pool_pre_ping=True,     # ✔️ Verifica que la conexión está viva antes de usarla
                       pool_recycle=280,       # ✔️ Cierra y recrea conexiones inactivas después de N segundos
                       pool_size=10,           # Tamaño del pool
                       max_overflow=20,)
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
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
