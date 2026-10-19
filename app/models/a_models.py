from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Numeric,
    Date,
    DateTime,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import relationship
from app.database.a_conexion_mysql import A_Base


class A_Usuario(A_Base):
    """Modelo ORM para la tabla usuarios."""
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    identificacion = Column(String(20), unique=True, nullable=False)
    nombres = Column(String(80), nullable=False)
    apellidos = Column(String(80), nullable=False)
    correo = Column(String(120), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    rol = Column(Enum("ADMIN", "CAJERO", "COCINERO", name="enum_rol"), nullable=False)
    estado = Column(Enum("ACTIVO", "INACTIVO", name="enum_estado_usuario"), default="ACTIVO", nullable=False)


class A_Categoria(A_Base):
    """Modelo ORM para la tabla categorias."""
    __tablename__ = "categorias"

    id_categoria = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(60), unique=True, nullable=False)
    descripcion = Column(String(200), nullable=True)
    estado = Column(Enum("ACTIVO", "INACTIVO", name="enum_estado_categoria"), default="ACTIVO", nullable=False)

    productos = relationship("A_Producto", back_populates="categoria")


class A_Producto(A_Base):
    """Modelo ORM para la tabla productos."""
    __tablename__ = "productos"

    id_producto = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(20), unique=True, nullable=False)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    precio_venta = Column(Numeric(10, 2), nullable=False)
    unidad_venta = Column(String(20), nullable=False)
    id_categoria = Column(Integer, ForeignKey("categorias.id_categoria"), nullable=False)
    estado = Column(Enum("DISPONIBLE", "AGOTADO", "INACTIVO", name="enum_estado_producto"), default="DISPONIBLE", nullable=False)

    categoria = relationship("A_Categoria", back_populates="productos")
    recetas = relationship("A_Receta", back_populates="producto")
    detalles_pedido = relationship("A_DetallePedido", back_populates="producto")


class A_Insumo(A_Base):
    """Modelo ORM para la tabla insumos."""
    __tablename__ = "insumos"

    id_insumo = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), unique=True, nullable=False)
    unidad_medida = Column(Enum("g", "kg", "ml", "l", "lb", "unidad", name="enum_unidad_medida"), nullable=False)
    stock_actual = Column(Numeric(10, 2), default=0.00, nullable=False)
    stock_minimo = Column(Numeric(10, 2), default=0.00, nullable=False)
    costo_unitario = Column(Numeric(10, 2), default=0.00, nullable=False)
    fecha_vencimiento = Column(Date, nullable=True)
    estado = Column(Enum("ACTIVO", "INACTIVO", name="enum_estado_insumo"), default="ACTIVO", nullable=False)

    recetas = relationship("A_Receta", back_populates="insumo")
    detalles_compra = relationship("A_DetalleCompra", back_populates="insumo")


class A_Receta(A_Base):
    """Modelo ORM para la tabla recetas (ficha técnica)."""
    __tablename__ = "recetas"

    id_receta = Column(Integer, primary_key=True, autoincrement=True)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"), nullable=False)
    id_insumo = Column(Integer, ForeignKey("insumos.id_insumo"), nullable=False)
    cantidad = Column(Numeric(10, 3), nullable=False)

    producto = relationship("A_Producto", back_populates="recetas")
    insumo = relationship("A_Insumo", back_populates="recetas")


class A_Proveedor(A_Base):
    """Modelo ORM para la tabla proveedores."""
    __tablename__ = "proveedores"

    id_proveedor = Column(Integer, primary_key=True, autoincrement=True)
    nit = Column(String(20), unique=True, nullable=False)
    razon_social = Column(String(120), nullable=False)
    telefono = Column(String(20), nullable=True)
    correo = Column(String(120), nullable=True)
    direccion = Column(String(150), nullable=True)
    estado = Column(Enum("ACTIVO", "INACTIVO", name="enum_estado_proveedor"), default="ACTIVO", nullable=False)

    compras = relationship("A_Compra", back_populates="proveedor")


