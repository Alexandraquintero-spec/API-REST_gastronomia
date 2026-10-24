from datetime import date, datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ============================================================
# 1. Esquemas de Autenticación
# ============================================================
class A_LoginRequest(BaseModel):
    """Esquema para inicio de sesión."""
    correo: EmailStr = Field(..., description="Correo institucional de acceso")
    password: str = Field(..., min_length=4, description="Contraseña de acceso")


class A_TokenResponse(BaseModel):
    """Respuesta con token JWT y datos de sesión."""
    access_token: str
    token_type: str = "bearer"
    rol: str
    id_usuario: int
    nombres: str


# ============================================================
# 2. Esquemas de Usuarios
# ============================================================
class A_UsuarioBase(BaseModel):
    identificacion: str = Field(..., max_length=20, description="Documento de identidad único")
    nombres: str = Field(..., max_length=80, description="Nombres del usuario")
    apellidos: str = Field(..., max_length=80, description="Apellidos del usuario")
    correo: EmailStr = Field(..., description="Correo electrónico institucional")
    rol: Literal["ADMIN", "CAJERO", "COCINERO"] = Field(..., description="Rol del usuario en el sistema")
    estado: Literal["ACTIVO", "INACTIVO"] = Field("ACTIVO", description="Estado del usuario")


class A_UsuarioCreate(A_UsuarioBase):
    password: str = Field(..., min_length=6, description="Contraseña en texto plano a cifrar con bcrypt")


class A_UsuarioUpdate(BaseModel):
    identificacion: Optional[str] = Field(None, max_length=20)
    nombres: Optional[str] = Field(None, max_length=80)
    apellidos: Optional[str] = Field(None, max_length=80)
    correo: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    rol: Optional[Literal["ADMIN", "CAJERO", "COCINERO"]] = None
    estado: Optional[Literal["ACTIVO", "INACTIVO"]] = None


class A_UsuarioResponse(A_UsuarioBase):
    id_usuario: int
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# 3. Esquemas de Categorías
# ============================================================
class A_CategoriaBase(BaseModel):
    nombre: str = Field(..., max_length=60, description="Nombre de la categoría")
    descripcion: Optional[str] = Field(None, max_length=200, description="Descripción")
    estado: Literal["ACTIVO", "INACTIVO"] = Field("ACTIVO", description="Estado de la categoría")


class A_CategoriaCreate(A_CategoriaBase):
    pass


class A_CategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=60)
    descripcion: Optional[str] = Field(None, max_length=200)
    estado: Optional[Literal["ACTIVO", "INACTIVO"]] = None


class A_CategoriaResponse(A_CategoriaBase):
    id_categoria: int
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# 4. Esquemas de Insumos
# ============================================================
class A_InsumoBase(BaseModel):
    nombre: str = Field(..., max_length=100, description="Nombre único del insumo")
    unidad_medida: Literal["g", "kg", "ml", "l", "lb", "unidad"] = Field(..., description="Unidad de medida")
    stock_actual: float = Field(default=0.0, ge=0, description="Existencias actuales")
    stock_minimo: float = Field(default=0.0, ge=0, description="Nivel mínimo de alerta")
    costo_unitario: float = Field(default=0.0, ge=0, description="Costo unitario actual")
    fecha_vencimiento: Optional[str] = Field(None, description="Fecha de vencimiento del lote (YYYY-MM-DD)")
    estado: Literal["ACTIVO", "INACTIVO"] = Field("ACTIVO", description="Estado")


class A_InsumoCreate(A_InsumoBase):
    pass


class A_InsumoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    unidad_medida: Optional[Literal["g", "kg", "ml", "l", "lb", "unidad"]] = None
    stock_actual: Optional[float] = Field(None, ge=0)
    stock_minimo: Optional[float] = Field(None, ge=0)
    costo_unitario: Optional[float] = Field(None, ge=0)
    fecha_vencimiento: Optional[str] = None
    estado: Optional[Literal["ACTIVO", "INACTIVO"]] = None


class A_InsumoResponse(A_InsumoBase):
    id_insumo: int
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# 5. Esquemas de Recetas
# ============================================================
class A_RecetaBase(BaseModel):
    id_producto: int = Field(..., description="ID del producto")
    id_insumo: int = Field(..., description="ID del insumo")
    cantidad: float = Field(..., gt=0, description="Cantidad del insumo requerida")


class A_RecetaCreate(A_RecetaBase):
    pass


class A_RecetaUpdate(BaseModel):
    id_producto: Optional[int] = None
    id_insumo: Optional[int] = None
    cantidad: Optional[float] = Field(None, gt=0)


