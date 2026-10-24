"""
Capa de controladores (Controllers) para la API Gastronomía.
Sigue el patrón de controladores visto en la carpeta ORM, operando directamente sobre MongoDB nativo (sin Docker).
Implementa todas las reglas de negocio RN01..RN06 y requerimientos funcionales RF01..RF12.
"""
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from bson import ObjectId
from fastapi import HTTPException, status
from pymongo.database import Database

from app.core.a_security import (
    a_crear_token_acceso,
    a_generar_hash_password,
    a_verificar_password,
)
from app.database.a_connection import a_obtener_siguiente_id
from app.models.a_models import A_Colecciones
from app.schemas.a_schemas import (
    A_CategoriaCreate,
    A_CategoriaUpdate,
    A_ClienteCreate,
    A_ClienteUpdate,
    A_CompraCreate,
    A_InsumoCreate,
    A_InsumoUpdate,
    A_LoginRequest,
    A_PedidoCreate,
    A_ProductoCreate,
    A_ProductoUpdate,
    A_ProveedorCreate,
    A_ProveedorUpdate,
    A_RecetaCreate,
    A_RecetaUpdate,
    A_TokenResponse,
    A_UsuarioCreate,
    A_UsuarioUpdate,
    A_CalificacionCreate,
    A_CalificacionUpdate,
)


