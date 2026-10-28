from app.database.a_connection import A_Base


class A_Proveedor(A_Base):
    """
    Colección: proveedores
    Campos: id_proveedor (int, PK), nit (UQ), razon_social, telefono, correo,
    direccion, estado (ACTIVO|INACTIVO)
    """

    a_coleccion = "proveedores"
    a_llave = "id_proveedor"
    a_campos_unicos = ["nit"]
