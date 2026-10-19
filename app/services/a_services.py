from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from pymongo.database import Database
from sqlalchemy.orm import Session
from app.core.a_security import (
    a_crear_token_acceso,
    a_generar_hash_password,
    a_verificar_password,
)
from app.models.a_models import (
    A_Usuario,
    A_Categoria,
    A_Producto,
    A_Insumo,
    A_Receta,
    A_Proveedor,
    A_Compra,
    A_DetalleCompra,
    A_Cliente,
    A_Pedido,
    A_DetallePedido,
)
from app.repositories.a_repositories import (
    A_UsuarioRepository,
    A_CategoriaRepository,
    A_ProductoRepository,
    A_InsumoRepository,
    A_RecetaRepository,
    A_ProveedorRepository,
    A_CompraRepository,
    A_ClienteRepository,
    A_PedidoRepository,
    A_ReporteRepository,
    A_CalificacionRepository,
)
from app.schemas.a_schemas import (
    A_LoginRequest,
    A_TokenResponse,
    A_UsuarioCreate,
    A_UsuarioUpdate,
    A_CategoriaCreate,
    A_CategoriaUpdate,
    A_ProductoCreate,
    A_ProductoUpdate,
    A_InsumoCreate,
    A_InsumoUpdate,
    A_RecetaCreate,
    A_RecetaUpdate,
    A_ProveedorCreate,
    A_ProveedorUpdate,
    A_CompraCreate,
    A_ClienteCreate,
    A_ClienteUpdate,
    A_PedidoCreate,
    A_CalificacionCreate,
    A_CalificacionUpdate,
)


class A_AuthService:
    """Servicio de autenticación y generación de tokens JWT."""

    def __init__(self, a_db: Session):
        self.a_usuario_repo = A_UsuarioRepository(a_db)

    def a_autenticar_usuario(self, a_datos_login: A_LoginRequest) -> A_TokenResponse:
        a_usuario = self.a_usuario_repo.a_obtener_por_correo(a_datos_login.correo)
        if not a_usuario:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not a_verificar_password(a_datos_login.password, a_usuario.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if a_usuario.estado != "ACTIVO":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="El usuario se encuentra inactivo en el sistema",
            )

        a_token_data = {
            "sub": str(a_usuario.id_usuario),
            "id_usuario": a_usuario.id_usuario,
            "correo": a_usuario.correo,
            "rol": a_usuario.rol,
            "nombres": f"{a_usuario.nombres} {a_usuario.apellidos}",
        }
        a_token = a_crear_token_acceso(a_token_data)
        return A_TokenResponse(
            access_token=a_token,
            token_type="bearer",
            rol=a_usuario.rol,
            id_usuario=a_usuario.id_usuario,
            nombres=f"{a_usuario.nombres} {a_usuario.apellidos}",
        )


class A_UsuarioService:
    """Servicio para gestión de usuarios del sistema."""

    def __init__(self, a_db: Session):
        self.a_usuario_repo = A_UsuarioRepository(a_db)

    def a_listar_usuarios(self) -> List[A_Usuario]:
        return self.a_usuario_repo.a_listar()

    def a_obtener_por_id(self, a_id_usuario: int) -> A_Usuario:
        a_usuario = self.a_usuario_repo.a_obtener_por_id(a_id_usuario)
        if not a_usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        return a_usuario

    def a_crear_usuario(self, a_datos: A_UsuarioCreate) -> A_Usuario:
        # Validar duplicados
        if self.a_usuario_repo.a_obtener_por_correo(a_datos.correo):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El correo ya se encuentra registrado")
        if self.a_usuario_repo.a_obtener_por_identificacion(a_datos.identificacion):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El documento ya se encuentra registrado")

        # Cifrar contraseña con bcrypt (RN06)
        a_hashed_pw = a_generar_hash_password(a_datos.password)
        a_nuevo_usuario = A_Usuario(
            identificacion=a_datos.identificacion,
            nombres=a_datos.nombres,
            apellidos=a_datos.apellidos,
            correo=a_datos.correo,
            password=a_hashed_pw,
            rol=a_datos.rol,
            estado=a_datos.estado,
        )
        return self.a_usuario_repo.a_crear(a_nuevo_usuario)

    def a_actualizar_usuario(self, a_id_usuario: int, a_datos: A_UsuarioUpdate) -> A_Usuario:
        a_usuario = self.a_obtener_por_id(a_id_usuario)

        if a_datos.correo and a_datos.correo != a_usuario.correo:
            if self.a_usuario_repo.a_obtener_por_correo(a_datos.correo):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El correo ya se encuentra registrado")
            a_usuario.correo = a_datos.correo

        if a_datos.identificacion and a_datos.identificacion != a_usuario.identificacion:
            if self.a_usuario_repo.a_obtener_por_identificacion(a_datos.identificacion):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El documento ya se encuentra registrado")
            a_usuario.identificacion = a_datos.identificacion

        if a_datos.nombres is not None:
            a_usuario.nombres = a_datos.nombres
        if a_datos.apellidos is not None:
            a_usuario.apellidos = a_datos.apellidos
        if a_datos.rol is not None:
            a_usuario.rol = a_datos.rol
        if a_datos.estado is not None:
            a_usuario.estado = a_datos.estado
        if a_datos.password is not None:
            a_usuario.password = a_generar_hash_password(a_datos.password)

        return self.a_usuario_repo.a_actualizar(a_usuario)

    def a_eliminar_usuario(self, a_id_usuario: int) -> Dict[str, str]:
        a_usuario = self.a_obtener_por_id(a_id_usuario)
        self.a_usuario_repo.a_eliminar(a_usuario)
        return {"mensaje": f"Usuario con ID {a_id_usuario} eliminado exitosamente"}