class A_RecetaResponse(A_RecetaBase):
    id_receta: int
    nombre_insumo: Optional[str] = None
    unidad_medida: Optional[str] = None
    costo_unitario: Optional[float] = None
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# 6. Esquemas de Productos
# ============================================================
class A_ProductoBase(BaseModel):
    codigo: str = Field(..., max_length=20, description="Código interno de producto")
    nombre: str = Field(..., max_length=100, description="Nombre del producto")
    descripcion: Optional[str] = Field(None, description="Descripción del producto")
    precio_venta: float = Field(..., gt=0, description="Precio de venta (> 0)")
    unidad_venta: str = Field(..., max_length=20, description="Unidad de venta (Porción, vaso, etc.)")
    id_categoria: int = Field(..., description="ID de la categoría a la que pertenece")
    estado: Literal["DISPONIBLE", "AGOTADO", "INACTIVO"] = Field("DISPONIBLE", description="Estado")


class A_ProductoCreate(A_ProductoBase):
    pass


class A_ProductoUpdate(BaseModel):
    codigo: Optional[str] = Field(None, max_length=20)
    nombre: Optional[str] = Field(None, max_length=100)
    descripcion: Optional[str] = None
    precio_venta: Optional[float] = Field(None, gt=0)
    unidad_venta: Optional[str] = Field(None, max_length=20)
    id_categoria: Optional[int] = None
    estado: Optional[Literal["DISPONIBLE", "AGOTADO", "INACTIVO"]] = None


class A_ProductoResponse(A_ProductoBase):
    id_producto: int
    categoria_nombre: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class A_ProductoCostoResponse(BaseModel):
    """Respuesta para cálculo de costo de producción y margen comercial (RF06)."""
    id_producto: int
    codigo: str
    nombre: str
    precio_venta: float
    costo_produccion: float
    margen_ganancia: float
    porcentaje_margen: float
    receta: List[A_RecetaResponse]


# ============================================================
# 7. Esquemas de Proveedores
# ============================================================
class A_ProveedorBase(BaseModel):
    nit: str = Field(..., max_length=20, description="NIT o documento del proveedor")
    razon_social: str = Field(..., max_length=120, description="Razón social o nombre comercial")
    telefono: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto")
    correo: Optional[str] = Field(None, max_length=120, description="Correo electrónico")
    direccion: Optional[str] = Field(None, max_length=150, description="Dirección comercial")
    estado: Literal["ACTIVO", "INACTIVO"] = Field("ACTIVO", description="Estado del proveedor")


class A_ProveedorCreate(A_ProveedorBase):
    pass


class A_ProveedorUpdate(BaseModel):
    nit: Optional[str] = Field(None, max_length=20)
    razon_social: Optional[str] = Field(None, max_length=120)
    telefono: Optional[str] = Field(None, max_length=20)
    correo: Optional[str] = Field(None, max_length=120)
    direccion: Optional[str] = Field(None, max_length=150)
    estado: Optional[Literal["ACTIVO", "INACTIVO"]] = None


class A_ProveedorResponse(A_ProveedorBase):
    id_proveedor: int
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# 8. Esquemas de Clientes
# ============================================================
class A_ClienteBase(BaseModel):
    identificacion: str = Field(..., max_length=20, description="Documento de identidad único")
    nombres: str = Field(..., max_length=80, description="Nombres del cliente")
    apellidos: str = Field(..., max_length=80, description="Apellidos del cliente")
    telefono: Optional[str] = Field(None, max_length=20, description="Teléfono")
    correo: Optional[str] = Field(None, max_length=120, description="Correo")
    tipo_cliente: Literal["APRENDIZ", "INSTRUCTOR", "FUNCIONARIO", "EXTERNO"] = Field(
        ..., description="Tipo de cliente"
    )
    estado: Literal["ACTIVO", "INACTIVO"] = Field("ACTIVO", description="Estado del cliente")


class A_ClienteCreate(A_ClienteBase):
    pass


class A_ClienteUpdate(BaseModel):
    identificacion: Optional[str] = Field(None, max_length=20)
    nombres: Optional[str] = Field(None, max_length=80)
    apellidos: Optional[str] = Field(None, max_length=80)
    telefono: Optional[str] = Field(None, max_length=20)
    correo: Optional[str] = Field(None, max_length=120)
    tipo_cliente: Optional[Literal["APRENDIZ", "INSTRUCTOR", "FUNCIONARIO", "EXTERNO"]] = None
    estado: Optional[Literal["ACTIVO", "INACTIVO"]] = None


