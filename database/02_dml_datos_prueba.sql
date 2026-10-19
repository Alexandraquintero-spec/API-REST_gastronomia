-- ============================================================
-- PROYECTO FORMATIVO: API REST GASTRONOMIA - SENA CGDSS
-- FICHA: 3312744
-- INSTRUCTIVO: EA4
-- SCRIPT: 02_dml_datos_prueba.sql
-- MOTOR: MySQL 8.0
-- DESCRIPCIÓN: Datos iniciales de prueba (mínimo 10 registros por tabla)
-- ============================================================

USE bd_gastronomia;

-- Desactivar chequeo de claves foráneas para carga limpia si es necesario
SET FOREIGN_KEY_CHECKS = 0;

TRUNCATE TABLE detalle_pedido;
TRUNCATE TABLE pedidos;
TRUNCATE TABLE detalle_compra;
TRUNCATE TABLE compras;
TRUNCATE TABLE recetas;
TRUNCATE TABLE insumos;
TRUNCATE TABLE productos;
TRUNCATE TABLE categorias;
TRUNCATE TABLE proveedores;
TRUNCATE TABLE clientes;
TRUNCATE TABLE usuarios;

SET FOREIGN_KEY_CHECKS = 1;

-- ------------------------------------------------------------
-- 1. Tabla: usuarios (10 registros, con contraseñas bcrypt reales)
-- Contraseñas:
-- Admin: Admin123* -> $2b$12$GKkTxCowjiv6x2OWGbIKseRaXoD1RL.F2KpMTc2yV6RSZPkVNwvSW
-- Cajero: Cajero123* -> $2b$12$zJdvOT/zpRV.JgbdEj59T.6e9zaIVL0AAMwLbZvJdnEaHaq9/gp/O
-- Cocinero: Cocinero123* -> $2b$12$Y5oiK..7JfH0XFDwHNoTv.FroHiqCcRj5olCvbWYp9OF3UkzMCjpu
-- ------------------------------------------------------------
INSERT INTO usuarios (id_usuario, identificacion, nombres, apellidos, correo, password, rol, estado) VALUES
(1, '1075234001', 'Wilson', 'Gomez', 'admin@gastronomia.sena.edu.co', '$2b$12$GKkTxCowjiv6x2OWGbIKseRaXoD1RL.F2KpMTc2yV6RSZPkVNwvSW', 'ADMIN', 'ACTIVO'),
(2, '1075234002', 'Laura', 'Sanchez', 'cajero@gastronomia.sena.edu.co', '$2b$12$zJdvOT/zpRV.JgbdEj59T.6e9zaIVL0AAMwLbZvJdnEaHaq9/gp/O', 'CAJERO', 'ACTIVO'),
(3, '1075234003', 'Carlos', 'Mejia', 'cocinero@gastronomia.sena.edu.co', '$2b$12$Y5oiK..7JfH0XFDwHNoTv.FroHiqCcRj5olCvbWYp9OF3UkzMCjpu', 'COCINERO', 'ACTIVO'),
(4, '1075234004', 'Andres', 'Perez', 'admin2@gastronomia.sena.edu.co', '$2b$12$GKkTxCowjiv6x2OWGbIKseRaXoD1RL.F2KpMTc2yV6RSZPkVNwvSW', 'ADMIN', 'ACTIVO'),
(5, '1075234005', 'Diana', 'Torres', 'cajero2@gastronomia.sena.edu.co', '$2b$12$zJdvOT/zpRV.JgbdEj59T.6e9zaIVL0AAMwLbZvJdnEaHaq9/gp/O', 'CAJERO', 'ACTIVO'),
(6, '1075234006', 'Javier', 'Ramirez', 'cocinero2@gastronomia.sena.edu.co', '$2b$12$Y5oiK..7JfH0XFDwHNoTv.FroHiqCcRj5olCvbWYp9OF3UkzMCjpu', 'COCINERO', 'ACTIVO'),
(7, '1075234007', 'Paola', 'Vargas', 'cajero3@gastronomia.sena.edu.co', '$2b$12$zJdvOT/zpRV.JgbdEj59T.6e9zaIVL0AAMwLbZvJdnEaHaq9/gp/O', 'CAJERO', 'ACTIVO'),
(8, '1075234008', 'Hernan', 'Duarte', 'cocinero3@gastronomia.sena.edu.co', '$2b$12$Y5oiK..7JfH0XFDwHNoTv.FroHiqCcRj5olCvbWYp9OF3UkzMCjpu', 'COCINERO', 'ACTIVO'),
(9, '1075234009', 'Sonia', 'Castillo', 'cajero4@gastronomia.sena.edu.co', '$2b$12$zJdvOT/zpRV.JgbdEj59T.6e9zaIVL0AAMwLbZvJdnEaHaq9/gp/O', 'CAJERO', 'ACTIVO'),
(10, '1075234010', 'Alberto', 'Rios', 'admin3@gastronomia.sena.edu.co', '$2b$12$GKkTxCowjiv6x2OWGbIKseRaXoD1RL.F2KpMTc2yV6RSZPkVNwvSW', 'ADMIN', 'ACTIVO');

