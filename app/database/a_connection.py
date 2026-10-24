"""
Módulo de conexión nativa a MongoDB (sin Docker) siguiendo la estructura de ORM.
"""
import os
from pathlib import Path
from typing import Generator
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database

# Cargar variables de entorno
a_base_dir = Path(__file__).resolve().parent.parent.parent
a_env_path = a_base_dir / ".env"
if a_env_path.exists():
    load_dotenv(dotenv_path=a_env_path)
else:
    load_dotenv()

# Configuración de MongoDB nativo local
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "bd_gastronomia")

# Cliente global de MongoDB
a_mongo_client: MongoClient = MongoClient(
    f"mongodb://{MONGO_HOST}:{MONGO_PORT}/",
    serverSelectionTimeoutMS=5000,
)

# Base de datos central del proyecto
a_mongo_db: Database = a_mongo_client[MONGO_DATABASE]


def a_get_db() -> Generator[Database, None, None]:
    """Generador de acceso a la base de datos MongoDB para inyección de dependencias (igual a get_db en ORM)."""
    yield a_mongo_db


def a_obtener_siguiente_id(a_db: Database, a_coleccion: str) -> int:
    """Genera identificadores numéricos autoincrementales secuenciales simulando PK."""
    a_contador = a_db["contadores"].find_one_and_update(
        {"_id": a_coleccion},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=True,
    )
    return int(a_contador["seq"])
