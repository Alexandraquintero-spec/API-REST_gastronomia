
import argparse
import getpass
import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import ASCENDING, DESCENDING, MongoClient

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Tipos reutilizables
A_ENTERO = {"bsonType": ["int", "long"]}
A_NUMERO = {"bsonType": ["int", "long", "double", "decimal"]}
A_ESTADO_GENERAL = {"enum": ["ACTIVO", "INACTIVO"]}
A_FECHA = {"bsonType": "string", "pattern": r"^\d{4}-\d{2}-\d{2}"}


def a_texto(a_maximo):
    return {"bsonType": "string", "maxLength": a_maximo}


def a_texto_nulo(a_maximo=None):
    a_tipo = {"bsonType": ["string", "null"]}
    if a_maximo:
        a_tipo["maxLength"] = a_maximo
    return a_tipo


def a_mayor_que_cero():
    return {**A_NUMERO, "minimum": 0, "exclusiveMinimum": True}


def a_no_negativo():
    return {**A_NUMERO, "minimum": 0}


A_COLECCIONES = {
    "usuarios": {
        "required": ["id_usuario", "identificacion", "nombres", "apellidos", "correo", "password", "rol", "estado"],
        "properties": {
            "id_usuario": A_ENTERO,
            "identificacion": a_texto(20),
            "nombres": a_texto(80),
            "apellidos": a_texto(80),
            "correo": a_texto(120),
            "password": {"bsonType": "string", "minLength": 60, "maxLength": 60, "description": "Hash bcrypt (RN06)"},
            "rol": {"enum": ["ADMIN", "CAJERO", "COCINERO"]},
            "estado": A_ESTADO_GENERAL,
        },
    },
    "categorias": {
        "required": ["id_categoria", "nombre", "estado"],
        "properties": {
            "id_categoria": A_ENTERO,
            "nombre": a_texto(60),
            "descripcion": a_texto_nulo(200),
            "estado": A_ESTADO_GENERAL,
        },
    },
    "productos": {
        "required": ["id_producto", "codigo", "nombre", "precio_venta", "unidad_venta", "id_categoria", "estado"],
        "properties": {
            "id_producto": A_ENTERO,
            "codigo": a_texto(20),
            "nombre": a_texto(100),
            "descripcion": a_texto_nulo(),
            "precio_venta": a_mayor_que_cero(),
            "unidad_venta": a_texto(20),
            "id_categoria": A_ENTERO,
            "estado": {"enum": ["DISPONIBLE", "AGOTADO", "INACTIVO"]},
        },
    },
    "insumos": {
        "required": ["id_insumo", "nombre", "unidad_medida", "stock_actual", "stock_minimo", "costo_unitario", "estado"],
        "properties": {
            "id_insumo": A_ENTERO,
            "nombre": a_texto(100),
            "unidad_medida": {"enum": ["g", "kg", "ml", "l", "lb", "unidad"]},
            "stock_actual": a_no_negativo(),
            "stock_minimo": a_no_negativo(),
            "costo_unitario": a_no_negativo(),
            "fecha_vencimiento": {"bsonType": ["string", "null"], "pattern": r"^\d{4}-\d{2}-\d{2}$"},
            "estado": A_ESTADO_GENERAL,
        },
    },
    "recetas": {
        "required": ["id_receta", "id_producto", "id_insumo", "cantidad"],
        "properties": {
            "id_receta": A_ENTERO,
            "id_producto": A_ENTERO,
            "id_insumo": A_ENTERO,
            "cantidad": a_mayor_que_cero(),
        },
    },
    "proveedores": {
        "required": ["id_proveedor", "nit", "razon_social", "estado"],
        "properties": {
            "id_proveedor": A_ENTERO,
            "nit": a_texto(20),
            "razon_social": a_texto(120),
            "telefono": a_texto_nulo(20),
            "correo": a_texto_nulo(120),
            "direccion": a_texto_nulo(150),
            "estado": A_ESTADO_GENERAL,
        },
    },
    "compras": {
        "required": ["id_compra", "numero_factura", "fecha_compra", "id_proveedor", "id_usuario", "total", "detalles"],
        "properties": {
            "id_compra": A_ENTERO,
            "numero_factura": a_texto(30),
            "fecha_compra": A_FECHA,
            "id_proveedor": A_ENTERO,
            "id_usuario": A_ENTERO,
            "total": a_no_negativo(),
            "detalles": {
                "bsonType": "array",
                "minItems": 1,
                "items": {
                    "bsonType": "object",
                    "required": ["id_insumo", "cantidad", "costo_unitario", "subtotal"],
                    "properties": {
                        "id_detalle_compra": A_ENTERO,
                        "id_insumo": A_ENTERO,
                        "nombre_insumo": a_texto_nulo(100),
                        "cantidad": a_mayor_que_cero(),
                        "costo_unitario": a_no_negativo(),
                        "subtotal": a_no_negativo(),
                    },
                },
            },
        },
    },
    "clientes": {
        "required": ["id_cliente", "identificacion", "nombres", "apellidos", "tipo_cliente", "estado"],
        "properties": {
            "id_cliente": A_ENTERO,
            "identificacion": a_texto(20),
            "nombres": a_texto(80),
            "apellidos": a_texto(80),
            "telefono": a_texto_nulo(20),
            "correo": a_texto_nulo(120),
            "tipo_cliente": {"enum": ["APRENDIZ", "INSTRUCTOR", "FUNCIONARIO", "EXTERNO"]},
            "estado": A_ESTADO_GENERAL,
        },
    },
    "pedidos": {
        "required": ["id_pedido", "fecha_pedido", "id_cliente", "id_usuario", "tipo_pedido", "estado", "total", "detalles"],
        "properties": {
            "id_pedido": A_ENTERO,
            "fecha_pedido": A_FECHA,
            "id_cliente": A_ENTERO,
            "id_usuario": A_ENTERO,
            "tipo_pedido": {"enum": ["MESA", "PARA_LLEVAR", "EVENTO"]},
            "estado": {"enum": ["PENDIENTE", "EN_PREPARACION", "ENTREGADO", "ANULADO"]},
            "total": a_no_negativo(),
            "observaciones": a_texto_nulo(),
            "detalles": {
                "bsonType": "array",
                "minItems": 1,
                "items": {
                    "bsonType": "object",
                    "required": ["id_producto", "cantidad", "precio_unitario", "subtotal"],
                    "properties": {
                        "id_detalle": A_ENTERO,
                        "id_producto": A_ENTERO,
                        "nombre_producto": a_texto_nulo(100),
                        "cantidad": {**A_ENTERO, "minimum": 1},
                        "precio_unitario": a_no_negativo(),
                        "subtotal": a_no_negativo(),
                    },
                },
            },
        },
    },
    "calificaciones": {
        "required": ["id_pedido", "id_cliente", "fecha", "calificacion_servicio", "comentario", "productos"],
        "properties": {
            "id_pedido": A_ENTERO,
            "id_cliente": A_ENTERO,
            "fecha": A_FECHA,
            "calificacion_servicio": {**A_ENTERO, "minimum": 1, "maximum": 5},
            "comentario": a_texto(500),
            "productos": {
                "bsonType": "array",
                "minItems": 1,
                "items": {
                    "bsonType": "object",
                    "required": ["id_producto", "nombre", "calificacion"],
                    "properties": {
                        "id_producto": A_ENTERO,
                        "nombre": a_texto(100),
                        "calificacion": {**A_ENTERO, "minimum": 1, "maximum": 5},
                    },
                },
            },
        },
    },
    "contadores": {
        "required": ["_id", "seq"],
        "properties": {
            "_id": {"bsonType": "string"},
            "seq": {**A_ENTERO, "minimum": 0},
        },
    },
}

