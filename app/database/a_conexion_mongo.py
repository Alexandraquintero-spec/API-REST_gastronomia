from typing import Generator
from pymongo import MongoClient
from pymongo.database import Database
from app.core.a_config import a_settings

# Cliente global de MongoDB
a_mongo_client: MongoClient = MongoClient(
    a_settings.a_mongo_url,
    serverSelectionTimeoutMS=5000,
)

# Base de datos MongoDB
a_mongo_db: Database = a_mongo_client[a_settings.a_mongo_database]


def a_obtener_db_mongo() -> Generator[Database, None, None]:
    """Generador de acceso a la base de datos MongoDB para inyección de dependencias."""
    yield a_mongo_db
