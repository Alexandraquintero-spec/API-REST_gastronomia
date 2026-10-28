from app.database.a_connection import A_Base


class A_Usuario(A_Base):
    """
    Colección: usuarios
    Campos: id_usuario (int, PK), identificacion (UQ), nombres, apellidos,
    correo (UQ), password (hash bcrypt - RN06), rol (ADMIN|CAJERO|COCINERO),
    estado (ACTIVO|INACTIVO)
    """

    a_coleccion = "usuarios"
    a_llave = "id_usuario"
    a_campos_unicos = ["correo", "identificacion"]
