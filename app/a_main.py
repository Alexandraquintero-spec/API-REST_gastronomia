import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Permite ejecutar este archivo directamente (botón ▶ de VS Code o "python app/a_main.py")
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Si se ejecuta con el Python global (sin el entorno virtual) faltan librerías: se explica cómo arrancar bien
try:
    import jwt  # noqa: F401
    import pymongo  # noqa: F401
except ModuleNotFoundError as a_error:
    raise SystemExit(
        f"\nFalta la librería '{a_error.name}': se está usando el Python global ({sys.executable}).\n"
        "Arranque la API con el entorno virtual del proyecto, de una de estas formas:\n"
        "  PowerShell: .\\venv\\Scripts\\Activate.ps1   y luego   uvicorn app.a_main:app --port 3000 --reload\n"
        "  CMD:        venv\\Scripts\\activate.bat     y luego   uvicorn app.a_main:app --port 3000 --reload\n"
    ) from None

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models  # noqa: F401  (registra todos los modelos en A_Base)
from app.database.a_connection import a_mongo_db, a_verificar_conexion
from app.database.a_seeder import a_inicializar_base_datos
from app.routers.a_auth import a_router as a_auth_router
from app.routers.a_usuario import a_router as a_usuario_router
from app.routers.a_categoria import a_router as a_categoria_router
from app.routers.a_producto import a_router as a_producto_router
from app.routers.a_insumo import a_router as a_insumo_router
from app.routers.a_receta import a_router as a_receta_router
from app.routers.a_proveedor import a_router as a_proveedor_router
from app.routers.a_compra import a_router as a_compra_router
from app.routers.a_cliente import a_router as a_cliente_router
from app.routers.a_pedido import a_router as a_pedido_router
from app.routers.a_reporte import a_router as a_reporte_router
from app.routers.a_calificacion import a_router as a_calificacion_router


@asynccontextmanager
async def lifespan(a_app: FastAPI):
    # Equivale a Base.metadata.create_all() del ORM: conexión, índices únicos y datos iniciales si está vacía
    a_verificar_conexion()
    a_inicializar_base_datos(a_mongo_db)
    yield


app = FastAPI(
    title="API REST Gastronomía - SENA CGDSS",
    description=(
        "API REST de la Unidad Productiva de Gastronomía (Ficha 3312744 - EA4).\n\n"
        "**Cómo probar:** 1) Ejecute `POST /api/v1/auth/login` con un usuario de prueba. "
        "2) Copie el `access_token`. 3) Pulse **Authorize** y péguelo. "
        "Todos los endpoints son privados excepto el login."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(a_auth_router)
app.include_router(a_usuario_router)
app.include_router(a_categoria_router)
app.include_router(a_producto_router)
app.include_router(a_insumo_router)
app.include_router(a_receta_router)
app.include_router(a_proveedor_router)
app.include_router(a_compra_router)
app.include_router(a_cliente_router)
app.include_router(a_pedido_router)
app.include_router(a_reporte_router)
app.include_router(a_calificacion_router)


@app.get("/", tags=["General"], summary="Estado del servicio")
def a_raiz():
    return {
        "mensaje": "API REST de la Unidad Productiva de Gastronomía SENA CGDSS",
        "documentacion": "/docs",
        "estado": "ACTIVO",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.a_main:app", host="127.0.0.1", port=3000, reload=True, reload_dirs=[str(Path(__file__).resolve().parent)]
    )
