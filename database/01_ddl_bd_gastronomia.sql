-- ============================================================
-- PROYECTO FORMATIVO: API REST GASTRONOMIA - SENA CGDSS
-- FICHA: 3312744
-- INSTRUCTIVO: EA4
-- SCRIPT: 01_ddl_bd_gastronomia.sql
-- MOTOR: MySQL 8.0
-- CHARSET: utf8mb4 | COLLATION: utf8mb4_unicode_ci
-- ============================================================

CREATE DATABASE IF NOT EXISTS bd_gastronomia
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE bd_gastronomia;

-- ------------------------------------------------------------
-- 1. Tabla: usuarios
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
  id_usuario INT AUTO_INCREMENT PRIMARY KEY,
  identificacion VARCHAR(20) NOT NULL,
  nombres VARCHAR(80) NOT NULL,
  apellidos VARCHAR(80) NOT NULL,
  correo VARCHAR(120) NOT NULL,
  password VARCHAR(255) NOT NULL,
  rol ENUM('ADMIN', 'CAJERO', 'COCINERO') NOT NULL,
  estado ENUM('ACTIVO', 'INACTIVO') NOT NULL DEFAULT 'ACTIVO',
  CONSTRAINT uq_usuario_identificacion UNIQUE (identificacion),
  CONSTRAINT uq_usuario_correo UNIQUE (correo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 2. Tabla: categorias
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS categorias (
  id_categoria INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(60) NOT NULL,
  descripcion VARCHAR(200) NULL,
  estado ENUM('ACTIVO', 'INACTIVO') NOT NULL DEFAULT 'ACTIVO',
  CONSTRAINT uq_categoria_nombre UNIQUE (nombre)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 3. Tabla: productos
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS productos (
  id_producto INT AUTO_INCREMENT PRIMARY KEY,
  codigo VARCHAR(20) NOT NULL,
  nombre VARCHAR(100) NOT NULL,
  descripcion TEXT NULL,
  precio_venta DECIMAL(10,2) NOT NULL,
  unidad_venta VARCHAR(20) NOT NULL,
  id_categoria INT NOT NULL,
  estado ENUM('DISPONIBLE', 'AGOTADO', 'INACTIVO') NOT NULL DEFAULT 'DISPONIBLE',
  CONSTRAINT uq_producto_codigo UNIQUE (codigo),
  CONSTRAINT chk_producto_precio CHECK (precio_venta > 0),
  CONSTRAINT fk_producto_categoria FOREIGN KEY (id_categoria)
    REFERENCES categorias(id_categoria)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 4. Tabla: insumos
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS insumos (
  id_insumo INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  unidad_medida ENUM('g', 'kg', 'ml', 'l', 'lb', 'unidad') NOT NULL,
  stock_actual DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  stock_minimo DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  costo_unitario DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  fecha_vencimiento DATE NULL,
  estado ENUM('ACTIVO', 'INACTIVO') NOT NULL DEFAULT 'ACTIVO',
  CONSTRAINT uq_insumo_nombre UNIQUE (nombre),
  CONSTRAINT chk_insumo_stock_actual CHECK (stock_actual >= 0),
  CONSTRAINT chk_insumo_stock_minimo CHECK (stock_minimo >= 0),
  CONSTRAINT chk_insumo_costo CHECK (costo_unitario >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 5. Tabla: recetas (ficha técnica)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recetas (
  id_receta INT AUTO_INCREMENT PRIMARY KEY,
  id_producto INT NOT NULL,
  id_insumo INT NOT NULL,
  cantidad DECIMAL(10,3) NOT NULL,
  CONSTRAINT chk_receta_cantidad CHECK (cantidad > 0),
  CONSTRAINT fk_receta_producto FOREIGN KEY (id_producto)
    REFERENCES productos(id_producto)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT fk_receta_insumo FOREIGN KEY (id_insumo)
    REFERENCES insumos(id_insumo)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 6. Tabla: proveedores
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS proveedores (
  id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
  nit VARCHAR(20) NOT NULL,
  razon_social VARCHAR(120) NOT NULL,
  telefono VARCHAR(20) NULL,
  correo VARCHAR(120) NULL,
  direccion VARCHAR(150) NULL,
  estado ENUM('ACTIVO', 'INACTIVO') NOT NULL DEFAULT 'ACTIVO',
  CONSTRAINT uq_proveedor_nit UNIQUE (nit)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 7. Tabla: compras
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS compras (
  id_compra INT AUTO_INCREMENT PRIMARY KEY,
  numero_factura VARCHAR(30) NOT NULL,
  fecha_compra DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  id_proveedor INT NOT NULL,
  id_usuario INT NOT NULL,
  total DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  CONSTRAINT fk_compra_proveedor FOREIGN KEY (id_proveedor)
    REFERENCES proveedores(id_proveedor)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT fk_compra_usuario FOREIGN KEY (id_usuario)
    REFERENCES usuarios(id_usuario)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 8. Tabla: detalle_compra
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS detalle_compra (
  id_detalle_compra INT AUTO_INCREMENT PRIMARY KEY,
  id_compra INT NOT NULL,
  id_insumo INT NOT NULL,
  cantidad DECIMAL(10,2) NOT NULL,
  costo_unitario DECIMAL(10,2) NOT NULL,
  subtotal DECIMAL(12,2) NOT NULL,
  CONSTRAINT chk_detcompra_cantidad CHECK (cantidad > 0),
  CONSTRAINT chk_detcompra_costo CHECK (costo_unitario >= 0),
  CONSTRAINT chk_detcompra_subtotal CHECK (subtotal >= 0),
  CONSTRAINT fk_detcompra_compra FOREIGN KEY (id_compra)
    REFERENCES compras(id_compra)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_detcompra_insumo FOREIGN KEY (id_insumo)
    REFERENCES insumos(id_insumo)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 9. Tabla: clientes
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS clientes (
  id_cliente INT AUTO_INCREMENT PRIMARY KEY,
  identificacion VARCHAR(20) NOT NULL,
  nombres VARCHAR(80) NOT NULL,
  apellidos VARCHAR(80) NOT NULL,
  telefono VARCHAR(20) NULL,
  correo VARCHAR(120) NULL,
  tipo_cliente ENUM('APRENDIZ', 'INSTRUCTOR', 'FUNCIONARIO', 'EXTERNO') NOT NULL,
  estado ENUM('ACTIVO', 'INACTIVO') NOT NULL DEFAULT 'ACTIVO',
  CONSTRAINT uq_cliente_identificacion UNIQUE (identificacion)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 10. Tabla: pedidos
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS pedidos (
  id_pedido INT AUTO_INCREMENT PRIMARY KEY,
  fecha_pedido DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  id_cliente INT NOT NULL,
  id_usuario INT NOT NULL,
  tipo_pedido ENUM('MESA', 'PARA_LLEVAR', 'EVENTO') NOT NULL,
  estado ENUM('PENDIENTE', 'EN_PREPARACION', 'ENTREGADO', 'ANULADO') NOT NULL DEFAULT 'PENDIENTE',
  total DECIMAL(12,2) NOT NULL DEFAULT 0.00,
  observaciones TEXT NULL,
  CONSTRAINT fk_pedido_cliente FOREIGN KEY (id_cliente)
    REFERENCES clientes(id_cliente)
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT fk_pedido_usuario FOREIGN KEY (id_usuario)
    REFERENCES usuarios(id_usuario)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------
-- 11. Tabla: detalle_pedido
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS detalle_pedido (
  id_detalle INT AUTO_INCREMENT PRIMARY KEY,
  id_pedido INT NOT NULL,
  id_producto INT NOT NULL,
  cantidad INT NOT NULL,
  precio_unitario DECIMAL(10,2) NOT NULL,
  subtotal DECIMAL(12,2) NOT NULL,
  CONSTRAINT chk_detpedido_cantidad CHECK (cantidad > 0),
  CONSTRAINT chk_detpedido_precio CHECK (precio_unitario >= 0),
  CONSTRAINT chk_detpedido_subtotal CHECK (subtotal >= 0),
  CONSTRAINT fk_detpedido_pedido FOREIGN KEY (id_pedido)
    REFERENCES pedidos(id_pedido)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_detpedido_producto FOREIGN KEY (id_producto)
    REFERENCES productos(id_producto)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Índices adicionales para optimización de consultas frecuentes
CREATE INDEX idx_productos_categoria ON productos(id_categoria);
CREATE INDEX idx_recetas_producto ON recetas(id_producto);
CREATE INDEX idx_recetas_insumo ON recetas(id_insumo);
CREATE INDEX idx_compras_fecha ON compras(fecha_compra);
CREATE INDEX idx_compras_proveedor ON compras(id_proveedor);
CREATE INDEX idx_pedidos_fecha ON pedidos(fecha_pedido);
CREATE INDEX idx_pedidos_estado ON pedidos(estado);
CREATE INDEX idx_pedidos_cliente ON pedidos(id_cliente);
CREATE INDEX idx_detpedido_producto ON detalle_pedido(id_producto);