class A_CategoriaService:
    """Servicio para categorías de productos."""

    def __init__(self, a_db: Session):
        self.a_categoria_repo = A_CategoriaRepository(a_db)

    def a_listar_categorias(self) -> List[A_Categoria]:
        return self.a_categoria_repo.a_listar()

    def a_obtener_por_id(self, a_id_categoria: int) -> A_Categoria:
        a_cat = self.a_categoria_repo.a_obtener_por_id(a_id_categoria)
        if not a_cat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada")
        return a_cat

    def a_crear_categoria(self, a_datos: A_CategoriaCreate) -> A_Categoria:
        if self.a_categoria_repo.a_obtener_por_nombre(a_datos.nombre):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe una categoría con ese nombre")
        a_cat = A_Categoria(**a_datos.model_dump())
        return self.a_categoria_repo.a_crear(a_cat)

    def a_actualizar_categoria(self, a_id_categoria: int, a_datos: A_CategoriaUpdate) -> A_Categoria:
        a_cat = self.a_obtener_por_id(a_id_categoria)
        if a_datos.nombre and a_datos.nombre != a_cat.nombre:
            if self.a_categoria_repo.a_obtener_por_nombre(a_datos.nombre):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe una categoría con ese nombre")
            a_cat.nombre = a_datos.nombre
        if a_datos.descripcion is not None:
            a_cat.descripcion = a_datos.descripcion
        if a_datos.estado is not None:
            a_cat.estado = a_datos.estado
        return self.a_categoria_repo.a_actualizar(a_cat)

    def a_eliminar_categoria(self, a_id_categoria: int) -> Dict[str, str]:
        a_cat = self.a_obtener_por_id(a_id_categoria)
        if a_cat.productos:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No se puede eliminar la categoría porque contiene productos asociados",
            )
        self.a_categoria_repo.a_eliminar(a_cat)
        return {"mensaje": f"Categoría con ID {a_id_categoria} eliminada exitosamente"}


