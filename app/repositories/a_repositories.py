from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional
from bson import ObjectId
from pymongo.database import Database
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
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


class A_UsuarioRepository:
    """Acceso a datos de la entidad usuarios."""

    def __init__(self, a_db: Session):
        self.a_db = a_db

    def a_obtener_por_id(self, a_id_usuario: int) -> Optional[A_Usuario]:
        return self.a_db.query(A_Usuario).filter(A_Usuario.id_usuario == a_id_usuario).first()

    def a_obtener_por_correo(self, a_correo: str) -> Optional[A_Usuario]:
        return self.a_db.query(A_Usuario).filter(A_Usuario.correo == a_correo).first()

    def a_obtener_por_identificacion(self, a_identificacion: str) -> Optional[A_Usuario]:
        return self.a_db.query(A_Usuario).filter(A_Usuario.identificacion == a_identificacion).first()

    def a_listar(self) -> List[A_Usuario]:
        return self.a_db.query(A_Usuario).all()

    def a_crear(self, a_usuario: A_Usuario) -> A_Usuario:
        self.a_db.add(a_usuario)
        self.a_db.commit()
        self.a_db.refresh(a_usuario)
        return a_usuario

    def a_actualizar(self, a_usuario: A_Usuario) -> A_Usuario:
        self.a_db.commit()
        self.a_db.refresh(a_usuario)
        return a_usuario

    def a_eliminar(self, a_usuario: A_Usuario) -> None:
        self.a_db.delete(a_usuario)
        self.a_db.commit()


class A_CategoriaRepository:
    """Acceso a datos de la entidad categorias."""

    def __init__(self, a_db: Session):
        self.a_db = a_db

    def a_obtener_por_id(self, a_id_categoria: int) -> Optional[A_Categoria]:
        return self.a_db.query(A_Categoria).filter(A_Categoria.id_categoria == a_id_categoria).first()

    def a_obtener_por_nombre(self, a_nombre: str) -> Optional[A_Categoria]:
        return self.a_db.query(A_Categoria).filter(A_Categoria.nombre == a_nombre).first()

    def a_listar(self) -> List[A_Categoria]:
        return self.a_db.query(A_Categoria).all()

    def a_crear(self, a_categoria: A_Categoria) -> A_Categoria:
        self.a_db.add(a_categoria)
        self.a_db.commit()
        self.a_db.refresh(a_categoria)
        return a_categoria

    def a_actualizar(self, a_categoria: A_Categoria) -> A_Categoria:
        self.a_db.commit()
        self.a_db.refresh(a_categoria)
        return a_categoria

    def a_eliminar(self, a_categoria: A_Categoria) -> None:
        self.a_db.delete(a_categoria)
        self.a_db.commit()


class A_ProductoRepository:
    """Acceso a datos de la entidad productos."""

    def __init__(self, a_db: Session):
        self.a_db = a_db

    def a_obtener_por_id(self, a_id_producto: int) -> Optional[A_Producto]:
        return self.a_db.query(A_Producto).filter(A_Producto.id_producto == a_id_producto).first()

    def a_obtener_por_codigo(self, a_codigo: str) -> Optional[A_Producto]:
        return self.a_db.query(A_Producto).filter(A_Producto.codigo == a_codigo).first()

    def a_listar(self) -> List[A_Producto]:
        return self.a_db.query(A_Producto).all()

    def a_listar_por_categoria(self, a_id_categoria: int) -> List[A_Producto]:
        return self.a_db.query(A_Producto).filter(A_Producto.id_categoria == a_id_categoria).all()

    def a_crear(self, a_producto: A_Producto) -> A_Producto:
        self.a_db.add(a_producto)
        self.a_db.commit()
        self.a_db.refresh(a_producto)
        return a_producto

    def a_actualizar(self, a_producto: A_Producto) -> A_Producto:
        self.a_db.commit()
        self.a_db.refresh(a_producto)
        return a_producto

    def a_eliminar(self, a_producto: A_Producto) -> None:
        self.a_db.delete(a_producto)
        self.a_db.commit()

    def a_tiene_movimientos(self, a_id_producto: int) -> bool:
        """Verifica si el producto está en recetas o detalles de pedidos."""
        a_en_recetas = self.a_db.query(A_Receta).filter(A_Receta.id_producto == a_id_producto).first()
        if a_en_recetas:
            return True
        a_en_pedidos = self.a_db.query(A_DetallePedido).filter(A_DetallePedido.id_producto == a_id_producto).first()
        return a_en_pedidos is not None


