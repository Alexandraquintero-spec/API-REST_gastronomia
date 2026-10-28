from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.a_comun import A_EstadoGeneral


class A_CategoriaBase(BaseModel):
    nombre: str = Field(..., max_length=60, description="Nombre de la categoría (único)")
    descripcion: Optional[str] = Field(None, max_length=200, description="Descripción")
    estado: A_EstadoGeneral = Field("ACTIVO", description="Estado de la categoría")


class A_CategoriaCreate(A_CategoriaBase):
    pass


class A_CategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=60)
    descripcion: Optional[str] = Field(None, max_length=200)
    estado: Optional[A_EstadoGeneral] = None


class A_CategoriaResponse(A_CategoriaBase):
    id_categoria: int
    model_config = ConfigDict(from_attributes=True)
