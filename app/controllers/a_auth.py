from fastapi import HTTPException, status
from pymongo.database import Database
from app.core.a_security import a_crear_token_acceso, a_verificar_password
from app.models.a_usuario import A_Usuario
from app.schemas.a_auth import A_LoginRequest, A_TokenResponse


def a_autenticar_usuario(a_db: Database, a_datos_login: A_LoginRequest) -> A_TokenResponse:
    """RF01: valida correo y contraseña (bcrypt) y genera el token JWT con el rol."""
    a_usuario = A_Usuario.a_tabla(a_db).find_one({"correo": a_datos_login.correo})
    if not a_usuario or not a_verificar_password(a_datos_login.password, a_usuario["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if a_usuario.get("estado") != "ACTIVO":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="El usuario se encuentra inactivo en el sistema",
        )

    a_nombre_completo = f"{a_usuario['nombres']} {a_usuario['apellidos']}"
    a_token = a_crear_token_acceso(
        {
            "sub": str(a_usuario["id_usuario"]),
            "id_usuario": a_usuario["id_usuario"],
            "correo": a_usuario["correo"],
            "rol": a_usuario["rol"],
            "nombres": a_nombre_completo,
        }
    )
    return A_TokenResponse(
        access_token=a_token,
        rol=a_usuario["rol"],
        id_usuario=a_usuario["id_usuario"],
        nombres=a_nombre_completo,
    )
