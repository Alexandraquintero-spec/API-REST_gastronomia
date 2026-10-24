"""
Módulo de inicialización de datos de prueba en MongoDB para el proyecto Gastronomía.
Inserta mínimo 10 registros por entidad, con contraseñas en bcrypt real.
"""
from datetime import datetime, timezone
from pymongo.database import Database
from app.core.a_security import a_generar_hash_password


def a_inicializar_base_datos(a_db: Database) -> None:
    """Inicializa colecciones con datos de prueba si están vacías."""
    # 1. Usuarios
    if a_db["usuarios"].count_documents({}) == 0:
        a_pass_admin = a_generar_hash_password("Admin123*")
        a_pass_cajero = a_generar_hash_password("Cajero123*")
        a_pass_cocinero = a_generar_hash_password("Cocinero123*")

        a_usuarios = [
            {"id_usuario": 1, "identificacion": "1075234001", "nombres": "Wilson", "apellidos": "Gomez", "correo": "admin@gastronomia.sena.edu.co", "password": a_pass_admin, "rol": "ADMIN", "estado": "ACTIVO"},
            {"id_usuario": 2, "identificacion": "1075234002", "nombres": "Laura", "apellidos": "Sanchez", "correo": "cajero@gastronomia.sena.edu.co", "password": a_pass_cajero, "rol": "CAJERO", "estado": "ACTIVO"},
            {"id_usuario": 3, "identificacion": "1075234003", "nombres": "Carlos", "apellidos": "Mejia", "correo": "cocinero@gastronomia.sena.edu.co", "password": a_pass_cocinero, "rol": "COCINERO", "estado": "ACTIVO"},
            {"id_usuario": 4, "identificacion": "1075234004", "nombres": "Andres", "apellidos": "Perez", "correo": "admin2@gastronomia.sena.edu.co", "password": a_pass_admin, "rol": "ADMIN", "estado": "ACTIVO"},
            {"id_usuario": 5, "identificacion": "1075234005", "nombres": "Diana", "apellidos": "Torres", "correo": "cajero2@gastronomia.sena.edu.co", "password": a_pass_cajero, "rol": "CAJERO", "estado": "ACTIVO"},
            {"id_usuario": 6, "identificacion": "1075234006", "nombres": "Javier", "apellidos": "Ramirez", "correo": "cocinero2@gastronomia.sena.edu.co", "password": a_pass_cocinero, "rol": "COCINERO", "estado": "ACTIVO"},
            {"id_usuario": 7, "identificacion": "1075234007", "nombres": "Paola", "apellidos": "Vargas", "correo": "cajero3@gastronomia.sena.edu.co", "password": a_pass_cajero, "rol": "CAJERO", "estado": "ACTIVO"},
            {"id_usuario": 8, "identificacion": "1075234008", "nombres": "Hernan", "apellidos": "Duarte", "correo": "cocinero3@gastronomia.sena.edu.co", "password": a_pass_cocinero, "rol": "COCINERO", "estado": "ACTIVO"},
            {"id_usuario": 9, "identificacion": "1075234009", "nombres": "Sonia", "apellidos": "Castillo", "correo": "cajero4@gastronomia.sena.edu.co", "password": a_pass_cajero, "rol": "CAJERO", "estado": "ACTIVO"},
            {"id_usuario": 10, "identificacion": "1075234010", "nombres": "Alberto", "apellidos": "Rios", "correo": "admin3@gastronomia.sena.edu.co", "password": a_pass_admin, "rol": "ADMIN", "estado": "ACTIVO"},
        ]
        a_db["usuarios"].insert_many(a_usuarios)
        a_db["contadores"].update_one({"_id": "usuarios"}, {"$set": {"seq": 10}}, upsert=True)

    # 2. Categorías
    if a_db["categorias"].count_documents({}) == 0:
        a_categorias = [
            {"id_categoria": 1, "nombre": "Platos Fuertes", "descripcion": "Platos principales tradicionales y a la carta", "estado": "ACTIVO"},
            {"id_categoria": 2, "nombre": "Bebidas Calientes", "descripcion": "Cafes, chocolates e infusiones tradicionales", "estado": "ACTIVO"},
            {"id_categoria": 3, "nombre": "Bebidas Frías", "descripcion": "Jugos naturales, limonadas y refrescos", "estado": "ACTIVO"},
            {"id_categoria": 4, "nombre": "Panadería", "descripcion": "Panes artesanales y amasijos tradicionales", "estado": "ACTIVO"},
            {"id_categoria": 5, "nombre": "Repostería", "descripcion": "Tortas, postres y dulces horneados", "estado": "ACTIVO"},
            {"id_categoria": 6, "nombre": "Sopas", "descripcion": "Caldos, cremas y sopas tipicas", "estado": "ACTIVO"},
            {"id_categoria": 7, "nombre": "Ensaladas", "descripcion": "Ensaladas frescas y guarniciones vegetales", "estado": "ACTIVO"},
            {"id_categoria": 8, "nombre": "Desayunos", "descripcion": "Combos de desayuno campesino y tradicional", "estado": "ACTIVO"},
            {"id_categoria": 9, "nombre": "Postres", "descripcion": "Postres frios y delicias lacteas", "estado": "ACTIVO"},
            {"id_categoria": 10, "nombre": "Snacks", "descripcion": "Empanadas, pasteles y pasabocas rapidos", "estado": "ACTIVO"},
        ]
        a_db["categorias"].insert_many(a_categorias)
        a_db["contadores"].update_one({"_id": "categorias"}, {"$set": {"seq": 10}}, upsert=True)

    # 3. Insumos
    if a_db["insumos"].count_documents({}) == 0:
        a_insumos = [
            {"id_insumo": 1, "nombre": "Carne de Res Molida", "unidad_medida": "kg", "stock_actual": 25.0, "stock_minimo": 5.0, "costo_unitario": 16000.0, "fecha_vencimiento": "2026-11-15", "estado": "ACTIVO"},
            {"id_insumo": 2, "nombre": "Pechuga de Pollo", "unidad_medida": "kg", "stock_actual": 30.0, "stock_minimo": 6.0, "costo_unitario": 14000.0, "fecha_vencimiento": "2026-11-10", "estado": "ACTIVO"},
            {"id_insumo": 3, "nombre": "Papa Criolla", "unidad_medida": "kg", "stock_actual": 50.0, "stock_minimo": 10.0, "costo_unitario": 3500.0, "fecha_vencimiento": "2026-10-30", "estado": "ACTIVO"},
            {"id_insumo": 4, "nombre": "Lulo Fresco", "unidad_medida": "kg", "stock_actual": 20.0, "stock_minimo": 5.0, "costo_unitario": 4500.0, "fecha_vencimiento": "2026-10-25", "estado": "ACTIVO"},
            {"id_insumo": 5, "nombre": "Café Tostado y Molido", "unidad_medida": "lb", "stock_actual": 15.0, "stock_minimo": 3.0, "costo_unitario": 12000.0, "fecha_vencimiento": "2026-12-31", "estado": "ACTIVO"},
            {"id_insumo": 6, "nombre": "Harina de Maíz", "unidad_medida": "kg", "stock_actual": 40.0, "stock_minimo": 8.0, "costo_unitario": 3800.0, "fecha_vencimiento": "2026-12-15", "estado": "ACTIVO"},
            {"id_insumo": 7, "nombre": "Queso Campesino", "unidad_medida": "kg", "stock_actual": 18.0, "stock_minimo": 4.0, "costo_unitario": 15000.0, "fecha_vencimiento": "2026-11-05", "estado": "ACTIVO"},
            {"id_insumo": 8, "nombre": "Leche Entera", "unidad_medida": "l", "stock_actual": 60.0, "stock_minimo": 12.0, "costo_unitario": 3200.0, "fecha_vencimiento": "2026-10-28", "estado": "ACTIVO"},
            {"id_insumo": 9, "nombre": "Azúcar Refinada", "unidad_medida": "kg", "stock_actual": 35.0, "stock_minimo": 5.0, "costo_unitario": 4000.0, "fecha_vencimiento": "2027-01-31", "estado": "ACTIVO"},
            {"id_insumo": 10, "nombre": "Aceite Vegetal", "unidad_medida": "l", "stock_actual": 25.0, "stock_minimo": 5.0, "costo_unitario": 8500.0, "fecha_vencimiento": "2027-02-28", "estado": "ACTIVO"},
        ]
        a_db["insumos"].insert_many(a_insumos)
        a_db["contadores"].update_one({"_id": "insumos"}, {"$set": {"seq": 10}}, upsert=True)

    # 4. Productos
    if a_db["productos"].count_documents({}) == 0:
        a_productos = [
            {"id_producto": 1, "codigo": "PRD-001", "nombre": "Bandeja Paisa", "descripcion": "Frijol, arroz, carne molida, chicharron, huevo, tajada y arepa", "precio_venta": 18000.0, "unidad_venta": "Porción", "id_categoria": 1, "estado": "DISPONIBLE"},
            {"id_producto": 2, "codigo": "PRD-002", "nombre": "Ajiaco Santafereño", "descripcion": "Sopa tradicional de pollo con tres papas, guascas, crema y alcaparras", "precio_venta": 16000.0, "unidad_venta": "Porción", "id_categoria": 6, "estado": "DISPONIBLE"},
            {"id_producto": 3, "codigo": "PRD-003", "nombre": "Jugo de Lulo", "descripcion": "Jugo natural en agua o leche con fruta fresca seleccionada", "precio_venta": 5000.0, "unidad_venta": "Vaso 12oz", "id_categoria": 3, "estado": "DISPONIBLE"},
            {"id_producto": 4, "codigo": "PRD-004", "nombre": "Café Especial Huila", "descripcion": "Cafe filtrado de origen Huila con notas achocolatadas", "precio_venta": 3500.0, "unidad_venta": "Taza 8oz", "id_categoria": 2, "estado": "DISPONIBLE"},
            {"id_producto": 5, "codigo": "PRD-005", "nombre": "Pan de Bono", "descripcion": "Amasijo tradicional de almidon de yuca y queso costeno", "precio_venta": 2500.0, "unidad_venta": "Unidad", "id_categoria": 4, "estado": "DISPONIBLE"},
            {"id_producto": 6, "codigo": "PRD-006", "nombre": "Empanada de Carne", "descripcion": "Empanada crocante de maiz rellena de carne desmechada y papa", "precio_venta": 3000.0, "unidad_venta": "Unidad", "id_categoria": 10, "estado": "DISPONIBLE"},
            {"id_producto": 7, "codigo": "PRD-007", "nombre": "Postre de Natas", "descripcion": "Postre tradicional a base de leche, nata y almibar de azucar", "precio_venta": 6000.0, "unidad_venta": "Porción", "id_categoria": 9, "estado": "DISPONIBLE"},
            {"id_producto": 8, "codigo": "PRD-008", "nombre": "Cazuela de Mariscos", "descripcion": "Cazuela cremosa de mariscos frescos al estilo pacifico", "precio_venta": 24000.0, "unidad_venta": "Porción", "id_categoria": 1, "estado": "DISPONIBLE"},
            {"id_producto": 9, "codigo": "PRD-009", "nombre": "Chocolate con Queso", "descripcion": "Chocolate caliente santafereño acompanado de tajada de queso campesino", "precio_venta": 5500.0, "unidad_venta": "Porción", "id_categoria": 2, "estado": "DISPONIBLE"},
            {"id_producto": 10, "codigo": "PRD-010", "nombre": "Torta de Zanahoria", "descripcion": "Porcion de torta esponjosa con especias y cubierta de queso crema", "precio_venta": 6500.0, "unidad_venta": "Porción", "id_categoria": 5, "estado": "DISPONIBLE"},
        ]
        a_db["productos"].insert_many(a_productos)
        a_db["contadores"].update_one({"_id": "productos"}, {"$set": {"seq": 10}}, upsert=True)

    # 5. Recetas
    if a_db["recetas"].count_documents({}) == 0:
        a_recetas = [
            {"id_receta": 1, "id_producto": 1, "id_insumo": 1, "cantidad": 0.250},
            {"id_receta": 2, "id_producto": 1, "id_insumo": 10, "cantidad": 0.050},
            {"id_receta": 3, "id_producto": 2, "id_insumo": 2, "cantidad": 0.300},
            {"id_receta": 4, "id_producto": 2, "id_insumo": 3, "cantidad": 0.250},
            {"id_receta": 5, "id_producto": 3, "id_insumo": 4, "cantidad": 0.150},
            {"id_receta": 6, "id_producto": 3, "id_insumo": 9, "cantidad": 0.030},
            {"id_receta": 7, "id_producto": 4, "id_insumo": 5, "cantidad": 0.020},
            {"id_receta": 8, "id_producto": 5, "id_insumo": 7, "cantidad": 0.080},
            {"id_receta": 9, "id_producto": 5, "id_insumo": 8, "cantidad": 0.050},
            {"id_receta": 10, "id_producto": 6, "id_insumo": 1, "cantidad": 0.060},
            {"id_receta": 11, "id_producto": 6, "id_insumo": 3, "cantidad": 0.040},
            {"id_receta": 12, "id_producto": 6, "id_insumo": 6, "cantidad": 0.050},
            {"id_receta": 13, "id_producto": 7, "id_insumo": 8, "cantidad": 0.400},
            {"id_receta": 14, "id_producto": 7, "id_insumo": 9, "cantidad": 0.080},
        ]
        a_db["recetas"].insert_many(a_recetas)
        a_db["contadores"].update_one({"_id": "recetas"}, {"$set": {"seq": 14}}, upsert=True)

    # 6. Proveedores
    if a_db["proveedores"].count_documents({}) == 0:
        a_proveedores = [
            {"id_proveedor": 1, "nit": "900123456-1", "razon_social": "Distribuidora Avícola del Huila S.A.S", "telefono": "3102345678", "correo": "ventas@avicolahuila.com", "direccion": "Calle 10 # 5-20, Pitalito", "estado": "ACTIVO"},
            {"id_proveedor": 2, "nit": "900234567-2", "razon_social": "Carnes y Derivados del Sur", "telefono": "3113456789", "correo": "pedidos@carnesdelsur.com", "direccion": "Carrera 4 # 12-45, Pitalito", "estado": "ACTIVO"},
            {"id_proveedor": 3, "nit": "900345678-3", "razon_social": "Frutas y Verduras La Huerta", "telefono": "3124567890", "correo": "lahuerta@frutas.com", "direccion": "Mercado Mayorista Local 14", "estado": "ACTIVO"},
            {"id_proveedor": 4, "nit": "900456789-4", "razon_social": "Molinos Santa Marta Ltda", "telefono": "3135678901", "correo": "contacto@molinossantamarta.com", "direccion": "Zona Industrial Manzana B", "estado": "ACTIVO"},
            {"id_proveedor": 5, "nit": "900567890-5", "razon_social": "Lácteos San Martín E.U.", "telefono": "3146789012", "correo": "lacteossanmartin@gmail.com", "direccion": "Vereda El Cedro Km 2", "estado": "ACTIVO"},
            {"id_proveedor": 6, "nit": "900678901-6", "razon_social": "Café Especial Pitalito Gourmet", "telefono": "3157890123", "correo": "gerencia@cafepitalito.com", "direccion": "Finca La Esperanza", "estado": "ACTIVO"},
            {"id_proveedor": 7, "nit": "900789012-7", "razon_social": "Abastecedora Andina de Alimentos", "telefono": "3168901234", "correo": "andina@abastecedora.com", "direccion": "Calle 5 # 8-30, Neiva", "estado": "ACTIVO"},
            {"id_proveedor": 8, "nit": "900890123-8", "razon_social": "Distribuidora El Campesino", "telefono": "3179012345", "correo": "ventas@campesino.com", "direccion": "Carrera 7 # 3-18, Pitalito", "estado": "ACTIVO"},
            {"id_proveedor": 9, "nit": "900901234-9", "razon_social": "Harinas y Levaduras del Valle", "telefono": "3180123456", "correo": "servicio@harinasvalle.com", "direccion": "Av Circunvalar # 15-40", "estado": "ACTIVO"},
            {"id_proveedor": 10, "nit": "901012345-0", "razon_social": "Aceites y Grasas del Llano", "telefono": "3191234567", "correo": "pedidos@aceitesllano.com", "direccion": "Parque Agroindustrial Lote 8", "estado": "ACTIVO"},
        ]
        a_db["proveedores"].insert_many(a_proveedores)
        a_db["contadores"].update_one({"_id": "proveedores"}, {"$set": {"seq": 10}}, upsert=True)

    # 7. Clientes
    if a_db["clientes"].count_documents({}) == 0:
        a_clientes = [
            {"id_cliente": 1, "identificacion": "1080123001", "nombres": "Santiago", "apellidos": "Castro", "telefono": "3101112233", "correo": "scastro@correo.com", "tipo_cliente": "APRENDIZ", "estado": "ACTIVO"},
            {"id_cliente": 2, "identificacion": "1080123002", "nombres": "Valentina", "apellidos": "Ochoa", "telefono": "3112223344", "correo": "vochoa@correo.com", "tipo_cliente": "APRENDIZ", "estado": "ACTIVO"},
            {"id_cliente": 3, "identificacion": "1080123003", "nombres": "Mauricio", "apellidos": "Navarro", "telefono": "3123334455", "correo": "mnavarro@sena.edu.co", "tipo_cliente": "INSTRUCTOR", "estado": "ACTIVO"},
            {"id_cliente": 4, "identificacion": "1080123004", "nombres": "Camila", "apellidos": "Zuñiga", "telefono": "3134445566", "correo": "czuniga@sena.edu.co", "tipo_cliente": "INSTRUCTOR", "estado": "ACTIVO"},
            {"id_cliente": 5, "identificacion": "1080123005", "nombres": "Felipe", "apellidos": "Herrera", "telefono": "3145556677", "correo": "fherrera@sena.edu.co", "tipo_cliente": "FUNCIONARIO", "estado": "ACTIVO"},
            {"id_cliente": 6, "identificacion": "1080123006", "nombres": "Gloria", "apellidos": "Amaya", "telefono": "3156667788", "correo": "gamaya@sena.edu.co", "tipo_cliente": "FUNCIONARIO", "estado": "ACTIVO"},
            {"id_cliente": 7, "identificacion": "1080123007", "nombres": "Mateo", "apellidos": "Giraldo", "telefono": "3167778899", "correo": "mgiraldo@empresa.com", "tipo_cliente": "EXTERNO", "estado": "ACTIVO"},
            {"id_cliente": 8, "identificacion": "1080123008", "nombres": "Juliana", "apellidos": "Mora", "telefono": "3178889900", "correo": "jmora@gmail.com", "tipo_cliente": "EXTERNO", "estado": "ACTIVO"},
            {"id_cliente": 9, "identificacion": "1080123009", "nombres": "Diego", "apellidos": "Cardona", "telefono": "3189990011", "correo": "dcardona@correo.com", "tipo_cliente": "APRENDIZ", "estado": "ACTIVO"},
            {"id_cliente": 10, "identificacion": "1080123010", "nombres": "Adriana", "apellidos": "Pineda", "telefono": "3190001122", "correo": "apineda@cliente.com", "tipo_cliente": "EXTERNO", "estado": "ACTIVO"},
        ]
        a_db["clientes"].insert_many(a_clientes)
        a_db["contadores"].update_one({"_id": "clientes"}, {"$set": {"seq": 10}}, upsert=True)

    # 8. Compras
    if a_db["compras"].count_documents({}) == 0:
        a_compras = [
            {
                "id_compra": 1,
                "numero_factura": "FAC-00101",
                "fecha_compra": "2026-10-01T08:30:00",
                "id_proveedor": 2,
                "id_usuario": 1,
                "total": 160000.0,
                "detalles": [{"id_detalle_compra": 1, "id_insumo": 1, "cantidad": 10.0, "costo_unitario": 16000.0, "subtotal": 160000.0}],
            },
            {
                "id_compra": 2,
                "numero_factura": "FAC-00102",
                "fecha_compra": "2026-10-02T09:15:00",
                "id_proveedor": 1,
                "id_usuario": 1,
                "total": 140000.0,
                "detalles": [{"id_detalle_compra": 2, "id_insumo": 2, "cantidad": 10.0, "costo_unitario": 14000.0, "subtotal": 140000.0}],
            },
            {
                "id_compra": 3,
                "numero_factura": "FAC-00103",
                "fecha_compra": "2026-10-03T10:00:00",
                "id_proveedor": 3,
                "id_usuario": 1,
                "total": 115000.0,
                "detalles": [
                    {"id_detalle_compra": 3, "id_insumo": 3, "cantidad": 20.0, "costo_unitario": 3500.0, "subtotal": 70000.0},
                    {"id_detalle_compra": 4, "id_insumo": 4, "cantidad": 10.0, "costo_unitario": 4500.0, "subtotal": 45000.0},
                ],
            },
            {
                "id_compra": 4,
                "numero_factura": "FAC-00104",
                "fecha_compra": "2026-10-05T11:20:00",
                "id_proveedor": 6,
                "id_usuario": 1,
                "total": 120000.0,
                "detalles": [{"id_detalle_compra": 5, "id_insumo": 5, "cantidad": 10.0, "costo_unitario": 12000.0, "subtotal": 120000.0}],
            },
            {
                "id_compra": 5,
                "numero_factura": "FAC-00105",
                "fecha_compra": "2026-10-06T08:45:00",
                "id_proveedor": 5,
                "id_usuario": 1,
                "total": 156000.0,
                "detalles": [
                    {"id_detalle_compra": 6, "id_insumo": 8, "cantidad": 30.0, "costo_unitario": 3200.0, "subtotal": 96000.0},
                    {"id_detalle_compra": 7, "id_insumo": 7, "cantidad": 4.0, "costo_unitario": 15000.0, "subtotal": 60000.0},
                ],
            },
            {
                "id_compra": 6,
                "numero_factura": "FAC-00106",
                "fecha_compra": "2026-10-08T14:10:00",
                "id_proveedor": 4,
                "id_usuario": 1,
                "total": 76000.0,
                "detalles": [{"id_detalle_compra": 8, "id_insumo": 6, "cantidad": 20.0, "costo_unitario": 3800.0, "subtotal": 76000.0}],
            },
            {
                "id_compra": 7,
                "numero_factura": "FAC-00107",
                "fecha_compra": "2026-10-10T09:30:00",
                "id_proveedor": 10,
                "id_usuario": 1,
                "total": 85000.0,
                "detalles": [{"id_detalle_compra": 9, "id_insumo": 10, "cantidad": 10.0, "costo_unitario": 8500.0, "subtotal": 85000.0}],
            },
            {
                "id_compra": 8,
                "numero_factura": "FAC-00108",
                "fecha_compra": "2026-10-12T10:40:00",
                "id_proveedor": 3,
                "id_usuario": 1,
                "total": 45000.0,
                "detalles": [{"id_detalle_compra": 10, "id_insumo": 4, "cantidad": 10.0, "costo_unitario": 4500.0, "subtotal": 45000.0}],
            },
            {
                "id_compra": 9,
                "numero_factura": "FAC-00109",
                "fecha_compra": "2026-10-14T15:00:00",
                "id_proveedor": 5,
                "id_usuario": 1,
                "total": 75000.0,
                "detalles": [{"id_detalle_compra": 11, "id_insumo": 7, "cantidad": 5.0, "costo_unitario": 15000.0, "subtotal": 75000.0}],
            },
            {
                "id_compra": 10,
                "numero_factura": "FAC-00110",
                "fecha_compra": "2026-10-16T11:00:00",
                "id_proveedor": 2,
                "id_usuario": 1,
                "total": 80000.0,
                "detalles": [{"id_detalle_compra": 12, "id_insumo": 1, "cantidad": 5.0, "costo_unitario": 16000.0, "subtotal": 80000.0}],
            },
        ]
        a_db["compras"].insert_many(a_compras)
        a_db["contadores"].update_one({"_id": "compras"}, {"$set": {"seq": 10}}, upsert=True)

    # 9. Pedidos
    if a_db["pedidos"].count_documents({}) == 0:
        a_pedidos = [
            {"id_pedido": 1, "fecha_pedido": "2026-10-10T12:15:00", "id_cliente": 1, "id_usuario": 2, "tipo_pedido": "MESA", "estado": "ENTREGADO", "total": 23000.0, "observaciones": "Mesa 4", "detalles": [{"id_detalle": 1, "id_producto": 1, "cantidad": 1, "precio_unitario": 18000.0, "subtotal": 18000.0}, {"id_detalle": 2, "id_producto": 3, "cantidad": 1, "precio_unitario": 5000.0, "subtotal": 5000.0}]},
            {"id_pedido": 2, "fecha_pedido": "2026-10-10T12:30:00", "id_cliente": 2, "id_usuario": 2, "tipo_pedido": "PARA_LLEVAR", "estado": "ENTREGADO", "total": 16000.0, "observaciones": "Empaque biodegradable", "detalles": [{"id_detalle": 3, "id_producto": 2, "cantidad": 1, "precio_unitario": 16000.0, "subtotal": 16000.0}]},
            {"id_pedido": 3, "fecha_pedido": "2026-10-11T13:00:00", "id_cliente": 3, "id_usuario": 2, "tipo_pedido": "MESA", "estado": "ENTREGADO", "total": 21500.0, "observaciones": "Mesa instructores", "detalles": [{"id_detalle": 4, "id_producto": 1, "cantidad": 1, "precio_unitario": 18000.0, "subtotal": 18000.0}, {"id_detalle": 5, "id_producto": 4, "cantidad": 1, "precio_unitario": 3500.0, "subtotal": 3500.0}]},
            {"id_pedido": 4, "fecha_pedido": "2026-10-12T12:45:00", "id_cliente": 4, "id_usuario": 2, "tipo_pedido": "EVENTO", "estado": "ENTREGADO", "total": 36000.0, "observaciones": "Reunion coordinacion", "detalles": [{"id_detalle": 6, "id_producto": 1, "cantidad": 2, "precio_unitario": 18000.0, "subtotal": 36000.0}]},
            {"id_pedido": 5, "fecha_pedido": "2026-10-13T13:15:00", "id_cliente": 5, "id_usuario": 5, "tipo_pedido": "MESA", "estado": "ENTREGADO", "total": 18000.0, "observaciones": "Mesa 2", "detalles": [{"id_detalle": 7, "id_producto": 1, "cantidad": 1, "precio_unitario": 18000.0, "subtotal": 18000.0}]},
            {"id_pedido": 6, "fecha_pedido": "2026-10-14T12:20:00", "id_cliente": 6, "id_usuario": 5, "tipo_pedido": "PARA_LLEVAR", "estado": "ENTREGADO", "total": 8500.0, "observaciones": "Llevar a oficina", "detalles": [{"id_detalle": 8, "id_producto": 6, "cantidad": 2, "precio_unitario": 3000.0, "subtotal": 6000.0}, {"id_detalle": 9, "id_producto": 5, "cantidad": 1, "precio_unitario": 2500.0, "subtotal": 2500.0}]},
            {"id_pedido": 7, "fecha_pedido": "2026-10-15T12:35:00", "id_cliente": 7, "id_usuario": 2, "tipo_pedido": "MESA", "estado": "EN_PREPARACION", "total": 24000.0, "observaciones": "Mesa 6", "detalles": [{"id_detalle": 10, "id_producto": 8, "cantidad": 1, "precio_unitario": 24000.0, "subtotal": 24000.0}]},
            {"id_pedido": 8, "fecha_pedido": "2026-10-16T12:50:00", "id_cliente": 8, "id_usuario": 2, "tipo_pedido": "MESA", "estado": "PENDIENTE", "total": 19500.0, "observaciones": "Cliente nuevo", "detalles": [{"id_detalle": 11, "id_producto": 2, "cantidad": 1, "precio_unitario": 16000.0, "subtotal": 16000.0}, {"id_detalle": 12, "id_producto": 4, "cantidad": 1, "precio_unitario": 3500.0, "subtotal": 3500.0}]},
            {"id_pedido": 9, "fecha_pedido": "2026-10-16T13:05:00", "id_cliente": 9, "id_usuario": 5, "tipo_pedido": "PARA_LLEVAR", "estado": "PENDIENTE", "total": 10500.0, "observaciones": "Recoge en barra", "detalles": [{"id_detalle": 13, "id_producto": 6, "cantidad": 2, "precio_unitario": 3000.0, "subtotal": 6000.0}, {"id_detalle": 14, "id_producto": 5, "cantidad": 1, "precio_unitario": 2500.0, "subtotal": 2500.0}, {"id_detalle": 15, "id_producto": 4, "cantidad": 1, "precio_unitario": 2000.0, "subtotal": 2000.0}]},
            {"id_pedido": 10, "fecha_pedido": "2026-10-16T13:20:00", "id_cliente": 10, "id_usuario": 2, "tipo_pedido": "MESA", "estado": "ANULADO", "total": 18000.0, "observaciones": "Cancelado", "detalles": [{"id_detalle": 16, "id_producto": 1, "cantidad": 1, "precio_unitario": 18000.0, "subtotal": 18000.0}]},
        ]
        a_db["pedidos"].insert_many(a_pedidos)
        a_db["contadores"].update_one({"_id": "pedidos"}, {"$set": {"seq": 10}}, upsert=True)

    # 10. Calificaciones
    if a_db["calificaciones"].count_documents({}) == 0:
        a_calificaciones = [
            {
                "id_pedido": 1,
                "id_cliente": 1,
                "fecha": "2026-10-10T12:45:00",
                "calificacion_servicio": 5,
                "comentario": "Excelente sabor tradicional y atencion muy rapida en la mesa.",
                "productos": [
                    {"id_producto": 1, "nombre": "Bandeja Paisa", "calificacion": 5},
                    {"id_producto": 3, "nombre": "Jugo de Lulo", "calificacion": 5},
                ],
            },
            {
                "id_pedido": 2,
                "id_cliente": 2,
                "fecha": "2026-10-10T13:10:00",
                "calificacion_servicio": 4,
                "comentario": "El ajiaco estaba delicioso, llego bien caliente el empaque.",
                "productos": [
                    {"id_producto": 2, "nombre": "Ajiaco Santafereño", "calificacion": 5}
                ],
            },
            {
                "id_pedido": 3,
                "id_cliente": 3,
                "fecha": "2026-10-11T13:40:00",
                "calificacion_servicio": 5,
                "comentario": "El cafe huilense tiene un aroma inigualable. Gran preparacion.",
                "productos": [
                    {"id_producto": 1, "nombre": "Bandeja Paisa", "calificacion": 4},
                    {"id_producto": 4, "nombre": "Café Especial Huila", "calificacion": 5},
                ],
            },
            {
                "id_pedido": 4,
                "id_cliente": 4,
                "fecha": "2026-10-12T13:30:00",
                "calificacion_servicio": 5,
                "comentario": "Excelente servicio para eventos de coordinacion.",
                "productos": [
                    {"id_producto": 1, "nombre": "Bandeja Paisa", "calificacion": 5}
                ],
            },
            {
                "id_pedido": 5,
                "id_cliente": 5,
                "fecha": "2026-10-13T13:50:00",
                "calificacion_servicio": 4,
                "comentario": "Porcion generosa y presentacion impecable.",
                "productos": [
                    {"id_producto": 1, "nombre": "Bandeja Paisa", "calificacion": 4}
                ],
            },
            {
                "id_pedido": 6,
                "id_cliente": 6,
                "fecha": "2026-10-14T12:55:00",
                "calificacion_servicio": 5,
                "comentario": "Las empanadas y el pan de bono recien horneados estaban increibles.",
                "productos": [
                    {"id_producto": 6, "nombre": "Empanada de Carne", "calificacion": 5},
                    {"id_producto": 5, "nombre": "Pan de Bono", "calificacion": 5},
                ],
            },
        ]
        a_db["calificaciones"].insert_many(a_calificaciones)