class A_InsumoRepository:
    """Acceso a datos de la entidad insumos."""

    def __init__(self, a_db: Session):
        self.a_db = a_db

    def a_obtener_por_id(self, a_id_insumo: int) -> Optional[A_Insumo]:
        return self.a_db.query(A_Insumo).filter(A_Insumo.id_insumo == a_id_insumo).first()

    def a_obtener_por_nombre(self, a_nombre: str) -> Optional[A_Insumo]:
        return self.a_db.query(A_Insumo).filter(A_Insumo.nombre == a_nombre).first()

    def a_listar(self) -> List[A_Insumo]:
        return self.a_db.query(A_Insumo).all()

    def a_listar_stock_bajo(self) -> List[A_Insumo]:
        """Insumos con stock_actual <= stock_minimo."""
        return self.a_db.query(A_Insumo).filter(A_Insumo.stock_actual <= A_Insumo.stock_minimo).all()

    def a_listar_por_vencer(self, a_dias: int = 7) -> List[A_Insumo]:
        """Insumos que vencen en los próximos N días a partir de la fecha actual."""
        a_hoy = date.today()
        a_limite = a_hoy + timedelta(days=a_dias)
        return (
            self.a_db.query(A_Insumo)
            .filter(
                A_Insumo.fecha_vencimiento.isnot(None),
                A_Insumo.fecha_vencimiento >= a_hoy,
                A_Insumo.fecha_vencimiento <= a_limite,
            )
            .all()
        )

    def a_crear(self, a_insumo: A_Insumo) -> A_Insumo:
        self.a_db.add(a_insumo)
        self.a_db.commit()
        self.a_db.refresh(a_insumo)
        return a_insumo

    def a_actualizar(self, a_insumo: A_Insumo) -> A_Insumo:
        self.a_db.commit()
        self.a_db.refresh(a_insumo)
        return a_insumo

    def a_eliminar(self, a_insumo: A_Insumo) -> None:
        self.a_db.delete(a_insumo)
        self.a_db.commit()

    def a_tiene_movimientos(self, a_id_insumo: int) -> bool:
        """Verifica si el insumo está en recetas o en compras."""
        a_en_recetas = self.a_db.query(A_Receta).filter(A_Receta.id_insumo == a_id_insumo).first()
        if a_en_recetas:
            return True
        a_en_compras = self.a_db.query(A_DetalleCompra).filter(A_DetalleCompra.id_insumo == a_id_insumo).first()
        return a_en_compras is not None


class A_RecetaRepository:
    """Acceso a datos de la entidad recetas (fichas técnicas)."""

    def __init__(self, a_db: Session):
        self.a_db = a_db

    def a_obtener_por_id(self, a_id_receta: int) -> Optional[A_Receta]:
        return self.a_db.query(A_Receta).filter(A_Receta.id_receta == a_id_receta).first()

    def a_listar(self) -> List[A_Receta]:
        return self.a_db.query(A_Receta).all()

    def a_listar_por_producto(self, a_id_producto: int) -> List[A_Receta]:
        return self.a_db.query(A_Receta).filter(A_Receta.id_producto == a_id_producto).all()

    def a_crear(self, a_receta: A_Receta) -> A_Receta:
        self.a_db.add(a_receta)
        self.a_db.commit()
        self.a_db.refresh(a_receta)
        return a_receta

    def a_actualizar(self, a_receta: A_Receta) -> A_Receta:
        self.a_db.commit()
        self.a_db.refresh(a_receta)
        return a_receta

    def a_eliminar(self, a_receta: A_Receta) -> None:
        self.a_db.delete(a_receta)
        self.a_db.commit()


class A_ProveedorRepository:
    """Acceso a datos de la entidad proveedores."""

    def __init__(self, a_db: Session):
        self.a_db = a_db

    def a_obtener_por_id(self, a_id_proveedor: int) -> Optional[A_Proveedor]:
        return self.a_db.query(A_Proveedor).filter(A_Proveedor.id_proveedor == a_id_proveedor).first()

    def a_obtener_por_nit(self, a_nit: str) -> Optional[A_Proveedor]:
        return self.a_db.query(A_Proveedor).filter(A_Proveedor.nit == a_nit).first()

    def a_listar(self) -> List[A_Proveedor]:
        return self.a_db.query(A_Proveedor).all()

    def a_crear(self, a_proveedor: A_Proveedor) -> A_Proveedor:
        self.a_db.add(a_proveedor)
        self.a_db.commit()
        self.a_db.refresh(a_proveedor)
        return a_proveedor

    def a_actualizar(self, a_proveedor: A_Proveedor) -> A_Proveedor:
        self.a_db.commit()
        self.a_db.refresh(a_proveedor)
        return a_proveedor

    def a_eliminar(self, a_proveedor: A_Proveedor) -> None:
        self.a_db.delete(a_proveedor)
        self.a_db.commit()

    def a_tiene_movimientos(self, a_id_proveedor: int) -> bool:
        """Verifica si el proveedor tiene compras registradas."""
        a_compra = self.a_db.query(A_Compra).filter(A_Compra.id_proveedor == a_id_proveedor).first()
        return a_compra is not None


