from app.database.a_connection import A_Base


class A_Receta(A_Base):
    """
    Colección: recetas
    Ficha técnica (relación N:M producto-insumo).
    Campos: id_receta (int, PK), id_producto (FK productos), id_insumo (FK insumos),
    cantidad (cantidad del insumo por unidad de producto)
    """

    a_coleccion = "recetas"
    a_llave = "id_receta"
    a_campos_unicos = []