class A_ProductoService:
    """Servicio para productos y cálculo de costos (RN04)."""

    def __init__(self, a_db: Session):
        self.a_db = a_db
        self.a_producto_repo = A_ProductoRepository(a_db)
        self.a_categoria_repo = A_CategoriaRepository(a_db)
        self.a_receta_repo = A_RecetaRepository(a_db)

    def a_listar_productos(self) -> List[A_Producto]:
        return self.a_producto_repo.a_listar()

    def a_obtener_por_id(self, a_id_producto: int) -> A_Producto:
        a_prd = self.a_producto_repo.a_obtener_por_id(a_id_producto)
        if not a_prd:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
        return a_prd

    def a_listar_por_categoria(self, a_id_categoria: int) -> List[A_Producto]:
        self.a_categoria_repo.a_obtener_por_id(a_id_categoria)
        return self.a_producto_repo.a_listar_por_categoria(a_id_categoria)

    def a_crear_producto(self, a_datos: A_ProductoCreate) -> A_Producto:
        if self.a_producto_repo.a_obtener_por_codigo(a_datos.codigo):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El código de producto ya existe")
        if not self.a_categoria_repo.a_obtener_por_id(a_datos.id_categoria):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La categoría especificada no existe")
        a_prd = A_Producto(**a_datos.model_dump())
        return self.a_producto_repo.a_crear(a_prd)

    def a_actualizar_producto(self, a_id_producto: int, a_datos: A_ProductoUpdate) -> A_Producto:
        a_prd = self.a_obtener_por_id(a_id_producto)
        if a_datos.codigo and a_datos.codigo != a_prd.codigo:
            if self.a_producto_repo.a_obtener_por_codigo(a_datos.codigo):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El código de producto ya existe")
            a_prd.codigo = a_datos.codigo
        if a_datos.id_categoria is not None:
            if not self.a_categoria_repo.a_obtener_por_id(a_datos.id_categoria):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La categoría especificada no existe")
            a_prd.id_categoria = a_datos.id_categoria
        if a_datos.nombre is not None:
            a_prd.nombre = a_datos.nombre
        if a_datos.descripcion is not None:
            a_prd.descripcion = a_datos.descripcion
        if a_datos.precio_venta is not None:
            a_prd.precio_venta = a_datos.precio_venta
        if a_datos.unidad_venta is not None:
            a_prd.unidad_venta = a_datos.unidad_venta
        if a_datos.estado is not None:
            a_prd.estado = a_datos.estado

        return self.a_producto_repo.a_actualizar(a_prd)

    def a_eliminar_producto(self, a_id_producto: int) -> Dict[str, str]:
        """Aplica RN04: Borrado lógico a INACTIVO si tiene movimientos; borrado físico si no."""
        a_prd = self.a_obtener_por_id(a_id_producto)
        if self.a_producto_repo.a_tiene_movimientos(a_id_producto):
            a_prd.estado = "INACTIVO"
            self.a_producto_repo.a_actualizar(a_prd)
            return {
                "mensaje": f"Producto con ID {a_id_producto} tiene movimientos asociados. Se aplicó borrado lógico a estado INACTIVO (RN04)",
                "tipo_borrado": "LOGICO",
            }
        else:
            self.a_producto_repo.a_eliminar(a_prd)
            return {
                "mensaje": f"Producto con ID {a_id_producto} eliminado físicamente exitosamente",
                "tipo_borrado": "FISICO",
            }

    def a_calcular_costo_produccion(self, a_id_producto: int) -> Dict[str, Any]:
        """Calcula el costo de producción: Σ (cantidad * costo_unitario) y margen (RF06)."""
        a_prd = self.a_obtener_por_id(a_id_producto)
        a_recetas = self.a_receta_repo.a_listar_por_producto(a_id_producto)

        a_costo_total = Decimal("0.00")
        a_recetas_detalladas = []

        for r in a_recetas:
            a_costo_item = Decimal(str(r.cantidad)) * Decimal(str(r.insumo.costo_unitario))
            a_costo_total += a_costo_item
            a_recetas_detalladas.append(
                {
                    "id_receta": r.id_receta,
                    "id_producto": r.id_producto,
                    "id_insumo": r.id_insumo,
                    "cantidad": r.cantidad,
                    "nombre_insumo": r.insumo.nombre,
                    "unidad_medida": r.insumo.unidad_medida,
                    "costo_unitario": r.insumo.costo_unitario,
                }
            )

        a_precio_venta = Decimal(str(a_prd.precio_venta))
        a_margen_ganancia = a_precio_venta - a_costo_total
        a_porcentaje = (
            (a_margen_ganancia / a_precio_venta) * Decimal("100.00")
            if a_precio_venta > 0
            else Decimal("0.00")
        )

        return {
            "id_producto": a_prd.id_producto,
            "codigo": a_prd.codigo,
            "nombre": a_prd.nombre,
            "precio_venta": a_precio_venta,
            "costo_produccion": a_costo_total,
            "margen_ganancia": a_margen_ganancia,
            "porcentaje_margen": round(a_porcentaje, 2),
            "receta": a_recetas_detalladas,
        }


class A_InsumoService:
    """Servicio para inventario de insumos (RN04, RF07)."""

    def __init__(self, a_db: Session):
        self.a_insumo_repo = A_InsumoRepository(a_db)

    def a_listar_insumos(self) -> List[A_Insumo]:
        return self.a_insumo_repo.a_listar()

    def a_obtener_por_id(self, a_id_insumo: int) -> A_Insumo:
        a_ins = self.a_insumo_repo.a_obtener_por_id(a_id_insumo)
        if not a_ins:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insumo no encontrado")
        return a_ins

    def a_listar_stock_bajo(self) -> List[A_Insumo]:
        return self.a_insumo_repo.a_listar_stock_bajo()

    def a_listar_por_vencer(self, a_dias: int = 7) -> List[A_Insumo]:
        return self.a_insumo_repo.a_listar_por_vencer(a_dias)

    def a_crear_insumo(self, a_datos: A_InsumoCreate) -> A_Insumo:
        if self.a_insumo_repo.a_obtener_por_nombre(a_datos.nombre):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un insumo con ese nombre")
        a_ins = A_Insumo(**a_datos.model_dump())
        return self.a_insumo_repo.a_crear(a_ins)

    def a_actualizar_insumo(self, a_id_insumo: int, a_datos: A_InsumoUpdate) -> A_Insumo:
        a_ins = self.a_obtener_por_id(a_id_insumo)
        if a_datos.nombre and a_datos.nombre != a_ins.nombre:
            if self.a_insumo_repo.a_obtener_por_nombre(a_datos.nombre):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un insumo con ese nombre")
            a_ins.nombre = a_datos.nombre
        if a_datos.unidad_medida is not None:
            a_ins.unidad_medida = a_datos.unidad_medida
        if a_datos.stock_actual is not None:
            a_ins.stock_actual = a_datos.stock_actual
        if a_datos.stock_minimo is not None:
            a_ins.stock_minimo = a_datos.stock_minimo
        if a_datos.costo_unitario is not None:
            a_ins.costo_unitario = a_datos.costo_unitario
        if a_datos.fecha_vencimiento is not None:
            a_ins.fecha_vencimiento = a_datos.fecha_vencimiento
        if a_datos.estado is not None:
            a_ins.estado = a_datos.estado
        return self.a_insumo_repo.a_actualizar(a_ins)

    def a_eliminar_insumo(self, a_id_insumo: int) -> Dict[str, str]:
        """Aplica RN04: Borrado lógico a INACTIVO si tiene movimientos; borrado físico si no."""
        a_ins = self.a_obtener_por_id(a_id_insumo)
        if self.a_insumo_repo.a_tiene_movimientos(a_id_insumo):
            a_ins.estado = "INACTIVO"
            self.a_insumo_repo.a_actualizar(a_ins)
            return {
                "mensaje": f"Insumo con ID {a_id_insumo} tiene movimientos en recetas o compras. Se cambió a estado INACTIVO (RN04)",
                "tipo_borrado": "LOGICO",
            }
        else:
            self.a_insumo_repo.a_eliminar(a_ins)
            return {
                "mensaje": f"Insumo con ID {a_id_insumo} eliminado físicamente exitosamente",
                "tipo_borrado": "FISICO",
            }


