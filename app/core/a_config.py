import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Localizar archivo .env en la raíz del proyecto
a_base_dir = Path(__file__).resolve().parent.parent.parent
a_env_path = a_base_dir / ".env"
if a_env_path.exists():
    load_dotenv(dotenv_path=a_env_path)
else:
    load_dotenv()

# Zona horaria America/Bogota (UTC-5, sin horario de verano)
A_ZONA_BOGOTA = timezone(timedelta(hours=-5), name="America/Bogota")


class A_Settings:
    """Clase de configuración central de la aplicación (lee variables del .env)."""

    def __init__(self):
        # MongoDB local (servicio nativo de Windows, sin Docker)
        self.a_mongo_host: str = os.getenv("MONGO_HOST", "localhost")
        self.a_mongo_port: int = int(os.getenv("MONGO_PORT", "27017"))
        self.a_mongo_database: str = os.getenv("MONGO_DATABASE", "bd_gastronomia_nosql")
        # Usuario de mínimos privilegios (database/03_dcl_usuario_api.py); vacío = sin autenticación
        self.a_mongo_user: str = os.getenv("MONGO_USER", "")
        self.a_mongo_password: str = os.getenv("MONGO_PASSWORD", "")

        # Seguridad JWT: la clave secreta solo se toma del .env
        a_secret = os.getenv("JWT_SECRET")
        if not a_secret:
            raise RuntimeError("Falta la variable JWT_SECRET en el archivo .env")
        self.a_jwt_secret: str = a_secret
        self.a_jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
        self.a_jwt_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

    @property
    def a_mongo_url(self) -> str:
        """Genera la URI de conexión para PyMongo (con credenciales si están en el .env)."""
        if self.a_mongo_user:
            a_credenciales = f"{quote_plus(self.a_mongo_user)}:{quote_plus(self.a_mongo_password)}@"
            return (
                f"mongodb://{a_credenciales}{self.a_mongo_host}:{self.a_mongo_port}/"
                f"?authSource={self.a_mongo_database}"
            )
        return f"mongodb://{self.a_mongo_host}:{self.a_mongo_port}/"


a_settings = A_Settings()


def a_fecha_actual() -> str:
    """Fecha y hora actual de Bogotá en formato ISO (YYYY-MM-DDTHH:MM:SS)."""
    return datetime.now(A_ZONA_BOGOTA).replace(tzinfo=None).isoformat(timespec="seconds")
