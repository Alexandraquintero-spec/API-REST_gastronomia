from app.database.a_connection import A_Base


class A_Compra(A_Base):
    """
    Colección: compras
    Campos: id_compra (int, PK), numero_factura, fecha_compra, id_proveedor (FK),
    id_usuario (FK), total, detalles: [{id_detalle_compra, id_insumo, nombre_insumo,
    cantidad, costo_unitario, subtotal}] (detalle_compra embebido)
    """

    a_coleccion = "compras"
    a_llave = "id_compra"
    a_campos_unicos = []