-- ------------------------------------------------------------
-- 2. Tabla: categorias (10 registros)
-- ------------------------------------------------------------
INSERT INTO categorias (id_categoria, nombre, descripcion, estado) VALUES
(1, 'Platos Fuertes', 'Platos principales tradicionales y a la carta', 'ACTIVO'),
(2, 'Bebidas Calientes', 'Cafés, chocolates e infusiones tradicionales', 'ACTIVO'),
(3, 'Bebidas Frías', 'Jugos naturales, limonadas y refrescos', 'ACTIVO'),
(4, 'Panadería', 'Panes artesanales y amasijos tradicionales', 'ACTIVO'),
(5, 'Repostería', 'Tortas, postres y dulces horneados', 'ACTIVO'),
(6, 'Sopas', 'Caldos, cremas y sopas típicas', 'ACTIVO'),
(7, 'Ensaladas', 'Ensaladas frescas y guarniciones vegetales', 'ACTIVO'),
(8, 'Desayunos', 'Combos de desayuno campesino y tradicional', 'ACTIVO'),
(9, 'Postres', 'Postres fríos y delicias lácteas', 'ACTIVO'),
(10, 'Snacks', 'Empanadas, pasteles y pasabocas rápidos', 'ACTIVO');

-- ------------------------------------------------------------
-- 3. Tabla: productos (10 registros)
-- ------------------------------------------------------------
INSERT INTO productos (id_producto, codigo, nombre, descripcion, precio_venta, unidad_venta, id_categoria, estado) VALUES
(1, 'PRD-001', 'Bandeja Paisa', 'Frijol, arroz, carne molida, chicharron, huevo, tajada y arepa', 18000.00, 'Porción', 1, 'DISPONIBLE'),
(2, 'PRD-002', 'Ajiaco Santafereño', 'Sopa tradicional de pollo con tres papas, guascas, crema y alcaparras', 16000.00, 'Porción', 6, 'DISPONIBLE'),
(3, 'PRD-003', 'Jugo de Lulo', 'Jugo natural en agua o leche con fruta fresca seleccionada', 5000.00, 'Vaso 12oz', 3, 'DISPONIBLE'),
(4, 'PRD-004', 'Café Especial Huila', 'Café filtrado de origen Huila con notas achocolatadas', 3500.00, 'Taza 8oz', 2, 'DISPONIBLE'),
(5, 'PRD-005', 'Pan de Bono', 'Amasijo tradicional de almidon de yuca y queso costeno', 2500.00, 'Unidad', 4, 'DISPONIBLE'),
(6, 'PRD-006', 'Empanada de Carne', 'Empanada crocante de maiz rellena de carne desmechada y papa', 3000.00, 'Unidad', 10, 'DISPONIBLE'),
(7, 'PRD-007', 'Postre de Natas', 'Postre tradicional a base de leche, nata y almibar de azucar', 6000.00, 'Porción', 9, 'DISPONIBLE'),
(8, 'PRD-008', 'Cazuela de Mariscos', 'Cazuela cremosa de mariscos frescos al estilo pacífico', 24000.00, 'Porción', 1, 'DISPONIBLE'),
(9, 'PRD-009', 'Chocolate con Queso', 'Chocolate caliente santafereño acompanado de tajada de queso campesino', 5500.00, 'Porción', 2, 'DISPONIBLE'),
(10, 'PRD-010', 'Torta de Zanahoria', 'Porcion de torta esponjosa con especias y cubierta de queso crema', 6500.00, 'Porción', 5, 'DISPONIBLE');

