from app.database.a_connection import A_Base


class A_Categoria(A_Base):
    """
    Colección: categorias
    Campos: id_categoria (int, PK), nombre (UQ), descripcion, estado (ACTIVO|INACTIVO)
    """

    a_coleccion = "categorias"
    a_llave = "id_categoria"
    a_campos_unicos = ["nombre"]