class A_ClienteResponse(A_ClienteBase):
    id_cliente: int
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# 9. Esquemas de Compras y Detalle (RN02)
# ============================================================
class A_DetalleCompraItemCreate(BaseModel):
    id_insumo: int = Field(..., description="ID del insumo adquirido")
    cantidad: float = Field(..., gt=0, description="Cantidad adquirida")
    costo_unitario: float = Field(..., ge=0, description="Nuevo costo unitario")


class A_CompraCreate(BaseModel):
    numero_factura: str = Field(..., max_length=30, description="Número de factura del proveedor")
    id_proveedor: int = Field(..., description="ID del proveedor")
    detalles: List[A_DetalleCompraItemCreate] = Field(..., min_length=1, description="Ítems de la compra")


class A_DetalleCompraResponse(BaseModel):
    id_detalle_compra: Optional[int] = None
    id_insumo: int
    nombre_insumo: Optional[str] = None
    cantidad: float
    costo_unitario: float
    subtotal: float
    model_config = ConfigDict(from_attributes=True)


class A_CompraResponse(BaseModel):
    id_compra: int
    numero_factura: str
    fecha_compra: str
    id_proveedor: int
    id_usuario: int
    total: float
    detalles: List[A_DetalleCompraResponse] = []
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# 10. Esquemas de Pedidos y Detalle (RN01, RN03, RN05)
# ============================================================
class A_DetallePedidoItemCreate(BaseModel):
    id_producto: int = Field(..., description="ID del producto solicitado")
    cantidad: int = Field(..., gt=0, description="Cantidad solicitada")


class A_PedidoCreate(BaseModel):
    id_cliente: int = Field(..., description="ID del cliente que ordena")
    tipo_pedido: Literal["MESA", "PARA_LLEVAR", "EVENTO"] = Field(..., description="Tipo de pedido")
    observaciones: Optional[str] = Field(None, description="Observaciones especiales")
    detalles: List[A_DetallePedidoItemCreate] = Field(..., min_length=1, description="Ítems del pedido")


class A_PedidoEstadoUpdate(BaseModel):
    estado: Literal["PENDIENTE", "EN_PREPARACION", "ENTREGADO", "ANULADO"] = Field(
        ..., description="Nuevo estado del pedido"
    )


class A_DetallePedidoResponse(BaseModel):
    id_detalle: Optional[int] = None
    id_producto: int
    nombre_producto: Optional[str] = None
    cantidad: int
    precio_unitario: float
    subtotal: float
    model_config = ConfigDict(from_attributes=True)


class A_PedidoResponse(BaseModel):
    id_pedido: int
    fecha_pedido: str
    id_cliente: int
    id_usuario: int
    tipo_pedido: str
    estado: str
    total: float
    observaciones: Optional[str] = None
    detalles: List[A_DetallePedidoResponse] = []
    model_config = ConfigDict(from_attributes=True)


# ============================================================
# 11. Esquemas de Reportes
# ============================================================
class A_ReporteVentasResponse(BaseModel):
    total_ventas: float
    numero_pedidos: int
    desde: Optional[str] = None
    hasta: Optional[str] = None


class A_ProductoMasVendidoItem(BaseModel):
    id_producto: int
    nombre: str
    cantidad_vendida: int
    total_recaudado: float


# ============================================================
# 12. Esquemas de Calificaciones MongoDB
# ============================================================
class A_CalificacionProductoItem(BaseModel):
    id_producto: int = Field(..., description="ID del producto evaluado")
    nombre: str = Field(..., description="Nombre del producto")
    calificacion: int = Field(..., ge=1, le=5, description="Puntuación (1-5)")


class A_CalificacionCreate(BaseModel):
    id_pedido: int = Field(..., description="ID del pedido calificado")
    id_cliente: int = Field(..., description="ID del cliente")
    fecha: Optional[str] = Field(None, description="Fecha ISO-8601 (por defecto actual)")
    calificacion_servicio: int = Field(..., ge=1, le=5, description="Calificación general del servicio")
    comentario: str = Field(..., description="Opinión cualitativa")
    productos: List[A_CalificacionProductoItem] = Field(..., min_length=1, description="Productos evaluados")


class A_CalificacionUpdate(BaseModel):
    calificacion_servicio: Optional[int] = Field(None, ge=1, le=5)
    comentario: Optional[str] = None
    productos: Optional[List[A_CalificacionProductoItem]] = None


class A_CalificacionResponse(BaseModel):
    id: Optional[str] = None
    id_pedido: int
    id_cliente: int
    fecha: str
    calificacion_servicio: int
    comentario: str
    productos: List[A_CalificacionProductoItem]


class A_CalificacionPromedioProductoResponse(BaseModel):
    id_producto: int
    nombre_producto: Optional[str] = None
    promedio_calificacion: float
    total_evaluaciones: int
    calificaciones: List[Dict[str, Any]]