class A_RecetaService:
    """Servicio para recetas de productos (fichas técnicas)."""

    def __init__(self, a_db: Session):
        self.a_receta_repo = A_RecetaRepository(a_db)
        self.a_producto_repo = A_ProductoRepository(a_db)
        self.a_insumo_repo = A_InsumoRepository(a_db)

    def a_listar_recetas(self) -> List[A_Receta]:
        return self.a_receta_repo.a_listar()

    def a_obtener_por_id(self, a_id_receta: int) -> A_Receta:
        a_rec = self.a_receta_repo.a_obtener_por_id(a_id_receta)
        if not a_rec:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receta no encontrada")
        return a_rec

    def a_listar_por_producto(self, a_id_producto: int) -> List[A_Receta]:
        if not self.a_producto_repo.a_obtener_por_id(a_id_producto):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
        return self.a_receta_repo.a_listar_por_producto(a_id_producto)

    def a_crear_receta(self, a_datos: A_RecetaCreate) -> A_Receta:
        if not self.a_producto_repo.a_obtener_por_id(a_datos.id_producto):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
        if not self.a_insumo_repo.a_obtener_por_id(a_datos.id_insumo):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insumo no encontrado")
        a_rec = A_Receta(**a_datos.model_dump())
        return self.a_receta_repo.a_crear(a_rec)

    def a_actualizar_receta(self, a_id_receta: int, a_datos: A_RecetaUpdate) -> A_Receta:
        a_rec = self.a_obtener_por_id(a_id_receta)
        if a_datos.id_producto is not None:
            if not self.a_producto_repo.a_obtener_por_id(a_datos.id_producto):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
            a_rec.id_producto = a_datos.id_producto
        if a_datos.id_insumo is not None:
            if not self.a_insumo_repo.a_obtener_por_id(a_datos.id_insumo):
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insumo no encontrado")
            a_rec.id_insumo = a_datos.id_insumo
        if a_datos.cantidad is not None:
            a_rec.cantidad = a_datos.cantidad
        return self.a_receta_repo.a_actualizar(a_rec)

    def a_eliminar_receta(self, a_id_receta: int) -> Dict[str, str]:
        a_rec = self.a_obtener_por_id(a_id_receta)
        self.a_receta_repo.a_eliminar(a_rec)
        return {"mensaje": f"Ficha técnica/receta con ID {a_id_receta} eliminada exitosamente"}


