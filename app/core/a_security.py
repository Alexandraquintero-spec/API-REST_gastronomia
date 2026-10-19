from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from app.core.a_config import a_settings

# Configuración de hashing de contraseñas con bcrypt (RN06)
a_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema Bearer para FastAPI / Swagger
a_bearer_scheme = HTTPBearer(auto_error=False)


def a_generar_hash_password(a_plain_password: str) -> str:
    """Genera hash bcrypt a partir de texto plano."""
    return a_pwd_context.hash(a_plain_password)


def a_verificar_password(a_plain_password: str, a_hashed_password: str) -> bool:
    """Verifica si la contraseña plana coincide con el hash almacenado."""
    return a_pwd_context.verify(a_plain_password, a_hashed_password)


def a_crear_token_acceso(a_datos: Dict[str, Any], a_tiempo_expiracion: Optional[timedelta] = None) -> str:
    """Genera un token JWT con tiempo de expiración y payload del usuario."""
    a_a_codificar = a_datos.copy()
    if a_tiempo_expiracion:
        a_exp = datetime.now(timezone.utc) + a_tiempo_expiracion
    else:
        a_exp = datetime.now(timezone.utc) + timedelta(minutes=a_settings.a_jwt_expire_minutes)

    a_a_codificar.update({"exp": a_exp, "iat": datetime.now(timezone.utc)})
    a_token_jwt = jwt.encode(
        a_a_codificar,
        a_settings.a_jwt_secret,
        algorithm=a_settings.a_jwt_algorithm,
    )
    return a_token_jwt


def a_decodificar_token_acceso(a_token: str) -> Dict[str, Any]:
    """Decodifica y valida un token JWT; lanza 401 si es inválido o expiró."""
    try:
        a_payload = jwt.decode(
            a_token,
            a_settings.a_jwt_secret,
            algorithms=[a_settings.a_jwt_algorithm],
        )
        return a_payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token de autenticación ha expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticación inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )


def a_obtener_usuario_actual(
    a_credenciales: Optional[HTTPAuthorizationCredentials] = Depends(a_bearer_scheme),
) -> Dict[str, Any]:
    """Dependencia para autenticar token JWT en peticiones privadas."""
    if not a_credenciales or not a_credenciales.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de autenticación no proporcionadas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    a_payload = a_decodificar_token_acceso(a_credenciales.credentials)
    if "sub" not in a_payload or "rol" not in a_payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no contiene los datos requeridos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return a_payload


class A_ValidadorRoles:
    """Clase para autorizar acceso según roles permitidos."""

    def __init__(self, a_roles_permitidos: List[str]):
        self.a_roles_permitidos = a_roles_permitidos

    def __call__(
        self, a_usuario_actual: Dict[str, Any] = Depends(a_obtener_usuario_actual)
    ) -> Dict[str, Any]:
        a_rol_usuario = a_usuario_actual.get("rol")
        if a_rol_usuario not in self.a_roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado: el rol '{a_rol_usuario}' no tiene permisos para esta acción",
            )
        return a_usuario_actual


def a_requerir_roles(a_roles_permitidos: List[str]) -> A_ValidadorRoles:
    """Genera dependencia de validación de roles requeridos (403 si no coincide)."""
    return A_ValidadorRoles(a_roles_permitidos)