def _quitar_mongo_id(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Limpia el campo _id de MongoDB para serialización Pydantic."""
    if doc is None:
        return None
    d = dict(doc)
    d.pop("_id", None)
    return d


# ============================================================
# 1. Controlador de Autenticación (RF01, RN06)
# ============================================================
def a_autenticar_usuario(db: Database, datos_login: A_LoginRequest) -> A_TokenResponse:
    col = db[A_Colecciones.USUARIOS]
    usuario = col.find_one({"correo": datos_login.correo})
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not a_verificar_password(datos_login.password, usuario["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if usuario.get("estado") != "ACTIVO":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario se encuentra inactivo en el sistema",
        )

    token_data = {
        "sub": str(usuario["id_usuario"]),
        "id_usuario": usuario["id_usuario"],
        "correo": usuario["correo"],
        "rol": usuario["rol"],
        "nombres": f"{usuario['nombres']} {usuario['apellidos']}",
    }
    token = a_crear_token_acceso(token_data)
    return A_TokenResponse(
        access_token=token,
        token_type="bearer",
        rol=usuario["rol"],
        id_usuario=usuario["id_usuario"],
        nombres=f"{usuario['nombres']} {usuario['apellidos']}",
    )


# ============================================================
# 2. Controlador de Usuarios (RF02, RN06)
# ============================================================
def a_listar_usuarios(db: Database) -> List[Dict[str, Any]]:
    col = db[A_Colecciones.USUARIOS]
    usuarios = list(col.find())
    return [_quitar_mongo_id(u) for u in usuarios]


def a_obtener_usuario(db: Database, id_usuario: int) -> Dict[str, Any]:
    col = db[A_Colecciones.USUARIOS]
    usuario = col.find_one({"id_usuario": id_usuario})
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return _quitar_mongo_id(usuario)


def a_crear_usuario(db: Database, datos: A_UsuarioCreate) -> Dict[str, Any]:
    col = db[A_Colecciones.USUARIOS]
    if col.find_one({"correo": datos.correo}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El correo ya se encuentra registrado")
    if col.find_one({"identificacion": datos.identificacion}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El documento ya se encuentra registrado")

    nuevo_id = a_obtener_siguiente_id(db, A_Colecciones.USUARIOS)
    nuevo_doc = datos.model_dump()
    nuevo_doc["id_usuario"] = nuevo_id
    nuevo_doc["password"] = a_generar_hash_password(datos.password)  # RN06: bcrypt

    col.insert_one(nuevo_doc)
    return _quitar_mongo_id(nuevo_doc)


def a_actualizar_usuario(db: Database, id_usuario: int, datos: A_UsuarioUpdate) -> Dict[str, Any]:
    col = db[A_Colecciones.USUARIOS]
    usuario = col.find_one({"id_usuario": id_usuario})
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

    cambios = {k: v for k, v in datos.model_dump().items() if v is not None}
    if "correo" in cambios and cambios["correo"] != usuario["correo"]:
        if col.find_one({"correo": cambios["correo"]}):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El correo ya se encuentra registrado")
    if "identificacion" in cambios and cambios["identificacion"] != usuario["identificacion"]:
        if col.find_one({"identificacion": cambios["identificacion"]}):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El documento ya se encuentra registrado")
    if "password" in cambios:
        cambios["password"] = a_generar_hash_password(cambios["password"])

    if cambios:
        col.update_one({"id_usuario": id_usuario}, {"$set": cambios})
    return a_obtener_usuario(db, id_usuario)


def a_eliminar_usuario(db: Database, id_usuario: int) -> Dict[str, str]:
    col = db[A_Colecciones.USUARIOS]
    usuario = col.find_one({"id_usuario": id_usuario})
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    col.delete_one({"id_usuario": id_usuario})
    return {"mensaje": f"Usuario con ID {id_usuario} eliminado exitosamente"}


# ============================================================
# 3. Controlador de Categorías (RF03)
# ============================================================
def a_listar_categorias(db: Database) -> List[Dict[str, Any]]:
    col = db[A_Colecciones.CATEGORIAS]
    return [_quitar_mongo_id(c) for c in col.find()]


def a_obtener_categoria(db: Database, id_categoria: int) -> Dict[str, Any]:
    col = db[A_Colecciones.CATEGORIAS]
    cat = col.find_one({"id_categoria": id_categoria})
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada")
    return _quitar_mongo_id(cat)


def a_crear_categoria(db: Database, datos: A_CategoriaCreate) -> Dict[str, Any]:
    col = db[A_Colecciones.CATEGORIAS]
    if col.find_one({"nombre": datos.nombre}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe una categoría con ese nombre")
    nuevo_id = a_obtener_siguiente_id(db, A_Colecciones.CATEGORIAS)
    nuevo_doc = datos.model_dump()
    nuevo_doc["id_categoria"] = nuevo_id
    col.insert_one(nuevo_doc)
    return _quitar_mongo_id(nuevo_doc)


def a_actualizar_categoria(db: Database, id_categoria: int, datos: A_CategoriaUpdate) -> Dict[str, Any]:
    col = db[A_Colecciones.CATEGORIAS]
    cat = col.find_one({"id_categoria": id_categoria})
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada")

    cambios = {k: v for k, v in datos.model_dump().items() if v is not None}
    if "nombre" in cambios and cambios["nombre"] != cat["nombre"]:
        if col.find_one({"nombre": cambios["nombre"]}):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe una categoría con ese nombre")
    if cambios:
        col.update_one({"id_categoria": id_categoria}, {"$set": cambios})
    return a_obtener_categoria(db, id_categoria)


def a_eliminar_categoria(db: Database, id_categoria: int) -> Dict[str, str]:
    col = db[A_Colecciones.CATEGORIAS]
    cat = col.find_one({"id_categoria": id_categoria})
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada")
    # Verificar si contiene productos asociados
    if db[A_Colecciones.PRODUCTOS].find_one({"id_categoria": id_categoria}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar la categoría porque contiene productos asociados",
        )
    col.delete_one({"id_categoria": id_categoria})
    return {"mensaje": f"Categoría con ID {id_categoria} eliminada exitosamente"}


# ============================================================
# 4. Controlador de Productos (RF04, RF06, RN04)
# ============================================================
def a_listar_productos(db: Database) -> List[Dict[str, Any]]:
    col = db[A_Colecciones.PRODUCTOS]
    return [_quitar_mongo_id(p) for p in col.find()]


def a_obtener_producto(db: Database, id_producto: int) -> Dict[str, Any]:
    col = db[A_Colecciones.PRODUCTOS]
    prod = col.find_one({"id_producto": id_producto})
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return _quitar_mongo_id(prod)


def a_productos_por_categoria(db: Database, id_categoria: int) -> List[Dict[str, Any]]:
    a_obtener_categoria(db, id_categoria)
    col = db[A_Colecciones.PRODUCTOS]
    return [_quitar_mongo_id(p) for p in col.find({"id_categoria": id_categoria})]


def a_crear_producto(db: Database, datos: A_ProductoCreate) -> Dict[str, Any]:
    col = db[A_Colecciones.PRODUCTOS]
    if col.find_one({"codigo": datos.codigo}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El código de producto ya existe")
    if not db[A_Colecciones.CATEGORIAS].find_one({"id_categoria": datos.id_categoria}):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La categoría especificada no existe")

    nuevo_id = a_obtener_siguiente_id(db, A_Colecciones.PRODUCTOS)
    nuevo_doc = datos.model_dump()
    nuevo_doc["id_producto"] = nuevo_id
    col.insert_one(nuevo_doc)
    return _quitar_mongo_id(nuevo_doc)


def a_actualizar_producto(db: Database, id_producto: int, datos: A_ProductoUpdate) -> Dict[str, Any]:
    col = db[A_Colecciones.PRODUCTOS]
    prod = col.find_one({"id_producto": id_producto})
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    cambios = {k: v for k, v in datos.model_dump().items() if v is not None}
    if "codigo" in cambios and cambios["codigo"] != prod["codigo"]:
        if col.find_one({"codigo": cambios["codigo"]}):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El código de producto ya existe")
    if "id_categoria" in cambios:
        if not db[A_Colecciones.CATEGORIAS].find_one({"id_categoria": cambios["id_categoria"]}):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La categoría especificada no existe")
    if cambios:
        col.update_one({"id_producto": id_producto}, {"$set": cambios})
    return a_obtener_producto(db, id_producto)


def a_eliminar_producto(db: Database, id_producto: int) -> Dict[str, str]:
    """RN04: Borrado lógico a INACTIVO si tiene movimientos (recetas o pedidos); físico si no."""
    col = db[A_Colecciones.PRODUCTOS]
    prod = col.find_one({"id_producto": id_producto})
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

    tiene_receta = db[A_Colecciones.RECETAS].find_one({"id_producto": id_producto}) is not None
    tiene_pedidos = db[A_Colecciones.PEDIDOS].find_one({"detalles.id_producto": id_producto}) is not None

    if tiene_receta or tiene_pedidos:
        col.update_one({"id_producto": id_producto}, {"$set": {"estado": "INACTIVO"}})
        return {
            "mensaje": f"Producto con ID {id_producto} tiene movimientos asociados. Se aplicó borrado lógico a estado INACTIVO (RN04)",
            "tipo_borrado": "LOGICO",
        }
    else:
        col.delete_one({"id_producto": id_producto})
        return {
            "mensaje": f"Producto con ID {id_producto} eliminado físicamente exitosamente",
            "tipo_borrado": "FISICO",
        }


def a_calcular_costo_produccion(db: Database, id_producto: int) -> Dict[str, Any]:
    """RF06: Costo = Σ cantidad × costo_unitario y margen frente al precio de venta."""
    prod = a_obtener_producto(db, id_producto)
    recetas = list(db[A_Colecciones.RECETAS].find({"id_producto": id_producto}))

    costo_total = 0.0
    recetas_detalladas = []

    for r in recetas:
        insumo = db[A_Colecciones.INSUMOS].find_one({"id_insumo": r["id_insumo"]})
        costo_u = float(insumo["costo_unitario"]) if insumo else 0.0
        costo_linea = float(r["cantidad"]) * costo_u
        costo_total += costo_linea
        recetas_detalladas.append(
            {
                "id_receta": r["id_receta"],
                "id_producto": r["id_producto"],
                "id_insumo": r["id_insumo"],
                "cantidad": float(r["cantidad"]),
                "nombre_insumo": insumo["nombre"] if insumo else "",
                "unidad_medida": insumo["unidad_medida"] if insumo else "",
                "costo_unitario": costo_u,
            }
        )

    precio_venta = float(prod["precio_venta"])
    margen_ganancia = precio_venta - costo_total
    porcentaje = (margen_ganancia / precio_venta * 100.0) if precio_venta > 0 else 0.0

    return {
        "id_producto": prod["id_producto"],
        "codigo": prod["codigo"],
        "nombre": prod["nombre"],
        "precio_venta": precio_venta,
        "costo_produccion": round(costo_total, 2),
        "margen_ganancia": round(margen_ganancia, 2),
        "porcentaje_margen": round(porcentaje, 2),
        "receta": recetas_detalladas,
    }


# ============================================================
# 5. Controlador de Insumos (RF07, RN04)
# ============================================================
def a_listar_insumos(db: Database) -> List[Dict[str, Any]]:
    col = db[A_Colecciones.INSUMOS]
    return [_quitar_mongo_id(i) for i in col.find()]


def a_obtener_insumo(db: Database, id_insumo: int) -> Dict[str, Any]:
    col = db[A_Colecciones.INSUMOS]
    ins = col.find_one({"id_insumo": id_insumo})
    if not ins:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insumo no encontrado")
    return _quitar_mongo_id(ins)


def a_insumos_stock_bajo(db: Database) -> List[Dict[str, Any]]:
    """RF07: Insumos con stock_actual <= stock_minimo."""
    col = db[A_Colecciones.INSUMOS]
    # En MongoDB usamos $expr para comparar dos campos en el mismo documento
    insumos = list(col.find({"$expr": {"$lte": ["$stock_actual", "$stock_minimo"]}}))
    return [_quitar_mongo_id(i) for i in insumos]


def a_insumos_por_vencer(db: Database, dias: int = 7) -> List[Dict[str, Any]]:
    """RF07: Insumos que vencen en los próximos N días."""
    col = db[A_Colecciones.INSUMOS]
    hoy = date.today().isoformat()
    limite = (date.today() + timedelta(days=dias)).isoformat()
    insumos = list(
        col.find(
            {
                "fecha_vencimiento": {"$ne": None, "$gte": hoy, "$lte": limite}
            }
        )
    )
    return [_quitar_mongo_id(i) for i in insumos]


def a_crear_insumo(db: Database, datos: A_InsumoCreate) -> Dict[str, Any]:
    col = db[A_Colecciones.INSUMOS]
    if col.find_one({"nombre": datos.nombre}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un insumo con ese nombre")
    nuevo_id = a_obtener_siguiente_id(db, A_Colecciones.INSUMOS)
    nuevo_doc = datos.model_dump()
    nuevo_doc["id_insumo"] = nuevo_id
    col.insert_one(nuevo_doc)
    return _quitar_mongo_id(nuevo_doc)


def a_actualizar_insumo(db: Database, id_insumo: int, datos: A_InsumoUpdate) -> Dict[str, Any]:
    col = db[A_Colecciones.INSUMOS]
    ins = col.find_one({"id_insumo": id_insumo})
    if not ins:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insumo no encontrado")

    cambios = {k: v for k, v in datos.model_dump().items() if v is not None}
    if "nombre" in cambios and cambios["nombre"] != ins["nombre"]:
        if col.find_one({"nombre": cambios["nombre"]}):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un insumo con ese nombre")
    if cambios:
        col.update_one({"id_insumo": id_insumo}, {"$set": cambios})
    return a_obtener_insumo(db, id_insumo)


def a_eliminar_insumo(db: Database, id_insumo: int) -> Dict[str, str]:
    """RN04: Borrado lógico si tiene recetas o compras asociadas; físico si no."""
    col = db[A_Colecciones.INSUMOS]
    ins = col.find_one({"id_insumo": id_insumo})
    if not ins:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insumo no encontrado")

    tiene_receta = db[A_Colecciones.RECETAS].find_one({"id_insumo": id_insumo}) is not None
    tiene_compras = db[A_Colecciones.COMPRAS].find_one({"detalles.id_insumo": id_insumo}) is not None

    if tiene_receta or tiene_compras:
        col.update_one({"id_insumo": id_insumo}, {"$set": {"estado": "INACTIVO"}})
        return {
            "mensaje": f"Insumo con ID {id_insumo} tiene movimientos en recetas o compras. Se cambió a estado INACTIVO (RN04)",
            "tipo_borrado": "LOGICO",
        }
    else:
        col.delete_one({"id_insumo": id_insumo})
        return {
            "mensaje": f"Insumo con ID {id_insumo} eliminado físicamente exitosamente",
            "tipo_borrado": "FISICO",
        }


# ============================================================
# 6. Controlador de Recetas (RF05)
# ============================================================
def a_listar_recetas(db: Database) -> List[Dict[str, Any]]:
    col = db[A_Colecciones.RECETAS]
    recetas = list(col.find())
    res = []
    for r in recetas:
        ins = db[A_Colecciones.INSUMOS].find_one({"id_insumo": r["id_insumo"]})
        d = _quitar_mongo_id(r)
        d["nombre_insumo"] = ins["nombre"] if ins else ""
        d["unidad_medida"] = ins["unidad_medida"] if ins else ""
        d["costo_unitario"] = ins["costo_unitario"] if ins else 0.0
        res.append(d)
    return res


def a_obtener_receta(db: Database, id_receta: int) -> Dict[str, Any]:
    col = db[A_Colecciones.RECETAS]
    r = col.find_one({"id_receta": id_receta})
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receta no encontrada")
    ins = db[A_Colecciones.INSUMOS].find_one({"id_insumo": r["id_insumo"]})
    d = _quitar_mongo_id(r)
    d["nombre_insumo"] = ins["nombre"] if ins else ""
    d["unidad_medida"] = ins["unidad_medida"] if ins else ""
    d["costo_unitario"] = ins["costo_unitario"] if ins else 0.0
    return d


def a_receta_por_producto(db: Database, id_producto: int) -> List[Dict[str, Any]]:
    if not db[A_Colecciones.PRODUCTOS].find_one({"id_producto": id_producto}):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    col = db[A_Colecciones.RECETAS]
    recetas = list(col.find({"id_producto": id_producto}))
    res = []
    for r in recetas:
        ins = db[A_Colecciones.INSUMOS].find_one({"id_insumo": r["id_insumo"]})
        d = _quitar_mongo_id(r)
        d["nombre_insumo"] = ins["nombre"] if ins else ""
        d["unidad_medida"] = ins["unidad_medida"] if ins else ""
        d["costo_unitario"] = ins["costo_unitario"] if ins else 0.0
        res.append(d)
    return res


def a_crear_receta(db: Database, datos: A_RecetaCreate) -> Dict[str, Any]:
    if not db[A_Colecciones.PRODUCTOS].find_one({"id_producto": datos.id_producto}):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    if not db[A_Colecciones.INSUMOS].find_one({"id_insumo": datos.id_insumo}):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insumo no encontrado")

    nuevo_id = a_obtener_siguiente_id(db, A_Colecciones.RECETAS)
    nuevo_doc = datos.model_dump()
    nuevo_doc["id_receta"] = nuevo_id
    db[A_Colecciones.RECETAS].insert_one(nuevo_doc)
    return a_obtener_receta(db, nuevo_id)


def a_actualizar_receta(db: Database, id_receta: int, datos: A_RecetaUpdate) -> Dict[str, Any]:
    col = db[A_Colecciones.RECETAS]
    r = col.find_one({"id_receta": id_receta})
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receta no encontrada")
    cambios = {k: v for k, v in datos.model_dump().items() if v is not None}
    if "id_producto" in cambios:
        if not db[A_Colecciones.PRODUCTOS].find_one({"id_producto": cambios["id_producto"]}):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    if "id_insumo" in cambios:
        if not db[A_Colecciones.INSUMOS].find_one({"id_insumo": cambios["id_insumo"]}):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insumo no encontrado")
    if cambios:
        col.update_one({"id_receta": id_receta}, {"$set": cambios})
    return a_obtener_receta(db, id_receta)


def a_eliminar_receta(db: Database, id_receta: int) -> Dict[str, str]:
    col = db[A_Colecciones.RECETAS]
    r = col.find_one({"id_receta": id_receta})
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receta no encontrada")
    col.delete_one({"id_receta": id_receta})
    return {"mensaje": f"Ficha técnica/receta con ID {id_receta} eliminada exitosamente"}


# ============================================================
# 7. Controlador de Proveedores (RF08, RN04)
# ============================================================
def a_listar_proveedores(db: Database) -> List[Dict[str, Any]]:
    col = db[A_Colecciones.PROVEEDORES]
    return [_quitar_mongo_id(p) for p in col.find()]


def a_obtener_proveedor(db: Database, id_proveedor: int) -> Dict[str, Any]:
    col = db[A_Colecciones.PROVEEDORES]
    prov = col.find_one({"id_proveedor": id_proveedor})
    if not prov:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado")
    return _quitar_mongo_id(prov)


def a_crear_proveedor(db: Database, datos: A_ProveedorCreate) -> Dict[str, Any]:
    col = db[A_Colecciones.PROVEEDORES]
    if col.find_one({"nit": datos.nit}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El NIT de proveedor ya existe")
    nuevo_id = a_obtener_siguiente_id(db, A_Colecciones.PROVEEDORES)
    nuevo_doc = datos.model_dump()
    nuevo_doc["id_proveedor"] = nuevo_id
    col.insert_one(nuevo_doc)
    return _quitar_mongo_id(nuevo_doc)


def a_actualizar_proveedor(db: Database, id_proveedor: int, datos: A_ProveedorUpdate) -> Dict[str, Any]:
    col = db[A_Colecciones.PROVEEDORES]
    prov = col.find_one({"id_proveedor": id_proveedor})
    if not prov:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado")
    cambios = {k: v for k, v in datos.model_dump().items() if v is not None}
    if "nit" in cambios and cambios["nit"] != prov["nit"]:
        if col.find_one({"nit": cambios["nit"]}):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El NIT de proveedor ya existe")
    if cambios:
        col.update_one({"id_proveedor": id_proveedor}, {"$set": cambios})
    return a_obtener_proveedor(db, id_proveedor)


def a_eliminar_proveedor(db: Database, id_proveedor: int) -> Dict[str, str]:
    """RN04: Borrado lógico si tiene compras registradas; físico si no."""
    col = db[A_Colecciones.PROVEEDORES]
    prov = col.find_one({"id_proveedor": id_proveedor})
    if not prov:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado")
    tiene_compras = db[A_Colecciones.COMPRAS].find_one({"id_proveedor": id_proveedor}) is not None
    if tiene_compras:
        col.update_one({"id_proveedor": id_proveedor}, {"$set": {"estado": "INACTIVO"}})
        return {
            "mensaje": f"Proveedor con ID {id_proveedor} tiene compras registradas. Se cambió a estado INACTIVO (RN04)",
            "tipo_borrado": "LOGICO",
        }
    else:
        col.delete_one({"id_proveedor": id_proveedor})
        return {
            "mensaje": f"Proveedor con ID {id_proveedor} eliminado físicamente exitosamente",
            "tipo_borrado": "FISICO",
        }


# ============================================================
# 8. Controlador de Compras (RF08, RN02)
# ============================================================
def a_listar_compras(db: Database) -> List[Dict[str, Any]]:
    col = db[A_Colecciones.COMPRAS]
    return [_quitar_mongo_id(c) for c in col.find().sort("fecha_compra", -1)]


def a_obtener_compra(db: Database, id_compra: int) -> Dict[str, Any]:
    col = db[A_Colecciones.COMPRAS]
    cmp = col.find_one({"id_compra": id_compra})
    if not cmp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compra no encontrada")
    return _quitar_mongo_id(cmp)


def a_compras_por_proveedor(db: Database, id_proveedor: int) -> List[Dict[str, Any]]:
    a_obtener_proveedor(db, id_proveedor)
    col = db[A_Colecciones.COMPRAS]
    return [_quitar_mongo_id(c) for c in col.find({"id_proveedor": id_proveedor}).sort("fecha_compra", -1)]


def a_crear_compra(db: Database, datos: A_CompraCreate, id_usuario: int) -> Dict[str, Any]:
    """RN02: Al registrar compra, suma stock_actual y actualiza costo_unitario de cada insumo."""
    a_obtener_proveedor(db, datos.id_proveedor)
    col_insumos = db[A_Colecciones.INSUMOS]

    total = 0.0
    detalles_guardar = []
    detalle_id_base = 1

    for item in datos.detalles:
        ins = col_insumos.find_one({"id_insumo": item.id_insumo})
        if not ins:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Insumo con ID {item.id_insumo} no existe")

        subtotal = round(float(item.cantidad) * float(item.costo_unitario), 2)
        total += subtotal

        # RN02: Actualizar existencias y costo unitario
        nuevo_stock = float(ins.get("stock_actual", 0.0)) + float(item.cantidad)
        col_insumos.update_one(
            {"id_insumo": item.id_insumo},
            {"$set": {"stock_actual": nuevo_stock, "costo_unitario": float(item.costo_unitario)}}
        )

        detalles_guardar.append(
            {
                "id_detalle_compra": detalle_id_base,
                "id_insumo": item.id_insumo,
                "nombre_insumo": ins.get("nombre", ""),
                "cantidad": float(item.cantidad),
                "costo_unitario": float(item.costo_unitario),
                "subtotal": subtotal,
            }
        )
        detalle_id_base += 1

    nuevo_id = a_obtener_siguiente_id(db, A_Colecciones.COMPRAS)
    nueva_compra = {
        "id_compra": nuevo_id,
        "numero_factura": datos.numero_factura,
        "fecha_compra": datetime.now(timezone.utc).isoformat(),
        "id_proveedor": datos.id_proveedor,
        "id_usuario": id_usuario,
        "total": round(total, 2),
        "detalles": detalles_guardar,
    }

    db[A_Colecciones.COMPRAS].insert_one(nueva_compra)
    return _quitar_mongo_id(nueva_compra)


def a_actualizar_compra(db: Database, id_compra: int, datos: Dict[str, Any]) -> Dict[str, Any]:
    col = db[A_Colecciones.COMPRAS]
    cmp = col.find_one({"id_compra": id_compra})
    if not cmp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compra no encontrada")
    if "numero_factura" in datos:
        col.update_one({"id_compra": id_compra}, {"$set": {"numero_factura": datos["numero_factura"]}})
    return a_obtener_compra(db, id_compra)


def a_eliminar_compra(db: Database, id_compra: int) -> Dict[str, str]:
    col = db[A_Colecciones.COMPRAS]
    cmp = col.find_one({"id_compra": id_compra})
    if not cmp:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compra no encontrada")
    col.delete_one({"id_compra": id_compra})
    return {"mensaje": f"Compra con ID {id_compra} eliminada exitosamente"}


# ============================================================
# 9. Controlador de Clientes (RF09, RN04)
# ============================================================
def a_listar_clientes(db: Database) -> List[Dict[str, Any]]:
    col = db[A_Colecciones.CLIENTES]
    return [_quitar_mongo_id(c) for c in col.find()]


def a_obtener_cliente(db: Database, id_cliente: int) -> Dict[str, Any]:
    col = db[A_Colecciones.CLIENTES]
    cli = col.find_one({"id_cliente": id_cliente})
    if not cli:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    return _quitar_mongo_id(cli)


def a_crear_cliente(db: Database, datos: A_ClienteCreate) -> Dict[str, Any]:
    col = db[A_Colecciones.CLIENTES]
    if col.find_one({"identificacion": datos.identificacion}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El documento de identidad ya existe")
    nuevo_id = a_obtener_siguiente_id(db, A_Colecciones.CLIENTES)
    nuevo_doc = datos.model_dump()
    nuevo_doc["id_cliente"] = nuevo_id
    col.insert_one(nuevo_doc)
    return _quitar_mongo_id(nuevo_doc)


def a_actualizar_cliente(db: Database, id_cliente: int, datos: A_ClienteUpdate) -> Dict[str, Any]:
    col = db[A_Colecciones.CLIENTES]
    cli = col.find_one({"id_cliente": id_cliente})
    if not cli:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    cambios = {k: v for k, v in datos.model_dump().items() if v is not None}
    if "identificacion" in cambios and cambios["identificacion"] != cli["identificacion"]:
        if col.find_one({"identificacion": cambios["identificacion"]}):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El documento de identidad ya existe")
    if cambios:
        col.update_one({"id_cliente": id_cliente}, {"$set": cambios})
    return a_obtener_cliente(db, id_cliente)


def a_eliminar_cliente(db: Database, id_cliente: int) -> Dict[str, str]:
    """RN04: Borrado lógico a INACTIVO si tiene pedidos; físico si no."""
    col = db[A_Colecciones.CLIENTES]
    cli = col.find_one({"id_cliente": id_cliente})
    if not cli:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
    tiene_pedidos = db[A_Colecciones.PEDIDOS].find_one({"id_cliente": id_cliente}) is not None
    if tiene_pedidos:
        col.update_one({"id_cliente": id_cliente}, {"$set": {"estado": "INACTIVO"}})
        return {
            "mensaje": f"Cliente con ID {id_cliente} tiene pedidos registrados. Se cambió a estado INACTIVO (RN04)",
            "tipo_borrado": "LOGICO",
        }
    else:
        col.delete_one({"id_cliente": id_cliente})
        return {
            "mensaje": f"Cliente con ID {id_cliente} eliminado físicamente exitosamente",
            "tipo_borrado": "FISICO",
        }


# ============================================================
# 10. Controlador de Pedidos (RF10, RN01, RN03, RN05)
# ============================================================
def a_listar_pedidos(db: Database) -> List[Dict[str, Any]]:
    col = db[A_Colecciones.PEDIDOS]
    return [_quitar_mongo_id(p) for p in col.find().sort("fecha_pedido", -1)]


def a_obtener_pedido(db: Database, id_pedido: int) -> Dict[str, Any]:
    col = db[A_Colecciones.PEDIDOS]
    ped = col.find_one({"id_pedido": id_pedido})
    if not ped:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
    return _quitar_mongo_id(ped)


def a_pedidos_por_cliente(db: Database, id_cliente: int) -> List[Dict[str, Any]]:
    a_obtener_cliente(db, id_cliente)
    col = db[A_Colecciones.PEDIDOS]
    return [_quitar_mongo_id(p) for p in col.find({"id_cliente": id_cliente}).sort("fecha_pedido", -1)]


def a_pedidos_por_estado(db: Database, estado: str) -> List[Dict[str, Any]]:
    if estado not in ["PENDIENTE", "EN_PREPARACION", "ENTREGADO", "ANULADO"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Estado de pedido inválido")
    col = db[A_Colecciones.PEDIDOS]
    return [_quitar_mongo_id(p) for p in col.find({"estado": estado}).sort("fecha_pedido", -1)]


def a_crear_pedido(db: Database, datos: A_PedidoCreate, id_usuario: int) -> Dict[str, Any]:
    """RN01: subtotal = cantidad * precio_unitario y total = suma de subtotales calculado por la API."""
    a_obtener_cliente(db, datos.id_cliente)
    col_prods = db[A_Colecciones.PRODUCTOS]

    total = 0.0
    detalles_guardar = []
    det_id = 1

    for item in datos.detalles:
        prod = col_prods.find_one({"id_producto": item.id_producto})
        if not prod:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Producto con ID {item.id_producto} no encontrado")
        if prod.get("estado") != "DISPONIBLE":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"El producto '{prod['nombre']}' no se encuentra disponible (estado: {prod.get('estado')})",
            )

        # RN01: Precio tomado del producto, subtotal calculado por la API
        precio_u = float(prod["precio_venta"])
        subtotal = round(float(item.cantidad) * precio_u, 2)
        total += subtotal

        detalles_guardar.append(
            {
                "id_detalle": det_id,
                "id_producto": item.id_producto,
                "nombre_producto": prod["nombre"],
                "cantidad": item.cantidad,
                "precio_unitario": precio_u,
                "subtotal": subtotal,
            }
        )
        det_id += 1

    nuevo_id = a_obtener_siguiente_id(db, A_Colecciones.PEDIDOS)
    nuevo_pedido = {
        "id_pedido": nuevo_id,
        "fecha_pedido": datetime.now(timezone.utc).isoformat(),
        "id_cliente": datos.id_cliente,
        "id_usuario": id_usuario,
        "tipo_pedido": datos.tipo_pedido,
        "estado": "PENDIENTE",
        "total": round(total, 2),
        "observaciones": datos.observaciones,
        "detalles": detalles_guardar,
    }

    db[A_Colecciones.PEDIDOS].insert_one(nuevo_pedido)
    return _quitar_mongo_id(nuevo_pedido)


def a_cambiar_estado_pedido(db: Database, id_pedido: int, nuevo_estado: str) -> Dict[str, Any]:
    """RN03 (descuento de insumos o 409 si falta stock) y RN05 (no modificar pedidos entregados o anulados)."""
    col = db[A_Colecciones.PEDIDOS]
    ped = col.find_one({"id_pedido": id_pedido})
    if not ped:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")

    estado_actual = ped.get("estado")

    # RN05: Un pedido ENTREGADO o ANULADO no puede modificarse
    if estado_actual in ["ENTREGADO", "ANULADO"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Un pedido en estado '{estado_actual}' no puede modificarse (RN05)",
        )

    # Flujo de estados: PENDIENTE -> EN_PREPARACION o ANULADO; EN_PREPARACION -> ENTREGADO o ANULADO
    if estado_actual == "PENDIENTE" and nuevo_estado not in ["EN_PREPARACION", "ANULADO"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Transición no permitida: de PENDIENTE solo se puede pasar a EN_PREPARACION o ANULADO",
        )
    if estado_actual == "EN_PREPARACION" and nuevo_estado not in ["ENTREGADO", "ANULADO"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Transición no permitida: de EN_PREPARACION solo se puede pasar a ENTREGADO o ANULADO",
        )

    # RN03: Al pasar a ENTREGADO, descontar insumos según receta * cantidad
    if nuevo_estado == "ENTREGADO":
        insumos_necesarios: Dict[int, float] = {}
        for det in ped.get("detalles", []):
            recetas = list(db[A_Colecciones.RECETAS].find({"id_producto": det["id_producto"]}))
            for r in recetas:
                cant_necesaria = float(r["cantidad"]) * float(det["cantidad"])
                insumos_necesarios[r["id_insumo"]] = (
                    insumos_necesarios.get(r["id_insumo"], 0.0) + cant_necesaria
                )

        # 1. Validar existencias de todos los insumos
        col_ins = db[A_Colecciones.INSUMOS]
        for id_ins, cant_req in insumos_necesarios.items():
            ins = col_ins.find_one({"id_insumo": id_ins})
            stock_act = float(ins.get("stock_actual", 0.0)) if ins else 0.0
            if not ins or stock_act < cant_req:
                nombre_ins = ins.get("nombre") if ins else f"ID {id_ins}"
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Stock insuficiente para el insumo '{nombre_ins}'. Existencias: {stock_act}, Requerido: {cant_req} (RN03)",
                )

        # 2. Descontar inventario
        for id_ins, cant_req in insumos_necesarios.items():
            col_ins.update_one({"id_insumo": id_ins}, {"$inc": {"stock_actual": -cant_req}})

    col.update_one({"id_pedido": id_pedido}, {"$set": {"estado": nuevo_estado}})
    return a_obtener_pedido(db, id_pedido)


def a_actualizar_pedido(db: Database, id_pedido: int, datos: Dict[str, Any]) -> Dict[str, Any]:
    col = db[A_Colecciones.PEDIDOS]
    ped = col.find_one({"id_pedido": id_pedido})
    if not ped:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
    if ped.get("estado") in ["ENTREGADO", "ANULADO"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Un pedido en estado '{ped.get('estado')}' no puede modificarse (RN05)",
        )
    cambios = {}
    if "observaciones" in datos:
        cambios["observaciones"] = datos["observaciones"]
    if "tipo_pedido" in datos:
        cambios["tipo_pedido"] = datos["tipo_pedido"]
    if cambios:
        col.update_one({"id_pedido": id_pedido}, {"$set": cambios})
    return a_obtener_pedido(db, id_pedido)


def a_eliminar_pedido(db: Database, id_pedido: int) -> Dict[str, str]:
    col = db[A_Colecciones.PEDIDOS]
    ped = col.find_one({"id_pedido": id_pedido})
    if not ped:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
    if ped.get("estado") in ["ENTREGADO", "EN_PREPARACION"]:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No se puede eliminar un pedido en estado {ped.get('estado')}",
        )
    col.delete_one({"id_pedido": id_pedido})
    return {"mensaje": f"Pedido con ID {id_pedido} eliminado exitosamente"}


# ============================================================
# 11. Controlador de Reportes (RF11)
# ============================================================
def a_reporte_ventas(db: Database, desde: Optional[str] = None, hasta: Optional[str] = None) -> Dict[str, Any]:
    col = db[A_Colecciones.PEDIDOS]
    filtro: Dict[str, Any] = {"estado": "ENTREGADO"}

    if desde and hasta:
        filtro["fecha_pedido"] = {"$gte": desde, "$lte": hasta}
    elif desde:
        filtro["fecha_pedido"] = {"$gte": desde}
    elif hasta:
        filtro["fecha_pedido"] = {"$lte": hasta}

    pedidos = list(col.find(filtro))
    total_ventas = sum(float(p.get("total", 0.0)) for p in pedidos)

    return {
        "total_ventas": round(total_ventas, 2),
        "numero_pedidos": len(pedidos),
        "desde": desde,
        "hasta": hasta,
    }


def a_reporte_productos_mas_vendidos(db: Database, limite: int = 10) -> List[Dict[str, Any]]:
    col = db[A_Colecciones.PEDIDOS]
    pipeline = [
        {"$match": {"estado": "ENTREGADO"}},
        {"$unwind": "$detalles"},
        {
            "$group": {
                "_id": "$detalles.id_producto",
                "nombre": {"$first": "$detalles.nombre_producto"},
                "cantidad_vendida": {"$sum": "$detalles.cantidad"},
                "total_recaudado": {"$sum": "$detalles.subtotal"},
            }
        },
        {"$sort": {"cantidad_vendida": -1}},
        {"$limit": limite},
    ]
    res = list(col.aggregate(pipeline))
    return [
        {
            "id_producto": r["_id"],
            "nombre": r.get("nombre") or "",
            "cantidad_vendida": int(r["cantidad_vendida"]),
            "total_recaudado": round(float(r["total_recaudado"]), 2),
        }
        for r in res
    ]


# ============================================================
# 12. Controlador de Calificaciones (RF12)
# ============================================================
def a_listar_calificaciones(db: Database) -> List[Dict[str, Any]]:
    col = db[A_Colecciones.CALIFICACIONES]
    docs = list(col.find())
    for d in docs:
        d["id"] = str(d.pop("_id", ""))
    return docs


def a_obtener_calificacion(db: Database, id_calificacion: str) -> Dict[str, Any]:
    col = db[A_Colecciones.CALIFICACIONES]
    try:
        oid = ObjectId(id_calificacion)
    except Exception:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ID de calificación inválido")
    doc = col.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calificación no encontrada")
    doc["id"] = str(doc.pop("_id", ""))
    return doc


def a_crear_calificacion(db: Database, datos: A_CalificacionCreate) -> Dict[str, Any]:
    # Validar pedido y cliente
    if not db[A_Colecciones.PEDIDOS].find_one({"id_pedido": datos.id_pedido}):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El pedido calificado no existe")
    if not db[A_Colecciones.CLIENTES].find_one({"id_cliente": datos.id_cliente}):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El cliente calificador no existe")

    col = db[A_Colecciones.CALIFICACIONES]
    if col.find_one({"id_pedido": datos.id_pedido}):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este pedido ya ha sido calificado")

    doc = datos.model_dump()
    if not doc.get("fecha"):
        doc["fecha"] = datetime.now(timezone.utc).isoformat()

    res = col.insert_one(doc)
    doc["id"] = str(res.inserted_id)
    doc.pop("_id", None)
    return doc


def a_actualizar_calificacion(db: Database, id_calificacion: str, datos: A_CalificacionUpdate) -> Dict[str, Any]:
    a_obtener_calificacion(db, id_calificacion)
    col = db[A_Colecciones.CALIFICACIONES]
    cambios = {k: v for k, v in datos.model_dump().items() if v is not None}
    if cambios:
        col.update_one({"_id": ObjectId(id_calificacion)}, {"$set": cambios})
    return a_obtener_calificacion(db, id_calificacion)


def a_eliminar_calificacion(db: Database, id_calificacion: str) -> Dict[str, str]:
    a_obtener_calificacion(db, id_calificacion)
    col = db[A_Colecciones.CALIFICACIONES]
    col.delete_one({"_id": ObjectId(id_calificacion)})
    return {"mensaje": f"Calificación con ID {id_calificacion} eliminada exitosamente"}


def a_calificaciones_por_producto(db: Database, id_producto: int) -> Dict[str, Any]:
    col = db[A_Colecciones.CALIFICACIONES]
    docs = list(col.find({"productos.id_producto": id_producto}))

    notas = []
    nombre_prod = None

    for doc in docs:
        doc["id"] = str(doc.pop("_id", ""))
        for p in doc.get("productos", []):
            if p.get("id_producto") == id_producto:
                notas.append(p.get("calificacion", 0))
                if not nombre_prod:
                    nombre_prod = p.get("nombre")

    promedio = (sum(notas) / len(notas)) if notas else 0.0

    return {
        "id_producto": id_producto,
        "nombre_producto": nombre_prod,
        "promedio_calificacion": round(float(promedio), 2),
        "total_evaluaciones": len(notas),
        "calificaciones": docs,
    }
