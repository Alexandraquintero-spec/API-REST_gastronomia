from typing import Literal, Optional
from pydantic import BaseModel

A_EstadoGeneral = Literal["ACTIVO", "INACTIVO"]

# Formato de fecha YYYY-MM-DD
A_PATRON_FECHA = r"^\d{4}-\d{2}-\d{2}$"


class A_MensajeResponse(BaseModel):
    """Respuesta estándar para operaciones de eliminación."""
    mensaje: str
    tipo_borrado: Optional[Literal["FISICO", "LOGICO"]] = None
