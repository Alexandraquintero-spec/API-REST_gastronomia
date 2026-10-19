from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.a_config import a_settings

# Creación del motor de base de datos MySQL con PyMySQL
a_engine = create_engine(
    a_settings.a_mysql_url,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Fábrica de sesiones ORM
a_session_maker = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=a_engine,
)

# Base declarativa de modelos SQLAlchemy
A_Base = declarative_base()


def a_obtener_db_mysql() -> Generator[Session, None, None]:
    """Generador de sesión de base de datos MySQL para inyección de dependencias."""
    a_db = a_session_maker()
    try:
        yield a_db
    except Exception:
        a_db.rollback()
        raise
    finally:
        a_db.close()