-- ------------------------------------------------------------
-- 4. Tabla: insumos (10 registros)
-- ------------------------------------------------------------
INSERT INTO insumos (id_insumo, nombre, unidad_medida, stock_actual, stock_minimo, costo_unitario, fecha_vencimiento, estado) VALUES
(1, 'Carne de Res Molida', 'kg', 25.00, 5.00, 16000.00, '2026-11-15', 'ACTIVO'),
(2, 'Pechuga de Pollo', 'kg', 30.00, 6.00, 14000.00, '2026-11-10', 'ACTIVO'),
(3, 'Papa Criolla', 'kg', 50.00, 10.00, 3500.00, '2026-10-30', 'ACTIVO'),
(4, 'Lulo Fresco', 'kg', 20.00, 5.00, 4500.00, '2026-10-25', 'ACTIVO'),
(5, 'Café Tostado y Molido', 'lb', 15.00, 3.00, 12000.00, '2026-12-31', 'ACTIVO'),
(6, 'Harina de Maíz', 'kg', 40.00, 8.00, 3800.00, '2026-12-15', 'ACTIVO'),
(7, 'Queso Campesino', 'kg', 18.00, 4.00, 15000.00, '2026-11-05', 'ACTIVO'),
(8, 'Leche Entera', 'l', 60.00, 12.00, 3200.00, '2026-10-28', 'ACTIVO'),
(9, 'Azúcar Refinada', 'kg', 35.00, 5.00, 4000.00, '2027-01-31', 'ACTIVO'),
(10, 'Aceite Vegetal', 'l', 25.00, 5.00, 8500.00, '2027-02-28', 'ACTIVO');

-- ------------------------------------------------------------
-- 5. Tabla: recetas (ficha técnica - 14 relaciones producto-insumo)
-- ------------------------------------------------------------
INSERT INTO recetas (id_receta, id_producto, id_insumo, cantidad) VALUES
(1, 1, 1, 0.250), -- Bandeja Paisa: 0.250 kg Carne
(2, 1, 10, 0.050), -- Bandeja Paisa: 0.050 L Aceite
(3, 2, 2, 0.300), -- Ajiaco: 0.300 kg Pollo
(4, 2, 3, 0.250), -- Ajiaco: 0.250 kg Papa Criolla
(5, 3, 4, 0.150), -- Jugo de Lulo: 0.150 kg Lulo
(6, 3, 9, 0.030), -- Jugo de Lulo: 0.030 kg Azúcar
(7, 4, 5, 0.020), -- Café Especial: 0.020 lb Café
(8, 5, 7, 0.080), -- Pan de Bono: 0.080 kg Queso
(9, 5, 8, 0.050), -- Pan de Bono: 0.050 L Leche
(10, 6, 1, 0.060), -- Empanada: 0.060 kg Carne
(11, 6, 3, 0.040), -- Empanada: 0.040 kg Papa
(12, 6, 6, 0.050), -- Empanada: 0.050 kg Harina Maiz
(13, 7, 8, 0.400), -- Postre Natas: 0.400 L Leche
(14, 7, 9, 0.080); -- Postre Natas: 0.080 kg Azúcar

-- ------------------------------------------------------------
-- 6. Tabla: proveedores (10 registros)
-- ------------------------------------------------------------
INSERT INTO proveedores (id_proveedor, nit, razon_social, telefono, correo, direccion, estado) VALUES
(1, '900123456-1', 'Distribuidora Avícola del Huila S.A.S', '3102345678', 'ventas@avicolahuila.com', 'Calle 10 # 5-20, Pitalito', 'ACTIVO'),
(2, '900234567-2', 'Carnes y Derivados del Sur', '3113456789', 'pedidos@carnesdelsur.com', 'Carrera 4 # 12-45, Pitalito', 'ACTIVO'),
(3, '900345678-3', 'Frutas y Verduras La Huerta', '3124567890', 'lahuerta@frutas.com', 'Mercado Mayorista Local 14', 'ACTIVO'),
(4, '900456789-4', 'Molinos Santa Marta Ltda', '3135678901', 'contacto@molinossantamarta.com', 'Zona Industrial Manzana B', 'ACTIVO'),
(5, '900567890-5', 'Lácteos San Martín E.U.', '3146789012', 'lacteossanmartin@gmail.com', 'Vereda El Cedro Km 2', 'ACTIVO'),
(6, '900678901-6', 'Café Especial Pitalito Gourmet', '3157890123', 'gerencia@cafepitalito.com', 'Finca La Esperanza', 'ACTIVO'),
(7, '900789012-7', 'Abastecedora Andina de Alimentos', '3168901234', 'andina@abastecedora.com', 'Calle 5 # 8-30, Neiva', 'ACTIVO'),
(8, '900890123-8', 'Distribuidora El Campesino', '3179012345', 'ventas@campesino.com', 'Carrera 7 # 3-18, Pitalito', 'ACTIVO'),
(9, '900901234-9', 'Harinas y Levaduras del Valle', '3180123456', 'servicio@harinasvalle.com', 'Av Circunvalar # 15-40', 'ACTIVO'),
(10, '901012345-0', 'Aceites y Grasas del Llano', '3191234567', 'pedidos@aceitesllano.com', 'Parque Agroindustrial Lote 8', 'ACTIVO');

