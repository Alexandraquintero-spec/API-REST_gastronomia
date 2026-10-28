from app.database.a_connection import A_Base


class A_Pedido(A_Base):
    """
    Colección: pedidos
    Campos: id_pedido (int, PK), fecha_pedido, id_cliente (FK), id_usuario (FK),
    tipo_pedido (MESA|PARA_LLEVAR|EVENTO), estado (PENDIENTE|EN_PREPARACION|ENTREGADO|ANULADO),
    total, observaciones, detalles: [{id_detalle, id_producto, nombre_producto, cantidad,
    precio_unitario, subtotal}] (detalle_pedido embebido)
    """

    a_coleccion = "pedidos"
    a_llave = "id_pedido"
    a_campos_unicos = []