class A_CompraRepository:
    """Acceso a datos de compras y detalle de compras."""

    def __init__(self, a_db: Session):
        self.a_db = a_db

    def a_obtener_por_id(self, a_id_compra: int) -> Optional[A_Compra]:
        return self.a_db.query(A_Compra).filter(A_Compra.id_compra == a_id_compra).first()

    def a_listar(self) -> List[A_Compra]:
        return self.a_db.query(A_Compra).order_by(desc(A_Compra.fecha_compra)).all()

    def a_listar_por_proveedor(self, a_id_proveedor: int) -> List[A_Compra]:
        return (
            self.a_db.query(A_Compra)
            .filter(A_Compra.id_proveedor == a_id_proveedor)
            .order_by(desc(A_Compra.fecha_compra))
            .all()
        )

    def a_crear(self, a_compra: A_Compra) -> A_Compra:
        self.a_db.add(a_compra)
        self.a_db.commit()
        self.a_db.refresh(a_compra)
        return a_compra

    def a_actualizar(self, a_compra: A_Compra) -> A_Compra:
        self.a_db.commit()
        self.a_db.refresh(a_compra)
        return a_compra

    def a_eliminar(self, a_compra: A_Compra) -> None:
        self.a_db.delete(a_compra)
        self.a_db.commit()


class A_ClienteRepository:
    """Acceso a datos de la entidad clientes."""

    def __init__(self, a_db: Session):
        self.a_db = a_db

    def a_obtener_por_id(self, a_id_cliente: int) -> Optional[A_Cliente]:
        return self.a_db.query(A_Cliente).filter(A_Cliente.id_cliente == a_id_cliente).first()

    def a_obtener_por_identificacion(self, a_identificacion: str) -> Optional[A_Cliente]:
        return self.a_db.query(A_Cliente).filter(A_Cliente.identificacion == a_identificacion).first()

    def a_listar(self) -> List[A_Cliente]:
        return self.a_db.query(A_Cliente).all()

    def a_crear(self, a_cliente: A_Cliente) -> A_Cliente:
        self.a_db.add(a_cliente)
        self.a_db.commit()
        self.a_db.refresh(a_cliente)
        return a_cliente

    def a_actualizar(self, a_cliente: A_Cliente) -> A_Cliente:
        self.a_db.commit()
        self.a_db.refresh(a_cliente)
        return a_cliente

    def a_eliminar(self, a_cliente: A_Cliente) -> None:
        self.a_db.delete(a_cliente)
        self.a_db.commit()

    def a_tiene_movimientos(self, a_id_cliente: int) -> bool:
        """Verifica si el cliente tiene pedidos registrados."""
        a_pedido = self.a_db.query(A_Pedido).filter(A_Pedido.id_cliente == a_id_cliente).first()
        return a_pedido is not None


class A_PedidoRepository:
    """Acceso a datos de pedidos y detalles de pedidos."""

    def __init__(self, a_db: Session):
        self.a_db = a_db

    def a_obtener_por_id(self, a_id_pedido: int) -> Optional[A_Pedido]:
        return self.a_db.query(A_Pedido).filter(A_Pedido.id_pedido == a_id_pedido).first()

    def a_listar(self) -> List[A_Pedido]:
        return self.a_db.query(A_Pedido).order_by(desc(A_Pedido.fecha_pedido)).all()

    def a_listar_por_cliente(self, a_id_cliente: int) -> List[A_Pedido]:
        return (
            self.a_db.query(A_Pedido)
            .filter(A_Pedido.id_cliente == a_id_cliente)
            .order_by(desc(A_Pedido.fecha_pedido))
            .all()
        )

    def a_listar_por_estado(self, a_estado: str) -> List[A_Pedido]:
        return (
            self.a_db.query(A_Pedido)
            .filter(A_Pedido.estado == a_estado)
            .order_by(desc(A_Pedido.fecha_pedido))
            .all()
        )

    def a_crear(self, a_pedido: A_Pedido) -> A_Pedido:
        self.a_db.add(a_pedido)
        self.a_db.commit()
        self.a_db.refresh(a_pedido)
        return a_pedido

    def a_actualizar(self, a_pedido: A_Pedido) -> A_Pedido:
        self.a_db.commit()
        self.a_db.refresh(a_pedido)
        return a_pedido

    def a_eliminar(self, a_pedido: A_Pedido) -> None:
        self.a_db.delete(a_pedido)
        self.a_db.commit()


