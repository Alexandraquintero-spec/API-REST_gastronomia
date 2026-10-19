import os
from pathlib import Path
from dotenv import load_dotenv

# Localizar archivo .env
a_base_dir = Path(__file__).resolve().parent.parent.parent
a_env_path = a_base_dir / ".env"
if a_env_path.exists():
    load_dotenv(dotenv_path=a_env_path)
else:
    load_dotenv()


class A_Settings:
    """Clase de configuración central de la aplicación."""

    def __init__(self):
        # MySQL
        self.a_mysql_host: str = os.getenv("MYSQL_HOST", "localhost")
        self.a_mysql_port: int = int(os.getenv("MYSQL_PORT", "3306"))
        self.a_mysql_database: str = os.getenv("MYSQL_DATABASE", "bd_gastronomia")
        self.a_mysql_user: str = os.getenv("MYSQL_USER", "usr_gastronomia")
        self.a_mysql_password: str = os.getenv("MYSQL_PASSWORD", "GastronomiaPass2026*")

        # MongoDB
        self.a_mongo_host: str = os.getenv("MONGO_HOST", "localhost")
        self.a_mongo_port: int = int(os.getenv("MONGO_PORT", "27017"))
        self.a_mongo_database: str = os.getenv("MONGO_DATABASE", "bd_gastronomia_nosql")

        # JWT Security
        self.a_jwt_secret: str = os.getenv(
            "JWT_SECRET", "supersecretgastronomiakey2026jwtsecrettokenadso3312744"
        )
        self.a_jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
        self.a_jwt_expire_minutes: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120")
        )

        # Timezone
        self.a_tz: str = os.getenv("TZ", "America/Bogota")

    @property
    def a_mysql_url(self) -> str:
        """Genera la URL de conexión para SQLAlchemy con PyMySQL."""
        return (
            f"mysql+pymysql://{self.a_mysql_user}:{self.a_mysql_password}@"
            f"{self.a_mysql_host}:{self.a_mysql_port}/{self.a_mysql_database}?charset=utf8mb4"
        )

    @property
    def a_mongo_url(self) -> str:
        """Genera la URI de conexión para PyMongo."""
        return f"mongodb://{self.a_mongo_host}:{self.a_mongo_port}/"


a_settings = A_Settings()


def a_obtener_configuracion() -> A_Settings:
    """Retorna la instancia global de configuración."""
    return a_settings
