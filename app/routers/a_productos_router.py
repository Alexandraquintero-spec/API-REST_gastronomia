from typing import Any, Dict, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.a_security import a_obtener_usuario_actual, a_requerir_roles
from app.database.a_conexion_mysql import a_obtener_db_mysql
from app.schemas.a_schemas import (
    A_ProductoCostoResponse,
    A_ProductoCreate,
    A_ProductoResponse,
    A_ProductoUpdate,
    A_RecetaResponse,
)
from app.services.a_services import A_ProductoService, A_RecetaService

a_productos_router = APIRouter(prefix="/productos", tags=["Productos"])


@a_productos_router.get(
    "",
    response_model=List[A_ProductoResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar productos",
    description="Obtiene el catálogo completo de productos gastronómicos (disponible para todos los usuarios autenticados).",
    responses={
        200: {"description": "Lista de productos"},
        401: {"description": "Token ausente o inválido"},
    },
)
def a_listar_productos(
    a_usuario: Dict[str, Any] = Depends(a_obtener_usuario_actual),
    a_db: Session = Depends(a_obtener_db_mysql),
) -> List[A_ProductoResponse]:
    a_servicio = A_ProductoService(a_db)
    return a_servicio.a_listar_productos()


@a_productos_router.get(
    "/categoria/{id_categoria}",
    response_model=List[A_ProductoResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar productos por categoría",
    description="Filtra y retorna todos los productos pertenecientes a una categoría específica.",
    responses={
        200: {"description": "Productos filtrados"},
        404: {"description": "Categoría no encontrada"},
    },
)
def a_productos_por_categoria(
    id_categoria: int,
    a_usuario: Dict[str, Any] = Depends(a_obtener_usuario_actual),
    a_db: Session = Depends(a_obtener_db_mysql),
) -> List[A_ProductoResponse]:
    a_servicio = A_ProductoService(a_db)
    return a_servicio.a_listar_por_categoria(id_categoria)


@a_productos_router.get(
    "/{id}/receta",
    response_model=List[A_RecetaResponse],
    status_code=status.HTTP_200_OK,
    summary="Consultar receta (ficha técnica) de un producto",
    description="Retorna la lista de insumos y cantidades que componen la receta del producto.",
    responses={
        200: {"description": "Ficha técnica del producto"},
        404: {"description": "Producto no encontrado"},
    },
)
def a_receta_de_producto(
    id: int,
    a_usuario: Dict[str, Any] = Depends(a_obtener_usuario_actual),
    a_db: Session = Depends(a_obtener_db_mysql),
) -> List[A_RecetaResponse]:
    a_servicio = A_RecetaService(a_db)
    return a_servicio.a_listar_por_producto(id)


@a_productos_router.get(
    "/{id}/costo",
    response_model=A_ProductoCostoResponse,
    status_code=status.HTTP_200_OK,
    summary="Calcular costo de producción y margen de ganancia",
    description="Calcula el costo total (Σ cantidad × costo_unitario) y el margen frente al precio de venta (RF06). Permitido para ADMIN y COCINERO.",
    responses={
        200: {"description": "Cálculo financiero y de producción exitoso"},
        403: {"description": "Rol no autorizado"},
        404: {"description": "Producto no encontrado"},
    },
)
def a_costo_de_producto(
    id: int,
    a_usuario: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN", "COCINERO"])),
    a_db: Session = Depends(a_obtener_db_mysql),
) -> A_ProductoCostoResponse:
    a_servicio = A_ProductoService(a_db)
    return a_servicio.a_calcular_costo_produccion(id)


@a_productos_router.get(
    "/{id}",
    response_model=A_ProductoResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener producto por ID",
    description="Retorna los datos detallados de un producto por su identificador.",
    responses={
        200: {"description": "Producto encontrado"},
        404: {"description": "Producto no encontrado"},
    },
)
def a_obtener_producto(
    id: int,
    a_usuario: Dict[str, Any] = Depends(a_obtener_usuario_actual),
    a_db: Session = Depends(a_obtener_db_mysql),
) -> A_ProductoResponse:
    a_servicio = A_ProductoService(a_db)
    return a_servicio.a_obtener_por_id(id)


@a_productos_router.post(
    "",
    response_model=A_ProductoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto",
    description="Registra un nuevo producto gastronómico (solo ADMIN).",
    responses={
        201: {"description": "Producto creado"},
        403: {"description": "Permisos insuficientes"},
        409: {"description": "Código de producto ya existente"},
    },
)
def a_crear_producto(
    a_datos: A_ProductoCreate,
    a_admin: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN"])),
    a_db: Session = Depends(a_obtener_db_mysql),
) -> A_ProductoResponse:
    a_servicio = A_ProductoService(a_db)
    return a_servicio.a_crear_producto(a_datos)


@a_productos_router.put(
    "/{id}",
    response_model=A_ProductoResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar producto",
    description="Actualiza la información de un producto (solo ADMIN).",
    responses={
        200: {"description": "Producto actualizado"},
        404: {"description": "Producto no encontrado"},
        409: {"description": "Código duplicado"},
    },
)
def a_actualizar_producto(
    id: int,
    a_datos: A_ProductoUpdate,
    a_admin: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN"])),
    a_db: Session = Depends(a_obtener_db_mysql),
) -> A_ProductoResponse:
    a_servicio = A_ProductoService(a_db)
    return a_servicio.a_actualizar_producto(id, a_datos)


@a_productos_router.delete(
    "/{id}",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Eliminar producto",
    description="Elimina un producto. Si tiene movimientos asociados (recetas o pedidos), aplica borrado lógico a INACTIVO según la RN04 (solo ADMIN).",
    responses={
        200: {"description": "Producto eliminado o desactivado según movimientos"},
        404: {"description": "Producto no encontrado"},
    },
)
def a_eliminar_producto(
    id: int,
    a_admin: Dict[str, Any] = Depends(a_requerir_roles(["ADMIN"])),
    a_db: Session = Depends(a_obtener_db_mysql),
) -> Dict[str, str]:
    a_servicio = A_ProductoService(a_db)
    return a_servicio.a_eliminar_producto(id)