-- ------------------------------------------------------------
-- 7. Tabla: compras (10 registros)
-- ------------------------------------------------------------
INSERT INTO compras (id_compra, numero_factura, fecha_compra, id_proveedor, id_usuario, total) VALUES
(1, 'FAC-00101', '2026-10-01 08:30:00', 2, 1, 160000.00),
(2, 'FAC-00102', '2026-10-02 09:15:00', 1, 1, 140000.00),
(3, 'FAC-00103', '2026-10-03 10:00:00', 3, 1, 70000.00),
(4, 'FAC-00104', '2026-10-05 11:20:00', 6, 1, 120000.00),
(5, 'FAC-00105', '2026-10-06 08:45:00', 5, 1, 96000.00),
(6, 'FAC-00106', '2026-10-08 14:10:00', 4, 1, 76000.00),
(7, 'FAC-00107', '2026-10-10 09:30:00', 10, 1, 85000.00),
(8, 'FAC-00108', '2026-10-12 10:40:00', 3, 1, 45000.00),
(9, 'FAC-00109', '2026-10-14 15:00:00', 5, 1, 75000.00),
(10, 'FAC-00110', '2026-10-16 11:00:00', 2, 1, 80000.00);

-- ------------------------------------------------------------
-- 8. Tabla: detalle_compra (12 registros)
-- ------------------------------------------------------------
INSERT INTO detalle_compra (id_detalle_compra, id_compra, id_insumo, cantidad, costo_unitario, subtotal) VALUES
(1, 1, 1, 10.00, 16000.00, 160000.00),
(2, 2, 2, 10.00, 14000.00, 140000.00),
(3, 3, 3, 20.00, 3500.00, 70000.00),
(4, 4, 5, 10.00, 12000.00, 120000.00),
(5, 5, 8, 30.00, 3200.00, 96000.00),
(6, 6, 6, 20.00, 3800.00, 76000.00),
(7, 7, 10, 10.00, 8500.00, 85000.00),
(8, 8, 4, 10.00, 4500.00, 45000.00),
(9, 9, 7, 5.00, 15000.00, 75000.00),
(10, 10, 1, 5.00, 16000.00, 80000.00),
(11, 3, 4, 10.00, 4500.00, 45000.00),
(12, 5, 7, 4.00, 15000.00, 60000.00);

-- ------------------------------------------------------------
-- 9. Tabla: clientes (10 registros)
-- ------------------------------------------------------------
INSERT INTO clientes (id_cliente, identificacion, nombres, apellidos, telefono, correo, tipo_cliente, estado) VALUES
(1, '1080123001', 'Santiago', 'Castro', '3101112233', 'scastro@correo.com', 'APRENDIZ', 'ACTIVO'),
(2, '1080123002', 'Valentina', 'Ochoa', '3112223344', 'vochoa@correo.com', 'APRENDIZ', 'ACTIVO'),
(3, '1080123003', 'Mauricio', 'Navarro', '3123334455', 'mnavarro@sena.edu.co', 'INSTRUCTOR', 'ACTIVO'),
(4, '1080123004', 'Camila', 'Zuñiga', '3134445566', 'czuniga@sena.edu.co', 'INSTRUCTOR', 'ACTIVO'),
(5, '1080123005', 'Felipe', 'Herrera', '3145556677', 'fherrera@sena.edu.co', 'FUNCIONARIO', 'ACTIVO'),
(6, '1080123006', 'Gloria', 'Amaya', '3156667788', 'gamaya@sena.edu.co', 'FUNCIONARIO', 'ACTIVO'),
(7, '1080123007', 'Mateo', 'Giraldo', '3167778899', 'mgiraldo@empresa.com', 'EXTERNO', 'ACTIVO'),
(8, '1080123008', 'Juliana', 'Mora', '3178889900', 'jmora@gmail.com', 'EXTERNO', 'ACTIVO'),
(9, '1080123009', 'Diego', 'Cardona', '3189990011', 'dcardona@correo.com', 'APRENDIZ', 'ACTIVO'),
(10, '1080123010', 'Adriana', 'Pineda', '3190001122', 'apineda@cliente.com', 'EXTERNO', 'ACTIVO');

