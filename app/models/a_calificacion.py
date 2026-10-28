from app.database.a_connection import A_Base


class A_Calificacion(A_Base):
    """
    Colección: calificaciones
    Documento libre (RF12). Campos: _id (ObjectId), id_pedido (UQ: un pedido se califica
    una sola vez), id_cliente, fecha, calificacion_servicio (1-5), comentario,
    productos: [{id_producto, nombre, calificacion (1-5)}]
    """

    a_coleccion = "calificaciones"
    a_llave = "_id"
    a_campos_unicos = ["id_pedido"]
