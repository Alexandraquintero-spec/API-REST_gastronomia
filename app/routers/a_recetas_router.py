from typing import Any, Dict, List
from fastapi import APIRouter, Depends, status
from pymongo.database import Database
from app.core.a_security import a_requerir_roles
from app.database.a_connection import a_get_db
from app.schemas.a_schemas import A_RecetaCreate, A_RecetaResponse, A_RecetaUpdate
from app.controllers import a_controllers

a_recetas_router = APIRouter(
    prefix="/recetas",
    tags=["Recetas (Fichas Técnicas)"],
    dependencies=[Depends(a_requerir_roles(["ADMIN", "COCINERO"]))],
)


@a_recetas_router.get(
    "",
    response_model=List[A_RecetaResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar recetas",
    description="Retorna todas las relaciones producto-insumo registradas en las fichas técnicas (ADMIN, COCINERO).",
    responses={
        200: {"description": "Lista de fichas técnicas"},
    },
)
def a_listar_recetas(
    a_db: Database = Depends(a_get_db),
) -> List[Dict[str, Any]]:
    return a_controllers.a_listar_recetas(a_db)


@a_recetas_router.get(
    "/{id}",
    response_model=A_RecetaResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener receta por ID",
    description="Retorna el detalle de una relación de receta por su ID numérico.",
    responses={
        200: {"description": "Receta encontrada"},
        404: {"description": "Receta no encontrada"},
    },
)
def a_obtener_receta(
    id: int,
    a_db: Database = Depends(a_get_db),
) -> Dict[str, Any]:
    return a_controllers.a_obtener_receta(a_db, id)


@a_recetas_router.post(
    "",
    response_model=A_RecetaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear ítem de receta",
    description="Asocia un insumo y cantidad a un producto gastronómico.",
    responses={
        201: {"description": "Ítem de receta creado"},
        404: {"description": "Producto o insumo no existe"},
    },
)
def a_crear_receta(
    a_datos: A_RecetaCreate,
    a_db: Database = Depends(a_get_db),
) -> Dict[str, Any]:
    return a_controllers.a_crear_receta(a_db, a_datos)


@a_recetas_router.put(
    "/{id}",
    response_model=A_RecetaResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar ítem de receta",
    description="Actualiza la cantidad o el insumo de una receta existente.",
    responses={
        200: {"description": "Receta actualizada"},
        404: {"description": "Receta no encontrada"},
    },
)
def a_actualizar_receta(
    id: int,
    a_datos: A_RecetaUpdate,
    a_db: Database = Depends(a_get_db),
) -> Dict[str, Any]:
    return a_controllers.a_actualizar_receta(a_db, id, a_datos)


@a_recetas_router.delete(
    "/{id}",
    response_model=Dict[str, str],
    status_code=status.HTTP_200_OK,
    summary="Eliminar ítem de receta",
    description="Elimina la asociación entre un insumo y un producto.",
    responses={
        200: {"description": "Receta eliminada"},
        404: {"description": "Receta no encontrada"},
    },
)
def a_eliminar_receta(
    id: int,
    a_db: Database = Depends(a_get_db),
) -> Dict[str, str]:
    return a_controllers.a_eliminar_receta(a_db, id)