-- ------------------------------------------------------------
-- 10. Tabla: pedidos (10 registros)
-- ------------------------------------------------------------
INSERT INTO pedidos (id_pedido, fecha_pedido, id_cliente, id_usuario, tipo_pedido, estado, total, observaciones) VALUES
(1, '2026-10-10 12:15:00', 1, 2, 'MESA', 'ENTREGADO', 23000.00, 'Mesa 4, sin cebolla en el plato'),
(2, '2026-10-10 12:30:00', 2, 2, 'PARA_LLEVAR', 'ENTREGADO', 16000.00, 'Empaque biodegradable'),
(3, '2026-10-11 13:00:00', 3, 2, 'MESA', 'ENTREGADO', 21500.00, 'Mesa de instructores'),
(4, '2026-10-12 12:45:00', 4, 2, 'EVENTO', 'ENTREGADO', 36000.00, 'Reunión de coordinación'),
(5, '2026-10-13 13:15:00', 5, 5, 'MESA', 'ENTREGADO', 18000.00, 'Mesa 2'),
(6, '2026-10-14 12:20:00', 6, 5, 'PARA_LLEVAR', 'ENTREGADO', 8500.00, 'Para llevar a oficina administrativa'),
(7, '2026-10-15 12:35:00', 7, 2, 'MESA', 'EN_PREPARACION', 24000.00, 'Mesa 6'),
(8, '2026-10-16 12:50:00', 8, 2, 'MESA', 'PENDIENTE', 19500.00, 'Cliente nuevo'),
(9, '2026-10-16 13:05:00', 9, 5, 'PARA_LLEVAR', 'PENDIENTE', 10500.00, 'Recoge en barra'),
(10, '2026-10-16 13:20:00', 10, 2, 'MESA', 'ANULADO', 18000.00, 'Cliente debió retirarse por urgencia');

-- ------------------------------------------------------------
-- 11. Tabla: detalle_pedido (15 registros)
-- ------------------------------------------------------------
INSERT INTO detalle_pedido (id_detalle, id_pedido, id_producto, cantidad, precio_unitario, subtotal) VALUES
(1, 1, 1, 1, 18000.00, 18000.00), -- Bandeja Paisa
(2, 1, 3, 1, 5000.00, 5000.00),   -- Jugo Lulo
(3, 2, 2, 1, 16000.00, 16000.00), -- Ajiaco
(4, 3, 1, 1, 18000.00, 18000.00), -- Bandeja Paisa
(5, 3, 4, 1, 3500.00, 3500.00),   -- Café Especial
(6, 4, 1, 2, 18000.00, 36000.00), -- 2 Bandejas Paisas
(7, 5, 1, 1, 18000.00, 18000.00), -- Bandeja Paisa
(8, 6, 6, 2, 3000.00, 6000.00),   -- 2 Empanadas
(9, 6, 5, 1, 2500.00, 2500.00),   -- 1 Pan de bono
(10, 7, 8, 1, 24000.00, 24000.00), -- Cazuela
(11, 8, 2, 1, 16000.00, 16000.00), -- Ajiaco
(12, 8, 4, 1, 3500.00, 3500.00),   -- Café
(13, 9, 6, 2, 3000.00, 6000.00),   -- 2 Empanadas
(14, 9, 5, 1, 2500.00, 2500.00),   -- 1 Pan de bono
(15, 9, 4, 1, 2000.00, 2000.00);   -- 1 Café
