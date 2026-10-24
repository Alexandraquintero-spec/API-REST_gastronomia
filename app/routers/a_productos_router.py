from typing import Any, Dict, List
from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from app.core.a_security import a_obtener_usuario_actual, a_requerir_roles
from app.database.a_connection import a_get_db
from app.schemas.a_schemas import (
    A_ProductoCostoResponse,
    A_ProductoCreate,
    A_ProductoResponse,
    A_ProductoUpdate,
    A_RecetaResponse,
)
from app.controllers.a_controllers import (
    a_actualizar_producto,
    a_calcular_costo_produccion,
    a_crear_producto,
    a_eliminar_producto,
    a_listar_productos,
    a_obtener_producto,
    a_productos_por_categoria,
    a_receta_por_producto,
)

a_productos_router = APIRouter(prefix="/productos", tags=["Productos"])


@a_productos_router.get(
    "",
    response_model=List[A_ProductoResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar productos",
    description="Obtiene el catálogo completo de productos gastronómicos (disponible para todos los usuarios autenticados).",
)
def a_listar_productos_route(
    a_usuario: Dict[str, Any] = Depends(a_obtener_usuario_actual),
    a_db: Database = Depends(a_get_db),
) -> List[A_ProductoResponse]:
    return a_listar_productos(db=a_db)


@a_productos_router.get(
    "/categoria/{id_categoria}",
    response_model=List[A_ProductoResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar productos por categoría",
    description="Filtra y retorna todos los productos pertenecientes a una categoría específica.",
)
def a_productos_por_categoria_route(
    id_categoria: int,
    a_usuario: Dict[str, Any] = Depends(a_obtener_usuario_actual),
    a_db: Database = Depends(a_get_db),
) -> List[A_ProductoResponse]:
    return a_productos_por_categoria(db=a_db, id_categoria=id_categoria)


@a_productos_router.get(
    "/{id}/receta",
    response_model=List[A_RecetaResponse],
    status_code=status.HTTP_200_OK,
    summary="Consultar receta (ficha técnica) de un producto",
    description="Retorna la lista de insumos y cantidades que componen la receta del producto.",
)
def a_receta_de_producto_route(
    id: int,
    a_usuario: Dict[str, Any] = Depends(a_obtener_usuario_actual),
    a_db: Database = Depends(a_get_db),
) -> List[A_RecetaResponse]:
    return a_receta_por_producto(db=a_db, id_producto=id)


@a_productos_router.get(
    "/{id}/costo",
    response_model=A_ProductoCostoResponse,
    status_code=status.HTTP_200_OK,
    summary="Calcular costo de producción y margen de ganancia",
    description="Calcula el costo total (Σ cantidad × costo_unitario) y el margen frente al precio de venta (RF06). Permitido para ADMIN y COCINERO.",
)
def a_costo_de_producto_route(
    id: int,
    a_usuario: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN", "COCINERO"])),
    a_db: Database = Depends(a_get_db),
) -> A_ProductoCostoResponse:
    return a_calcular_costo_produccion(db=a_db, id_producto=id)


@a_productos_router.get(
    "/{id}",
    response_model=A_ProductoResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener producto por ID",
    description="Retorna los datos detallados de un producto por su identificador.",
)
def a_obtener_producto_route(
    id: int,
    a_usuario: Dict[str, Any] = Depends(a_obtener_usuario_actual),
    a_db: Database = Depends(a_get_db),
) -> A_ProductoResponse:
    return a_obtener_producto(db=a_db, id_producto=id)


@a_productos_router.post(
    "",
    response_model=A_ProductoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto",
    description="Registra un nuevo producto gastronómico (solo ADMIN).",
)
def a_crear_producto_route(
    a_datos: A_ProductoCreate,
    a_admin: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN"])),
    a_db: Database = Depends(a_get_db),
) -> A_ProductoResponse:
    return a_crear_producto(db=a_db, datos=a_datos)


@a_productos_router.put(
    "/{id}",
    response_model=A_ProductoResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar producto",
    description="Actualiza la información de un producto (solo ADMIN).",
)
def a_actualizar_producto_route(
    id: int,
    a_datos: A_ProductoUpdate,
    a_admin: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN"])),
    a_db: Database = Depends(a_get_db),
) -> A_ProductoResponse:
    return a_actualizar_producto(db=a_db, id_producto=id, datos=a_datos)


@a_productos_router.delete(
    "/{id}",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Eliminar producto",
    description="Elimina un producto. Si tiene movimientos asociados (recetas o pedidos), aplica borrado lógico a INACTIVO según la RN04 (solo ADMIN).",
)
def a_eliminar_producto_route(
    id: int,
    a_admin: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN"])),
    a_db: Database = Depends(a_get_db),
) -> Dict[str, str]:
    return a_eliminar_producto(db=a_db, id_producto=id)
