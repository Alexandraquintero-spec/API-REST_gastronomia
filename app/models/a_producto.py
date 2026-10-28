from app.database.a_connection import A_Base


class A_Producto(A_Base):
    """
    Colección: productos
    Campos: id_producto (int, PK), codigo (UQ), nombre, descripcion, precio_venta (> 0),
    unidad_venta, id_categoria (FK categorias), estado (DISPONIBLE|AGOTADO|INACTIVO)
    """

    a_coleccion = "productos"
    a_llave = "id_producto"
    a_campos_unicos = ["codigo"]
