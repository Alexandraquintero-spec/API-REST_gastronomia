
import argparse
import getpass
import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

A_ROL_API = "rol_api_gastronomia"


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


def a_crear_usuario_api(a_bd):
    a_usuario_api = os.getenv("MONGO_USER") or "usr_gastronomia_api"

    # Rol a la medida: solo leer, insertar, actualizar, borrar documentos y crear índices.
    # No puede borrar colecciones ni la base, crear usuarios ni cambiar permisos.
    a_privilegios = [
        {
            "resource": {"db": a_bd.name, "collection": ""},
            "actions": ["find", "insert", "update", "remove", "createIndex"],
        }
    ]
    a_roles_existentes = a_bd.command("rolesInfo", A_ROL_API)["roles"]
    if a_roles_existentes:
        a_bd.command("updateRole", A_ROL_API, privileges=a_privilegios, roles=[])
        print(f"Rol actualizado: {A_ROL_API}")
    else:
        a_bd.command("createRole", A_ROL_API, privileges=a_privilegios, roles=[])
        print(f"Rol creado: {A_ROL_API}")

    a_roles_usuario = [{"role": A_ROL_API, "db": a_bd.name}]
    if a_bd.command("usersInfo", a_usuario_api)["users"]:
        a_bd.command("updateUser", a_usuario_api, roles=a_roles_usuario)
        print(f"El usuario {a_usuario_api} ya existe; se actualizaron sus roles.")
    else:
        a_clave = os.getenv("MONGO_PASSWORD") or getpass.getpass(f"Contraseña nueva para {a_usuario_api}: ")
        a_bd.command("createUser", a_usuario_api, pwd=a_clave, roles=a_roles_usuario)
        print(f"Usuario creado: {a_usuario_api}")

    # Evidencia de permisos otorgados
    a_info = a_bd.command("usersInfo", a_usuario_api, showPrivileges=True)["users"][0]
    for a_privilegio in a_info["inheritedPrivileges"]:
        print(f"Permisos sobre {a_privilegio['resource']}: {sorted(a_privilegio['actions'])}")


if __name__ == "__main__":
    a_crear_usuario_api(a_conectar("Crea el usuario de la API con mínimos privilegios"))