class A_ProveedorService:
    """Servicio para proveedores (RN04)."""

    def __init__(self, a_db: Session):
        self.a_proveedor_repo = A_ProveedorRepository(a_db)

    def a_listar_proveedores(self) -> List[A_Proveedor]:
        return self.a_proveedor_repo.a_listar()

    def a_obtener_por_id(self, a_id_proveedor: int) -> A_Proveedor:
        a_prov = self.a_proveedor_repo.a_obtener_por_id(a_id_proveedor)
        if not a_prov:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado")
        return a_prov

    def a_crear_proveedor(self, a_datos: A_ProveedorCreate) -> A_Proveedor:
        if self.a_proveedor_repo.a_obtener_por_nit(a_datos.nit):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El NIT de proveedor ya existe")
        a_prov = A_Proveedor(**a_datos.model_dump())
        return self.a_proveedor_repo.a_crear(a_prov)

    def a_actualizar_proveedor(self, a_id_proveedor: int, a_datos: A_ProveedorUpdate) -> A_Proveedor:
        a_prov = self.a_obtener_por_id(a_id_proveedor)
        if a_datos.nit and a_datos.nit != a_prov.nit:
            if self.a_proveedor_repo.a_obtener_por_nit(a_datos.nit):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El NIT de proveedor ya existe")
            a_prov.nit = a_datos.nit
        if a_datos.razon_social is not None:
            a_prov.razon_social = a_datos.razon_social
        if a_datos.telefono is not None:
            a_prov.telefono = a_datos.telefono
        if a_datos.correo is not None:
            a_prov.correo = a_datos.correo
        if a_datos.direccion is not None:
            a_prov.direccion = a_datos.direccion
        if a_datos.estado is not None:
            a_prov.estado = a_datos.estado
        return self.a_proveedor_repo.a_actualizar(a_prov)

    def a_eliminar_proveedor(self, a_id_proveedor: int) -> Dict[str, str]:
        """Aplica RN04: Borrado lógico a INACTIVO si tiene compras; borrado físico si no."""
        a_prov = self.a_obtener_por_id(a_id_proveedor)
        if self.a_proveedor_repo.a_tiene_movimientos(a_id_proveedor):
            a_prov.estado = "INACTIVO"
            self.a_proveedor_repo.a_actualizar(a_prov)
            return {
                "mensaje": f"Proveedor con ID {a_id_proveedor} tiene compras registradas. Se cambió a estado INACTIVO (RN04)",
                "tipo_borrado": "LOGICO",
            }
        else:
            self.a_proveedor_repo.a_eliminar(a_prov)
            return {
                "mensaje": f"Proveedor con ID {a_id_proveedor} eliminado físicamente exitosamente",
                "tipo_borrado": "FISICO",
            }


class A_CompraService:
    """Servicio para compras y actualización de stock/costos (RN02)."""

    def __init__(self, a_db: Session):
        self.a_db = a_db
        self.a_compra_repo = A_CompraRepository(a_db)
        self.a_insumo_repo = A_InsumoRepository(a_db)
        self.a_proveedor_repo = A_ProveedorRepository(a_db)

    def a_listar_compras(self) -> List[A_Compra]:
        return self.a_compra_repo.a_listar()

    def a_obtener_por_id(self, a_id_compra: int) -> A_Compra:
        a_cmp = self.a_compra_repo.a_obtener_por_id(a_id_compra)
        if not a_cmp:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Compra no encontrada")
        return a_cmp

    def a_listar_por_proveedor(self, a_id_proveedor: int) -> List[A_Compra]:
        if not self.a_proveedor_repo.a_obtener_por_id(a_id_proveedor):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado")
        return self.a_compra_repo.a_listar_por_proveedor(a_id_proveedor)

    def a_crear_compra(self, a_datos: A_CompraCreate, a_id_usuario: int) -> A_Compra:
        """Aplica RN02: suma stock_actual y actualiza costo_unitario de cada insumo."""
        if not self.a_proveedor_repo.a_obtener_por_id(a_datos.id_proveedor):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Proveedor no encontrado")

        a_total = Decimal("0.00")
        a_detalles_crear = []

        try:
            for item in a_datos.detalles:
                a_insumo = self.a_insumo_repo.a_obtener_por_id(item.id_insumo)
                if not a_insumo:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Insumo con ID {item.id_insumo} no existe",
                    )
                a_subtotal = item.cantidad * item.costo_unitario
                a_total += a_subtotal

                # RN02: actualizar stock y costo unitario
                a_insumo.stock_actual += item.cantidad
                a_insumo.costo_unitario = item.costo_unitario

                a_det = A_DetalleCompra(
                    id_insumo=item.id_insumo,
                    cantidad=item.cantidad,
                    costo_unitario=item.costo_unitario,
                    subtotal=a_subtotal,
                )
                a_detalles_crear.append(a_det)

            a_compra = A_Compra(
                numero_factura=a_datos.numero_factura,
                id_proveedor=a_datos.id_proveedor,
                id_usuario=a_id_usuario,
                total=a_total,
                detalles=a_detalles_crear,
            )
            self.a_db.add(a_compra)
            self.a_db.commit()
            self.a_db.refresh(a_compra)
            return a_compra
        except Exception:
            self.a_db.rollback()
            raise

    def a_actualizar_compra(self, a_id_compra: int, a_datos: Dict[str, Any]) -> A_Compra:
        a_cmp = self.a_obtener_por_id(a_id_compra)
        if "numero_factura" in a_datos:
            a_cmp.numero_factura = a_datos["numero_factura"]
        return self.a_compra_repo.a_actualizar(a_cmp)

    def a_eliminar_compra(self, a_id_compra: int) -> Dict[str, str]:
        a_cmp = self.a_obtener_por_id(a_id_compra)
        self.a_compra_repo.a_eliminar(a_cmp)
        return {"mensaje": f"Compra con ID {a_id_compra} eliminada exitosamente"}


