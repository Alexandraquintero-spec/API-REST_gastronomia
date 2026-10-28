from app.database.a_connection import A_Base


class A_Cliente(A_Base):
    """
    Colección: clientes
    Campos: id_cliente (int, PK), identificacion (UQ), nombres, apellidos, telefono,
    correo, tipo_cliente (APRENDIZ|INSTRUCTOR|FUNCIONARIO|EXTERNO), estado (ACTIVO|INACTIVO)
    """

    a_coleccion = "clientes"
    a_llave = "id_cliente"
    a_campos_unicos = ["identificacion"]
