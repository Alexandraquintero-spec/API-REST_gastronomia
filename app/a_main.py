from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.a_auth_router import a_auth_router
from app.routers.a_usuarios_router import a_usuarios_router
from app.routers.a_categorias_router import a_categorias_router
from app.routers.a_productos_router import a_productos_router
from app.routers.a_insumos_router import a_insumos_router
from app.routers.a_recetas_router import a_recetas_router
from app.routers.a_proveedores_router import a_proveedores_router
from app.routers.a_compras_router import a_compras_router
from app.routers.a_clientes_router import a_clientes_router
from app.routers.a_pedidos_router import a_pedidos_router
from app.routers.a_reportes_router import a_reportes_router
from app.routers.a_calificaciones_router import a_calificaciones_router

# Punto de entrada principal FastAPI según instructivo EA4
app = FastAPI(
    title="API REST Unidad Productiva de Gastronomía - SENA CGDSS",
    description=(
        "API REST centralizada para la gestión de productos, recetas, insumos, proveedores, "
        "compras, clientes, pedidos y calificaciones en MongoDB. Cumple con los requerimientos "
        "funcionales RF01-RF12 y reglas de negocio RN01-RN06 del instructivo EA4 (Ficha 3312744)."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusión de enrutadores con prefijo /api/v1
a_prefijo_api = "/api/v1"
app.include_router(a_auth_router, prefix=a_prefijo_api)
app.include_router(a_usuarios_router, prefix=a_prefijo_api)
app.include_router(a_categorias_router, prefix=a_prefijo_api)
app.include_router(a_productos_router, prefix=a_prefijo_api)
app.include_router(a_insumos_router, prefix=a_prefijo_api)
app.include_router(a_recetas_router, prefix=a_prefijo_api)
app.include_router(a_proveedores_router, prefix=a_prefijo_api)
app.include_router(a_compras_router, prefix=a_prefijo_api)
app.include_router(a_clientes_router, prefix=a_prefijo_api)
app.include_router(a_pedidos_router, prefix=a_prefijo_api)
app.include_router(a_reportes_router, prefix=a_prefijo_api)
app.include_router(a_calificaciones_router, prefix=a_prefijo_api)


@app.get("/", tags=["General"], summary="Ruta raíz de bienvenida y estado del servicio")
def a_raiz():
    """Ruta raíz de bienvenida que indica el estado activo de la API."""
    return {
        "mensaje": "Bienvenido a la API REST de la Unidad Productiva de Gastronomía SENA CGDSS",
        "version": "1.0.0",
        "documentacion": "/docs",
        "redoc": "/redoc",
        "estado": "ACTIVO",
    }