class A_ClienteService:
    """Servicio para gestión de clientes (RN04)."""

    def __init__(self, a_db: Session):
        self.a_cliente_repo = A_ClienteRepository(a_db)

    def a_listar_clientes(self) -> List[A_Cliente]:
        return self.a_cliente_repo.a_listar()

    def a_obtener_por_id(self, a_id_cliente: int) -> A_Cliente:
        a_cli = self.a_cliente_repo.a_obtener_por_id(a_id_cliente)
        if not a_cli:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
        return a_cli

    def a_crear_cliente(self, a_datos: A_ClienteCreate) -> A_Cliente:
        if self.a_cliente_repo.a_obtener_por_identificacion(a_datos.identificacion):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El documento de identidad ya existe")
        a_cli = A_Cliente(**a_datos.model_dump())
        return self.a_cliente_repo.a_crear(a_cli)

    def a_actualizar_cliente(self, a_id_cliente: int, a_datos: A_ClienteUpdate) -> A_Cliente:
        a_cli = self.a_obtener_por_id(a_id_cliente)
        if a_datos.identificacion and a_datos.identificacion != a_cli.identificacion:
            if self.a_cliente_repo.a_obtener_por_identificacion(a_datos.identificacion):
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El documento de identidad ya existe")
            a_cli.identificacion = a_datos.identificacion
        if a_datos.nombres is not None:
            a_cli.nombres = a_datos.nombres
        if a_datos.apellidos is not None:
            a_cli.apellidos = a_datos.apellidos
        if a_datos.telefono is not None:
            a_cli.telefono = a_datos.telefono
        if a_datos.correo is not None:
            a_cli.correo = a_datos.correo
        if a_datos.tipo_cliente is not None:
            a_cli.tipo_cliente = a_datos.tipo_cliente
        if a_datos.estado is not None:
            a_cli.estado = a_datos.estado
        return self.a_cliente_repo.a_actualizar(a_cli)

    def a_eliminar_cliente(self, a_id_cliente: int) -> Dict[str, str]:
        """Aplica RN04: Borrado lógico a INACTIVO si tiene pedidos; borrado físico si no."""
        a_cli = self.a_obtener_por_id(a_id_cliente)
        if self.a_cliente_repo.a_tiene_movimientos(a_id_cliente):
            a_cli.estado = "INACTIVO"
            self.a_cliente_repo.a_actualizar(a_cli)
            return {
                "mensaje": f"Cliente con ID {a_id_cliente} tiene pedidos registrados. Se cambió a estado INACTIVO (RN04)",
                "tipo_borrado": "LOGICO",
            }
        else:
            self.a_cliente_repo.a_eliminar(a_cli)
            return {
                "mensaje": f"Cliente con ID {a_id_cliente} eliminado físicamente exitosamente",
                "tipo_borrado": "FISICO",
            }