class A_Compra(A_Base):
    """Modelo ORM para la tabla compras."""
    __tablename__ = "compras"

    id_compra = Column(Integer, primary_key=True, autoincrement=True)
    numero_factura = Column(String(30), nullable=False)
    fecha_compra = Column(DateTime, default=datetime.utcnow, nullable=False)
    id_proveedor = Column(Integer, ForeignKey("proveedores.id_proveedor"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    total = Column(Numeric(12, 2), default=0.00, nullable=False)

    proveedor = relationship("A_Proveedor", back_populates="compras")
    usuario = relationship("A_Usuario")
    detalles = relationship("A_DetalleCompra", back_populates="compra", cascade="all, delete-orphan")


class A_DetalleCompra(A_Base):
    """Modelo ORM para la tabla detalle_compra."""
    __tablename__ = "detalle_compra"

    id_detalle_compra = Column(Integer, primary_key=True, autoincrement=True)
    id_compra = Column(Integer, ForeignKey("compras.id_compra"), nullable=False)
    id_insumo = Column(Integer, ForeignKey("insumos.id_insumo"), nullable=False)
    cantidad = Column(Numeric(10, 2), nullable=False)
    costo_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(12, 2), nullable=False)

    compra = relationship("A_Compra", back_populates="detalles")
    insumo = relationship("A_Insumo", back_populates="detalles_compra")


class A_Cliente(A_Base):
    """Modelo ORM para la tabla clientes."""
    __tablename__ = "clientes"

    id_cliente = Column(Integer, primary_key=True, autoincrement=True)
    identificacion = Column(String(20), unique=True, nullable=False)
    nombres = Column(String(80), nullable=False)
    apellidos = Column(String(80), nullable=False)
    telefono = Column(String(20), nullable=True)
    correo = Column(String(120), nullable=True)
    tipo_cliente = Column(
        Enum("APRENDIZ", "INSTRUCTOR", "FUNCIONARIO", "EXTERNO", name="enum_tipo_cliente"),
        nullable=False,
    )
    estado = Column(Enum("ACTIVO", "INACTIVO", name="enum_estado_cliente"), default="ACTIVO", nullable=False)

    pedidos = relationship("A_Pedido", back_populates="cliente")


class A_Pedido(A_Base):
    """Modelo ORM para la tabla pedidos."""
    __tablename__ = "pedidos"

    id_pedido = Column(Integer, primary_key=True, autoincrement=True)
    fecha_pedido = Column(DateTime, default=datetime.utcnow, nullable=False)
    id_cliente = Column(Integer, ForeignKey("clientes.id_cliente"), nullable=False)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    tipo_pedido = Column(
        Enum("MESA", "PARA_LLEVAR", "EVENTO", name="enum_tipo_pedido"),
        nullable=False,
    )
    estado = Column(
        Enum("PENDIENTE", "EN_PREPARACION", "ENTREGADO", "ANULADO", name="enum_estado_pedido"),
        default="PENDIENTE",
        nullable=False,
    )
    total = Column(Numeric(12, 2), default=0.00, nullable=False)
    observaciones = Column(Text, nullable=True)

    cliente = relationship("A_Cliente", back_populates="pedidos")
    usuario = relationship("A_Usuario")
    detalles = relationship("A_DetallePedido", back_populates="pedido", cascade="all, delete-orphan")


class A_DetallePedido(A_Base):
    """Modelo ORM para la tabla detalle_pedido."""
    __tablename__ = "detalle_pedido"

    id_detalle = Column(Integer, primary_key=True, autoincrement=True)
    id_pedido = Column(Integer, ForeignKey("pedidos.id_pedido"), nullable=False)
    id_producto = Column(Integer, ForeignKey("productos.id_producto"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(12, 2), nullable=False)

    pedido = relationship("A_Pedido", back_populates="detalles")
    producto = relationship("A_Producto", back_populates="detalles_pedido")
