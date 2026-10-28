"""
Conexión a MongoDB local (equivalente a database/connection.py del proyecto ORM).

- a_mongo_db        -> base de datos (equivale al engine/SessionLocal del ORM)
- A_Base            -> clase base de los modelos (equivale a declarative_base())
- a_get_db()        -> dependencia de FastAPI (equivale a get_db())
"""
from typing import Any, Dict, Generator, List, Optional, Type
from pymongo import MongoClient, ReturnDocument
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError
from app.core.a_config import a_settings

# Cliente global de MongoDB
a_mongo_client: MongoClient = MongoClient(a_settings.a_mongo_url, serverSelectionTimeoutMS=5000)

# Base de datos del proyecto
a_mongo_db: Database = a_mongo_client[a_settings.a_mongo_database]


class A_Base:
    """
    Clase base de todos los modelos (colecciones).
    Cada modelo define su colección, su llave numérica y sus campos únicos.
    """

    a_coleccion: str = ""
    a_llave: str = ""
    a_campos_unicos: List[str] = []
    a_modelos: List[Type["A_Base"]] = []

    def __init_subclass__(cls, **a_kwargs):
        super().__init_subclass__(**a_kwargs)
        A_Base.a_modelos.append(cls)

    @classmethod
    def a_tabla(cls, a_db: Database) -> Collection:
        """Retorna la colección de MongoDB asociada al modelo."""
        return a_db[cls.a_coleccion]

    @classmethod
    def a_crear_indices(cls, a_db: Database) -> None:
        """Crea índices únicos para todos los modelos (equivale a Base.metadata.create_all)."""
        for a_modelo in cls.a_modelos:
            a_col = a_modelo.a_tabla(a_db)
            if a_modelo.a_llave and a_modelo.a_llave != "_id":
                a_col.create_index(a_modelo.a_llave, unique=True)
            for a_campo in a_modelo.a_campos_unicos:
                a_col.create_index(a_campo, unique=True)


def a_verificar_conexion() -> None:
    """Comprueba MongoDB al arrancar y explica en español los fallos más comunes."""
    a_servidor = f"{a_settings.a_mongo_host}:{a_settings.a_mongo_port}"
    try:
        a_mongo_client.admin.command("ping")
        A_Base.a_crear_indices(a_mongo_db)
    except ServerSelectionTimeoutError:
        raise RuntimeError(
            f"MongoDB no responde en {a_servidor}. Inicie el servicio en PowerShell como administrador: "
            "Start-Service MongoDB"
        ) from None
    except OperationFailure as a_error:
        if a_error.code == 18:
            raise RuntimeError(
                "MongoDB rechazó el usuario o la contraseña. Revise MONGO_USER y MONGO_PASSWORD en el archivo .env"
            ) from None
        if a_error.code == 14031:
            raise RuntimeError(
                "El disco está lleno: MongoDB necesita al menos 500 MB libres para trabajar. Libere espacio en el disco C:"
            ) from None
        raise


def a_get_db() -> Generator[Database, None, None]:
    """Dependencia de FastAPI que entrega la base de datos MongoDB."""
    yield a_mongo_db


def a_obtener_siguiente_id(a_db: Database, a_coleccion: str) -> int:
    """Genera un identificador numérico autoincremental (simula el AUTO_INCREMENT de SQL)."""
    a_contador = a_db["contadores"].find_one_and_update(
        {"_id": a_coleccion},
        {"$inc": {"seq": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return int(a_contador["seq"])


def a_limpiar_documento(a_doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Quita el _id interno de MongoDB para que Pydantic pueda serializar el documento."""
    if a_doc is None:
        return None
    a_resultado = dict(a_doc)
    a_resultado.pop("_id", None)
    return a_resultado