class A_PedidoService:
    """Servicio para gestión de pedidos, aplicación de RN01, RN03 y RN05."""

    def __init__(self, a_db: Session):
        self.a_db = a_db
        self.a_pedido_repo = A_PedidoRepository(a_db)
        self.a_cliente_repo = A_ClienteRepository(a_db)
        self.a_producto_repo = A_ProductoRepository(a_db)
        self.a_insumo_repo = A_InsumoRepository(a_db)
        self.a_receta_repo = A_RecetaRepository(a_db)

    def a_listar_pedidos(self) -> List[A_Pedido]:
        return self.a_pedido_repo.a_listar()

    def a_obtener_por_id(self, a_id_pedido: int) -> A_Pedido:
        a_ped = self.a_pedido_repo.a_obtener_por_id(a_id_pedido)
        if not a_ped:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
        return a_ped

    def a_listar_por_cliente(self, a_id_cliente: int) -> List[A_Pedido]:
        if not self.a_cliente_repo.a_obtener_por_id(a_id_cliente):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")
        return self.a_pedido_repo.a_listar_por_cliente(a_id_cliente)

    def a_listar_por_estado(self, a_estado: str) -> List[A_Pedido]:
        if a_estado not in ["PENDIENTE", "EN_PREPARACION", "ENTREGADO", "ANULADO"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Estado de pedido inválido")
        return self.a_pedido_repo.a_listar_por_estado(a_estado)

    def a_crear_pedido(self, a_datos: A_PedidoCreate, a_id_usuario: int) -> A_Pedido:
        """Aplica RN01: subtotal = cantidad * precio_unitario y total = suma subtotales calculados por la API."""
        if not self.a_cliente_repo.a_obtener_por_id(a_datos.id_cliente):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

        a_total = Decimal("0.00")
        a_detalles_crear = []

        try:
            for item in a_datos.detalles:
                a_prod = self.a_producto_repo.a_obtener_por_id(item.id_producto)
                if not a_prod:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Producto con ID {item.id_producto} no encontrado",
                    )
                if a_prod.estado != "DISPONIBLE":
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"El producto '{a_prod.nombre}' no se encuentra disponible (estado: {a_prod.estado})",
                    )

                # RN01: precio tomado del producto y subtotal calculado por la API
                a_precio_unit = Decimal(str(a_prod.precio_venta))
                a_subtotal = Decimal(str(item.cantidad)) * a_precio_unit
                a_total += a_subtotal

                a_det = A_DetallePedido(
                    id_producto=item.id_producto,
                    cantidad=item.cantidad,
                    precio_unitario=a_precio_unit,
                    subtotal=a_subtotal,
                )
                a_detalles_crear.append(a_det)

            a_nuevo_pedido = A_Pedido(
                id_cliente=a_datos.id_cliente,
                id_usuario=a_id_usuario,
                tipo_pedido=a_datos.tipo_pedido,
                estado="PENDIENTE",
                total=a_total,
                observaciones=a_datos.observaciones,
                detalles=a_detalles_crear,
            )
            self.a_db.add(a_nuevo_pedido)
            self.a_db.commit()
            self.a_db.refresh(a_nuevo_pedido)
            return a_nuevo_pedido
        except Exception:
            self.a_db.rollback()
            raise

    def a_cambiar_estado(self, a_id_pedido: int, a_nuevo_estado: str) -> A_Pedido:
        """Aplica RN03 (descuento de insumos al pasar a ENTREGADO o 409 si falta stock) y RN05 (no modificar ENTREGADO ni ANULADO)."""
        a_ped = self.a_obtener_por_id(a_id_pedido)

        # RN05: Un pedido ENTREGADO o ANULADO no puede modificarse
        if a_ped.estado in ["ENTREGADO", "ANULADO"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Un pedido en estado '{a_ped.estado}' no puede modificarse (RN05)",
            )

        # Validación del flujo de estados:
        # PENDIENTE -> EN_PREPARACION o ANULADO
        # EN_PREPARACION -> ENTREGADO o ANULADO
        if a_ped.estado == "PENDIENTE" and a_nuevo_estado not in ["EN_PREPARACION", "ANULADO"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Transición de estado no permitida: de PENDIENTE solo se puede pasar a EN_PREPARACION o ANULADO",
            )
        if a_ped.estado == "EN_PREPARACION" and a_nuevo_estado not in ["ENTREGADO", "ANULADO"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Transición de estado no permitida: de EN_PREPARACION solo se puede pasar a ENTREGADO o ANULADO",
            )

        # RN03: Al pasar a ENTREGADO, descontar insumos según receta * cantidad
        if a_nuevo_estado == "ENTREGADO":
            # Calcular requerimientos totales agrupados por insumo
            a_insumos_requeridos: Dict[int, Decimal] = {}
            for det in a_ped.detalles:
                a_recetas = self.a_receta_repo.a_listar_por_producto(det.id_producto)
                for rec in a_recetas:
                    a_necesario = Decimal(str(rec.cantidad)) * Decimal(str(det.cantidad))
                    a_insumos_requeridos[rec.id_insumo] = (
                        a_insumos_requeridos.get(rec.id_insumo, Decimal("0.00")) + a_necesario
                    )

            # Validar existencia suficiente para cada insumo antes de descontar nada
            for a_id_insumo, a_cant_necesaria in a_insumos_requeridos.items():
                a_insumo = self.a_insumo_repo.a_obtener_por_id(a_id_insumo)
                if not a_insumo or Decimal(str(a_insumo.stock_actual)) < a_cant_necesaria:
                    a_nombre = a_insumo.nombre if a_insumo else f"ID {a_id_insumo}"
                    a_actual = a_insumo.stock_actual if a_insumo else 0
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=(
                            f"Stock insuficiente para el insumo '{a_nombre}'. "
                            f"Existencias: {a_actual}, Requerido: {a_cant_necesaria} (RN03)"
                        ),
                    )

            # Si todos tienen stock suficiente, descontar inventario en una sola transacción
            for a_id_insumo, a_cant_necesaria in a_insumos_requeridos.items():
                a_insumo = self.a_insumo_repo.a_obtener_por_id(a_id_insumo)
                a_insumo.stock_actual -= a_cant_necesaria

        a_ped.estado = a_nuevo_estado
        self.a_db.commit()
        self.a_db.refresh(a_ped)
        return a_ped

    def a_actualizar_pedido(self, a_id_pedido: int, a_datos: Dict[str, Any]) -> A_Pedido:
        a_ped = self.a_obtener_por_id(a_id_pedido)
        if a_ped.estado in ["ENTREGADO", "ANULADO"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Un pedido en estado '{a_ped.estado}' no puede modificarse (RN05)",
            )
        if "observaciones" in a_datos:
            a_ped.observaciones = a_datos["observaciones"]
        if "tipo_pedido" in a_datos:
            a_ped.tipo_pedido = a_datos["tipo_pedido"]
        return self.a_pedido_repo.a_actualizar(a_ped)

    def a_eliminar_pedido(self, a_id_pedido: int) -> Dict[str, str]:
        a_ped = self.a_obtener_por_id(a_id_pedido)
        if a_ped.estado in ["ENTREGADO", "EN_PREPARACION"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"No se puede eliminar un pedido en estado {a_ped.estado}",
            )
        self.a_pedido_repo.a_eliminar(a_ped)
        return {"mensaje": f"Pedido con ID {a_id_pedido} eliminado exitosamente"}