# Índices: (campos, único). Llave primaria numérica (PK), campos únicos (UQ) y de consulta
A_INDICES = {
    "usuarios": [([("id_usuario", ASCENDING)], True), ([("correo", ASCENDING)], True), ([("identificacion", ASCENDING)], True)],
    "categorias": [([("id_categoria", ASCENDING)], True), ([("nombre", ASCENDING)], True)],
    "productos": [([("id_producto", ASCENDING)], True), ([("codigo", ASCENDING)], True), ([("id_categoria", ASCENDING)], False)],
    "insumos": [([("id_insumo", ASCENDING)], True), ([("nombre", ASCENDING)], True), ([("fecha_vencimiento", ASCENDING)], False)],
    "recetas": [
        ([("id_receta", ASCENDING)], True),
        ([("id_producto", ASCENDING), ("id_insumo", ASCENDING)], True),
        ([("id_insumo", ASCENDING)], False),
    ],
    "proveedores": [([("id_proveedor", ASCENDING)], True), ([("nit", ASCENDING)], True)],
    "compras": [([("id_compra", ASCENDING)], True), ([("id_proveedor", ASCENDING), ("fecha_compra", DESCENDING)], False)],
    "clientes": [([("id_cliente", ASCENDING)], True), ([("identificacion", ASCENDING)], True)],
    "pedidos": [
        ([("id_pedido", ASCENDING)], True),
        ([("estado", ASCENDING), ("fecha_pedido", DESCENDING)], False),
        ([("id_cliente", ASCENDING)], False),
    ],
    "calificaciones": [([("id_pedido", ASCENDING)], True), ([("productos.id_producto", ASCENDING)], False)],
    "contadores": [],
}


def a_conectar(a_descripcion):
    """Conecta a MongoDB; con --usuario pide la contraseña del administrador."""
    a_parser = argparse.ArgumentParser(description=a_descripcion)
    a_parser.add_argument("--bd", default=os.getenv("MONGO_DATABASE", "bd_gastronomia_nosql"), help="Base de datos")
    a_parser.add_argument("--usuario", help="Usuario administrador (solo si MongoDB tiene autenticación)")
    a_args = a_parser.parse_args()

    a_host = os.getenv("MONGO_HOST", "localhost")
    a_puerto = int(os.getenv("MONGO_PORT", "27017"))
    if a_args.usuario:
        a_clave = getpass.getpass(f"Contraseña de {a_args.usuario}: ")
        a_cliente = MongoClient(a_host, a_puerto, username=a_args.usuario, password=a_clave, authSource="admin")
    else:
        a_cliente = MongoClient(a_host, a_puerto)
    return a_cliente[a_args.bd]


def a_crear_estructura(a_bd):
    a_existentes = a_bd.list_collection_names()
    for a_nombre, a_esquema in A_COLECCIONES.items():
        a_validador = {"$jsonSchema": {"bsonType": "object", **a_esquema}}
        if a_nombre in a_existentes:
            a_bd.command("collMod", a_nombre, validator=a_validador, validationLevel="strict", validationAction="error")
            print(f"Validador actualizado: {a_nombre}")
        else:
            a_bd.create_collection(a_nombre, validator=a_validador, validationLevel="strict", validationAction="error")
            print(f"Colección creada: {a_nombre}")
        for a_campos, a_unico in A_INDICES[a_nombre]:
            a_bd[a_nombre].create_index(a_campos, unique=a_unico)

    print(f"\nColecciones en {a_bd.name}: {sorted(a_bd.list_collection_names())}")


if __name__ == "__main__":
    a_crear_estructura(a_conectar("Crea las colecciones con su validador $jsonSchema e índices"))
