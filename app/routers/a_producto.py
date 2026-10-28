from typing import List
from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from app.controllers.a_producto import (
    a_actualizar_producto,
    a_calcular_costo_produccion,
    a_crear_producto,
    a_eliminar_producto,
    a_listar_productos,
    a_obtener_producto,
    a_productos_por_categoria,
)
from app.controllers.a_receta import a_receta_por_producto
from app.core.a_security import a_obtener_usuario_actual, a_requerir_roles
from app.database.a_connection import a_get_db
from app.schemas.a_comun import A_MensajeResponse
from app.schemas.a_producto import (
    A_ProductoCostoResponse,
    A_ProductoCreate,
    A_ProductoResponse,
    A_ProductoUpdate,
)
from app.schemas.a_receta import A_RecetaResponse

# Consulta: cualquier usuario autenticado. Escritura: solo ADMIN.
a_router = APIRouter(prefix="/api/v1/productos", tags=["Productos"])
a_solo_admin = [Depends(a_requerir_roles(["ADMIN"]))]
a_autenticado = [Depends(a_obtener_usuario_actual)]


@a_router.get("", response_model=List[A_ProductoResponse], summary="Listar productos", dependencies=a_autenticado)
def a_listar(a_db: Database = Depends(a_get_db)):
    return a_listar_productos(a_db=a_db)


@a_router.get(
    "/categoria/{id_categoria}",
    response_model=List[A_ProductoResponse],
    summary="Productos de una categoría",
    responses={404: {"description": "Categoría no encontrada"}},
    dependencies=a_autenticado,
)
def a_por_categoria(id_categoria: int, a_db: Database = Depends(a_get_db)):
    return a_productos_por_categoria(a_db=a_db, a_id_categoria=id_categoria)


@a_router.get(
    "/{id}/receta",
    response_model=List[A_RecetaResponse],
    summary="Receta (ficha técnica) de un producto",
    description="Insumos y cantidades de la receta del producto (RF05).",
    responses={404: {"description": "Producto no encontrado"}},
    dependencies=a_autenticado,
)
def a_receta(id: int, a_db: Database = Depends(a_get_db)):
    return a_receta_por_producto(a_db=a_db, a_id_producto=id)


@a_router.get(
    "/{id}/costo",
    response_model=A_ProductoCostoResponse,
    summary="Costo de producción y margen",
    description="Costo = Σ (cantidad × costo_unitario) de la receta y margen frente al precio de venta (RF06). ADMIN y COCINERO.",
    responses={404: {"description": "Producto no encontrado"}},
    dependencies=[Depends(a_requerir_roles(["ADMIN", "COCINERO"]))],
)
def a_costo(id: int, a_db: Database = Depends(a_get_db)):
    return a_calcular_costo_produccion(a_db=a_db, a_id_producto=id)


@a_router.get(
    "/{id}",
    response_model=A_ProductoResponse,
    summary="Obtener producto por ID",
    responses={404: {"description": "Producto no encontrado"}},
    dependencies=a_autenticado,
)
def a_obtener(id: int, a_db: Database = Depends(a_get_db)):
    return a_obtener_producto(a_db=a_db, a_id_producto=id)


@a_router.post(
    "",
    response_model=A_ProductoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto (ADMIN)",
    responses={404: {"description": "Categoría no existe"}, 409: {"description": "Código duplicado"}},
    dependencies=a_solo_admin,
)
def a_crear(a_datos: A_ProductoCreate, a_db: Database = Depends(a_get_db)):
    return a_crear_producto(a_db=a_db, a_datos=a_datos)


@a_router.put(
    "/{id}",
    response_model=A_ProductoResponse,
    summary="Actualizar producto (ADMIN)",
    responses={404: {"description": "Producto o categoría no encontrados"}, 409: {"description": "Código duplicado"}},
    dependencies=a_solo_admin,
)
def a_actualizar(id: int, a_datos: A_ProductoUpdate, a_db: Database = Depends(a_get_db)):
    return a_actualizar_producto(a_db=a_db, a_id_producto=id, a_datos=a_datos)


@a_router.delete(
    "/{id}",
    response_model=A_MensajeResponse,
    summary="Eliminar producto (ADMIN)",
    description="RN04: si tiene recetas o pedidos se cambia a INACTIVO (borrado lógico).",
    responses={404: {"description": "Producto no encontrado"}},
    dependencies=a_solo_admin,
)
def a_eliminar(id: int, a_db: Database = Depends(a_get_db)):
    return a_eliminar_producto(a_db=a_db, a_id_producto=id)
