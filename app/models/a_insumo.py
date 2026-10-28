from app.database.a_connection import A_Base


class A_Insumo(A_Base):
    """
    Colección: insumos
    Campos: id_insumo (int, PK), nombre (UQ), unidad_medida (g|kg|ml|l|lb|unidad),
    stock_actual (>= 0), stock_minimo, costo_unitario, fecha_vencimiento (YYYY-MM-DD),
    estado (ACTIVO|INACTIVO)
    """

    a_coleccion = "insumos"
    a_llave = "id_insumo"
    a_campos_unicos = ["nombre"]