class A_ReporteRepository:
    """Consultas de agregación y reportes de negocio."""

    def __init__(self, a_db: Session):
        self.a_db = a_db

    def a_ventas_por_fecha(
        self, a_desde: Optional[datetime], a_hasta: Optional[datetime]
    ) -> Dict[str, Any]:
        """Calcula el total vendido y la cantidad de pedidos entregados en un rango de fechas."""
        a_query = self.a_db.query(
            func.coalesce(func.sum(A_Pedido.total), 0).label("total_ventas"),
            func.count(A_Pedido.id_pedido).label("numero_pedidos"),
        ).filter(A_Pedido.estado == "ENTREGADO")

        if a_desde:
            a_query = a_query.filter(A_Pedido.fecha_pedido >= a_desde)
        if a_hasta:
            a_query = a_query.filter(A_Pedido.fecha_pedido <= a_hasta)

        a_resultado = a_query.first()
        return {
            "total_ventas": Decimal(str(a_resultado[0])),
            "numero_pedidos": int(a_resultado[1]),
        }

    def a_productos_mas_vendidos(self, a_limite: int = 10) -> List[Dict[str, Any]]:
        """Ranking de productos más vendidos en pedidos entregados."""
        a_query = (
            self.a_db.query(
                A_Producto.id_producto,
                A_Producto.nombre,
                func.sum(A_DetallePedido.cantidad).label("cantidad_vendida"),
                func.sum(A_DetallePedido.subtotal).label("total_recaudado"),
            )
            .join(A_DetallePedido, A_Producto.id_producto == A_DetallePedido.id_producto)
            .join(A_Pedido, A_DetallePedido.id_pedido == A_Pedido.id_pedido)
            .filter(A_Pedido.estado == "ENTREGADO")
            .group_by(A_Producto.id_producto, A_Producto.nombre)
            .order_by(desc("cantidad_vendida"))
            .limit(a_limite)
        )

        a_filas = a_query.all()
        return [
            {
                "id_producto": r[0],
                "nombre": r[1],
                "cantidad_vendida": int(r[2]),
                "total_recaudado": Decimal(str(r[3])),
            }
            for r in a_filas
        ]


class A_CalificacionRepository:
    """Acceso a datos de calificaciones en MongoDB."""

    def __init__(self, a_db: Database):
        self.a_db = a_db
        self.a_collection = a_db["calificaciones"]

    def a_listar(self) -> List[Dict[str, Any]]:
        a_documentos = list(self.a_collection.find())
        for doc in a_documentos:
            doc["id"] = str(doc.pop("_id", ""))
        return a_documentos

    def a_obtener_por_id(self, a_id: str) -> Optional[Dict[str, Any]]:
        try:
            a_oid = ObjectId(a_id)
        except Exception:
            return None
        doc = self.a_collection.find_one({"_id": a_oid})
        if doc:
            doc["id"] = str(doc.pop("_id", ""))
        return doc

    def a_obtener_por_pedido(self, a_id_pedido: int) -> Optional[Dict[str, Any]]:
        doc = self.a_collection.find_one({"id_pedido": a_id_pedido})
        if doc:
            doc["id"] = str(doc.pop("_id", ""))
        return doc

    def a_crear(self, a_datos: Dict[str, Any]) -> Dict[str, Any]:
        a_resultado = self.a_collection.insert_one(a_datos)
        a_datos["id"] = str(a_resultado.inserted_id)
        a_datos.pop("_id", None)
        return a_datos

    def a_actualizar(self, a_id: str, a_datos: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            a_oid = ObjectId(a_id)
        except Exception:
            return None
        self.a_collection.update_one({"_id": a_oid}, {"$set": a_datos})
        return self.a_obtener_por_id(a_id)

    def a_eliminar(self, a_id: str) -> bool:
        try:
            a_oid = ObjectId(a_id)
        except Exception:
            return False
        a_res = self.a_collection.delete_one({"_id": a_oid})
        return a_res.deleted_count > 0

    def a_listar_por_producto(self, a_id_producto: int) -> List[Dict[str, Any]]:
        a_documentos = list(self.a_collection.find({"productos.id_producto": a_id_producto}))
        for doc in a_documentos:
            doc["id"] = str(doc.pop("_id", ""))
        return a_documentos