class A_ReporteService:
    """Servicio de reportes y agregaciones."""

    def __init__(self, a_db: Session):
        self.a_reporte_repo = A_ReporteRepository(a_db)

    def a_obtener_ventas(
        self, a_desde: Optional[str] = None, a_hasta: Optional[str] = None
    ) -> Dict[str, Any]:
        a_dt_desde = datetime.fromisoformat(a_desde) if a_desde else None
        a_dt_hasta = datetime.fromisoformat(a_hasta) if a_hasta else None
        a_datos = self.a_reporte_repo.a_ventas_por_fecha(a_dt_desde, a_dt_hasta)
        a_datos["desde"] = a_desde
        a_datos["hasta"] = a_hasta
        return a_datos

    def a_obtener_productos_mas_vendidos(self, a_limite: int = 10) -> List[Dict[str, Any]]:
        return self.a_reporte_repo.a_productos_mas_vendidos(a_limite)


class A_CalificacionService:
    """Servicio para calificaciones en MongoDB (RF12)."""

    def __init__(self, a_db: Database, a_mysql_db: Session):
        self.a_mongo_repo = A_CalificacionRepository(a_db)
        self.a_pedido_repo = A_PedidoRepository(a_mysql_db)
        self.a_cliente_repo = A_ClienteRepository(a_mysql_db)

    def a_listar(self) -> List[Dict[str, Any]]:
        return self.a_mongo_repo.a_listar()

    def a_obtener_por_id(self, a_id: str) -> Dict[str, Any]:
        a_doc = self.a_mongo_repo.a_obtener_por_id(a_id)
        if not a_doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Calificación no encontrada")
        return a_doc

    def a_crear(self, a_datos: A_CalificacionCreate) -> Dict[str, Any]:
        # Validar existencia de pedido y cliente en MySQL
        a_ped = self.a_pedido_repo.a_obtener_por_id(a_datos.id_pedido)
        if not a_ped:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El pedido calificado no existe")
        if not self.a_cliente_repo.a_obtener_por_id(a_datos.id_cliente):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El cliente calificador no existe")

        # Evitar calificar el mismo pedido dos veces
        if self.a_mongo_repo.a_obtener_por_pedido(a_datos.id_pedido):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Este pedido ya ha sido calificado")

        a_doc = a_datos.model_dump()
        if not a_doc.get("fecha"):
            a_doc["fecha"] = datetime.now(timezone.utc).isoformat()
        return self.a_mongo_repo.a_crear(a_doc)

    def a_actualizar(self, a_id: str, a_datos: A_CalificacionUpdate) -> Dict[str, Any]:
        self.a_obtener_por_id(a_id)
        a_update = {k: v for k, v in a_datos.model_dump().items() if v is not None}
        return self.a_mongo_repo.a_actualizar(a_id, a_update)

    def a_eliminar(self, a_id: str) -> Dict[str, str]:
        self.a_obtener_por_id(a_id)
        self.a_mongo_repo.a_eliminar(a_id)
        return {"mensaje": f"Calificación con ID {a_id} eliminada exitosamente de MongoDB"}

    def a_calificaciones_por_producto(self, a_id_producto: int) -> Dict[str, Any]:
        """Obtiene las calificaciones y calcula el promedio ponderado de un producto específico."""
        a_documentos = self.a_mongo_repo.a_listar_por_producto(a_id_producto)
        a_notas = []
        a_nombre_producto = None

        for doc in a_documentos:
            for p in doc.get("productos", []):
                if p.get("id_producto") == a_id_producto:
                    a_notas.append(p.get("calificacion", 0))
                    if not a_nombre_producto:
                        a_nombre_producto = p.get("nombre")

        a_promedio = float(sum(a_notas) / len(a_notas)) if a_notas else 0.0

        return {
            "id_producto": a_id_producto,
            "nombre_producto": a_nombre_producto,
            "promedio_calificacion": round(a_promedio, 2),
            "total_evaluaciones": len(a_notas),
            "calificaciones": a_documentos,
        }
