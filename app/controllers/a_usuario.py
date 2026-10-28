from typing import Any, Dict, List
from fastapi import HTTPException, status
from pymongo.database import Database
from app.core.a_security import a_generar_hash_password
from app.database.a_connection import a_limpiar_documento, a_obtener_siguiente_id
from app.models.a_usuario import A_Usuario
from app.schemas.a_usuario import A_UsuarioCreate, A_UsuarioUpdate


def a_listar_usuarios(a_db: Database) -> List[Dict[str, Any]]:
    return [a_limpiar_documento(a_u) for a_u in A_Usuario.a_tabla(a_db).find()]


def a_obtener_usuario(a_db: Database, a_id_usuario: int) -> Dict[str, Any]:
    a_usuario = A_Usuario.a_tabla(a_db).find_one({"id_usuario": a_id_usuario})
    if not a_usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return a_limpiar_documento(a_usuario)


def a_crear_usuario(a_db: Database, a_datos: A_UsuarioCreate) -> Dict[str, Any]:
    a_col = A_Usuario.a_tabla(a_db)
    if a_col.find_one({"correo": a_datos.correo}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El correo ya se encuentra registrado")
    if a_col.find_one({"identificacion": a_datos.identificacion}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El documento ya se encuentra registrado")

    a_nuevo_doc = a_datos.model_dump()
    a_nuevo_doc["id_usuario"] = a_obtener_siguiente_id(a_db, A_Usuario.a_coleccion)
    a_nuevo_doc["password"] = a_generar_hash_password(a_datos.password)  # RN06: bcrypt
    a_col.insert_one(a_nuevo_doc)
    return a_limpiar_documento(a_nuevo_doc)


def a_actualizar_usuario(a_db: Database, a_id_usuario: int, a_datos: A_UsuarioUpdate) -> Dict[str, Any]:
    a_col = A_Usuario.a_tabla(a_db)
    a_usuario = a_obtener_usuario(a_db, a_id_usuario)

    a_cambios = a_datos.model_dump(exclude_none=True)
    if "correo" in a_cambios and a_cambios["correo"] != a_usuario["correo"]:
        if a_col.find_one({"correo": a_cambios["correo"]}):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El correo ya se encuentra registrado")
    if "identificacion" in a_cambios and a_cambios["identificacion"] != a_usuario["identificacion"]:
        if a_col.find_one({"identificacion": a_cambios["identificacion"]}):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El documento ya se encuentra registrado")
    if "password" in a_cambios:
        a_cambios["password"] = a_generar_hash_password(a_cambios["password"])  # RN06

    if a_cambios:
        a_col.update_one({"id_usuario": a_id_usuario}, {"$set": a_cambios})
    return a_obtener_usuario(a_db, a_id_usuario)


def a_eliminar_usuario(a_db: Database, a_id_usuario: int, a_id_usuario_actual: int) -> Dict[str, str]:
    a_obtener_usuario(a_db, a_id_usuario)
    if a_id_usuario == a_id_usuario_actual:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No puede eliminar su propio usuario")
    A_Usuario.a_tabla(a_db).delete_one({"id_usuario": a_id_usuario})
    return {"mensaje": f"Usuario con ID {a_id_usuario} eliminado exitosamente", "tipo_borrado": "FISICO"}
