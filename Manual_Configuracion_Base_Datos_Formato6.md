# FORMATO 6: MANUAL DE CONFIGURACIÓN DE BASE DE DATOS
## PROYECTO FORMATIVO: SISTEMA DE GESTIÓN API REST GASTRONOMÍA
### CENTRO DE GESTIÓN Y DESARROLLO SOSTENIBLE SURCOLOMBIANO (CGDSS) - SENA
**Programa:** Análisis y Desarrollo de Software (ADSO)  
**Ficha:** 3312744  
**Actividad:** EA4 — Construir el prototipo de una API REST con Python  
**Aprendiz:** [A] (Letra de identificación: A)  
**Fecha de Elaboración:** Octubre de 2026  

---

## 1. HISTORIAL DE REVISIÓN Y CAMBIOS

| Versión | Fecha | Descripción del Cambio | Elaboró | Revisó | Aprobó |
| :---: | :---: | :--- | :--- | :--- | :--- |
| **1.0.0** | 18/10/2026 | Creación inicial del manual, diccionario de datos completo (11 tablas MySQL + colección MongoDB), modelo relacional, justificación técnica y guías de despliegue. | Aprendiz [A] (Desarrollador) | Instructor de Seguimiento Técnico (ADSO) | Líder de la Unidad Productiva de Gastronomía |

---

## 2. INTRODUCCIÓN

El presente Manual de Configuración de Base de Datos tiene como propósito establecer las pautas técnicas, estructurales, operativas y de seguridad bajo las cuales opera el repositorio de persistencia de datos para la **Unidad Productiva de Gastronomía del Centro de Gestión y Desarrollo Sostenible Surcolombiano (CGDSS) - SENA**.

La Unidad Productiva elabora y comercializa platos típicos, bebidas, productos de panadería y repostería para la comunidad educativa (aprendices, instructores, administrativos y visitantes externos), además de atender eventos institucionales. La arquitectura de persistencia implementada adopta un enfoque **híbrido (Políglota)**:
1. **Base de Datos Relacional (MySQL 8.0 - `bd_gastronomia`):** Almacena de forma transaccional, consistente y referencial la información de usuarios, roles, catálogo de productos, fichas técnicas (recetas), existencias de inventario (insumos), proveedores, compras a proveedores, clientes y comandas de pedidos con sus detalles y liquidación de costos.
2. **Base de Datos No Relacional (MongoDB 7.0 - `bd_gastronomia_nosql`):** Diseñada para almacenar colecciones semiestructuradas y dinámicas de retroalimentación cualitativa y cuantitativa de clientes (colección `calificaciones`), garantizando alta velocidad de escritura, agregaciones analíticas para el cálculo de satisfacción promedio y desacoplamiento frente a esquemas relacionales rígidos.

Esta base de datos sirve como el núcleo transaccional consumido exclusivamente por la **API REST en FastAPI**, asegurando que ninguna aplicación externa (web o móvil) interactúe con los motores sin pasar por la capa de lógica y validación de seguridad (JWT, roles y reglas de negocio RN01 a RN06).

---

## 3. ALCANCE

El alcance de la solución de base de datos para este prototipo abarca los siguientes módulos y procesos:
- **Gestión de Seguridad y Control de Acceso:** Registro de usuarios autorizados, clasificación por roles (`ADMIN`, `CAJERO`, `COCINERO`), almacenamiento de contraseñas bajo hash unidireccional `bcrypt` y estados de cuenta.
- **Estandarización de Fichas Técnicas (Recetas):** Descomposición de productos en materias primas (insumos) y formulación de cantidades precisas por porción/unidad para costeo exacto.
- **Control de Inventarios y Alertas:** Control de existencias (`stock_actual`), niveles de alerta (`stock_minimo`), costos unitarios y monitoreo de fechas de caducidad de lotes.
- **Gestión de Compras y Abastecimiento:** Registro de proveedores, órdenes y facturas de compra con detalle de insumos, con cálculo y actualización automática de existencias y costos unitarios.
- **Gestión de Clientes y Pedidos:** Clasificación de clientes (`APRENDIZ`, `INSTRUCTOR`, `FUNCIONARIO`, `EXTERNO`), toma de pedidos según tipo (`MESA`, `PARA_LLEVAR`, `EVENTO`), control de ciclo de vida (`PENDIENTE` → `EN_PREPARACION` → `ENTREGADO` / `ANULADO`) y liquidación matemática de subtotales.
- **Métricas de Satisfacción (NoSQL):** Captura de opiniones, calificación del servicio (1 a 5 estrellas) y puntuación desagregada por cada plato/bebida consumida.

### Fuera del Alcance (Prototipo Fase 1):
- Facturación electrónica directa con la DIAN (se registran números de factura internos/proveedor).
- Integración con pasarelas de pago bancarias (PSE, datáfonos en línea).
- Módulo de nómina de cocineros y personal operativo.

---

## 4. RESPONSABLES E INVOLUCRADOS

| Nombre / Rol | Rol en el Proyecto | Responsabilidad Técnica |
| :--- | :--- | :--- |
| **Aprendiz [A]** | Responsable Técnico / Desarrollador Backend | Diseño del MER, elaboración de scripts DDL/DML/DCL/NoSQL, configuración de Docker Compose, desarrollo de la API REST y documentación técnica. |
| **Instructor Técnico SENA** | Revisor / Evaluador | Revisión de arquitectura, validación de normalización relacional, auditoría de seguridad (JWT, bcrypt, DCL) y aprobación del entregable. |
| **Líder Unidad Gastronómica** | Involucrado / Stakeholder Funcional | Suministro de requerimientos, validación de fichas técnicas de platos, prueba funcional de comandas y aceptación del prototipo. |

---

## 5. MODELO ENTIDAD RELACIÓN (MER)

El modelo conceptual entidad–relación modela las entidades participantes, sus atributos y sus cardinalidades:
- Una **Categoría** contiene **1:N** **Productos**.
- Un **Producto** se compone de **N:M** **Insumos**, relación resuelta a través de la entidad asociativa débil **Recetas (Ficha Técnica)** que almacena el atributo derivado `cantidad`.
- Un **Proveedor** suministra **1:N** **Compras**.
- Una **Compra** contiene **N:M** **Insumos**, resuelta mediante la entidad asociativa **Detalle_Compra** (`cantidad`, `costo_unitario`, `subtotal`).
- Un **Cliente** emite **1:N** **Pedidos**.
- Un **Usuario** (Cajero/Admin) atiende y registra **1:N** **Pedidos**.
- Un **Pedido** agrupa **N:M** **Productos**, resuelta mediante la entidad asociativa **Detalle_Pedido** (`cantidad`, `precio_unitario`, `subtotal`).

```
+-------------------------------------------------------------------------------------------------------+
|                       [MARCADOR OBLIGATORIO DE DIAGRAMA: MODELO ENTIDAD-RELACIÓN]                     |
|                                                                                                       |
| Pegue aquí el Diagrama Conceptual MER elaborado en MySQL Workbench o draw.io que ilustra las          |
| entidades (usuarios, categorias, productos, insumos, recetas, proveedores, compras, detalle_compra,  |
| clientes, pedidos, detalle_pedido), sus atributos principales, claves primarias y cardinalidades.     |
+-------------------------------------------------------------------------------------------------------+
```

---

## 6. DICCIONARIO DE DATOS

A continuación se detalla la especificación de campos, tipos, nulidad, claves, restricciones y valores por defecto para cada una de las 11 tablas relacionales en MySQL y la colección NoSQL en MongoDB.

### 6.1. Tabla: `usuarios`
Almacena las credenciales de acceso, datos personales y perfiles de rol del personal administrativo y operativo.

| Campo | Tipo | Tamaño | Nulo | Llave | Defecto / Restricción | Descripción |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| `id_usuario` | INT | 11 | No | PK | `AUTO_INCREMENT` | Identificador único secuencial del usuario |
| `identificacion` | VARCHAR | 20 | No | UQ | Restricción `UNIQUE` | Documento de identidad (cédula o tarjeta) |
| `nombres` | VARCHAR | 80 | No | - | - | Nombres del funcionario o aprendiz |
| `apellidos` | VARCHAR | 80 | No | - | - | Apellidos del funcionario o aprendiz |
| `correo` | VARCHAR | 120 | No | UQ | Restricción `UNIQUE` | Correo electrónico de acceso al sistema |
| `password` | VARCHAR | 255 | No | - | Hash bcrypt real | Contraseña cifrada unidireccional (RN06) |
| `rol` | ENUM | - | No | - | `'ADMIN','CAJERO','COCINERO'` | Perfil de autorización para endpoints |
| `estado` | ENUM | - | No | - | `'ACTIVO'` (`'ACTIVO','INACTIVO'`) | Estado de la cuenta en el sistema |

---

### 6.2. Tabla: `categorias`
Clasificación comercial y funcional de los productos gastronómicos ofertados.

| Campo | Tipo | Tamaño | Nulo | Llave | Defecto / Restricción | Descripción |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| `id_categoria` | INT | 11 | No | PK | `AUTO_INCREMENT` | Identificador único de la categoría |
| `nombre` | VARCHAR | 60 | No | UQ | Restricción `UNIQUE` | Nombre representativo (ej. Platos Fuertes) |
| `descripcion` | VARCHAR | 200 | Sí | - | `NULL` | Detalle del tipo de alimentos incluidos |
| `estado` | ENUM | - | No | - | `'ACTIVO'` (`'ACTIVO','INACTIVO'`) | Estado operativo de la categoría |

---

### 6.3. Tabla: `productos`
Almacena el catálogo de preparaciones finales disponibles para la venta.

| Campo | Tipo | Tamaño | Nulo | Llave | Defecto / Restricción | Descripción |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| `id_producto` | INT | 11 | No | PK | `AUTO_INCREMENT` | Identificador único del producto |
| `codigo` | VARCHAR | 20 | No | UQ | Restricción `UNIQUE` | Código alfanumérico interno (ej. PRD-001) |
| `nombre` | VARCHAR | 100 | No | - | - | Nombre comercial del plato o bebida |
| `descripcion` | TEXT | - | Sí | - | `NULL` | Ingredientes e información del plato |
| `precio_venta` | DECIMAL | 10,2 | No | - | `CHECK (precio_venta > 0)` | Precio de venta al público en COP |
| `unidad_venta` | VARCHAR | 20 | No | - | - | Porción, vaso 12oz, unidad, etc. |
| `id_categoria` | INT | 11 | No | FK | `categorias(id_categoria)` | Referencia a la categoría correspondiente |
| `estado` | ENUM | - | No | - | `'DISPONIBLE'` (`'DISPONIBLE','AGOTADO','INACTIVO'`) | Estado para venta y borrado lógico |

---

### 6.4. Tabla: `insumos`
Control de materias primas e ingredientes disponibles en bodega/cocina.

| Campo | Tipo | Tamaño | Nulo | Llave | Defecto / Restricción | Descripción |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| `id_insumo` | INT | 11 | No | PK | `AUTO_INCREMENT` | Identificador único del insumo |
| `nombre` | VARCHAR | 100 | No | UQ | Restricción `UNIQUE` | Nombre del ingrediente o materia prima |
| `unidad_medida`| ENUM | - | No | - | `'g','kg','ml','l','lb','unidad'` | Unidad física estandarizada |
| `stock_actual` | DECIMAL | 10,2 | No | - | `DEFAULT 0.00, CHECK (>= 0)` | Existencias disponibles en bodega |
| `stock_minimo` | DECIMAL | 10,2 | No | - | `DEFAULT 0.00, CHECK (>= 0)` | Umbral de alerta para reposición |
| `costo_unitario`| DECIMAL | 10,2 | No | - | `DEFAULT 0.00, CHECK (>= 0)` | Costo por unidad según última compra |
| `fecha_vencimiento`| DATE | - | Sí | - | `NULL` | Fecha de caducidad del lote actual |
| `estado` | ENUM | - | No | - | `'ACTIVO'` (`'ACTIVO','INACTIVO'`) | Estado operativo del insumo |

---

### 6.5. Tabla: `recetas`
Fichas técnicas que definen la cantidad exacta de materias primas requeridas por producto.

| Campo | Tipo | Tamaño | Nulo | Llave | Defecto / Restricción | Descripción |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| `id_receta` | INT | 11 | No | PK | `AUTO_INCREMENT` | Identificador único de la línea de receta |
| `id_producto` | INT | 11 | No | FK | `productos(id_producto)` | Referencia al plato o bebida elaborado |
| `id_insumo` | INT | 11 | No | FK | `insumos(id_insumo)` | Referencia a la materia prima utilizada |
| `cantidad` | DECIMAL | 10,3 | No | - | `CHECK (cantidad > 0)` | Cantidad requerida en la unidad del insumo |

---

### 6.6. Tabla: `proveedores`
Empresas o personas naturales que abastecen a la unidad productiva.

| Campo | Tipo | Tamaño | Nulo | Llave | Defecto / Restricción | Descripción |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| `id_proveedor` | INT | 11 | No | PK | `AUTO_INCREMENT` | Identificador único del proveedor |
| `nit` | VARCHAR | 20 | No | UQ | Restricción `UNIQUE` | NIT o documento fiscal con dígito verificación |
| `razon_social` | VARCHAR | 120 | No | - | - | Nombre o razón social de la empresa |
| `telefono` | VARCHAR | 20 | Sí | - | `NULL` | Teléfono de contacto comercial |
| `correo` | VARCHAR | 120 | Sí | - | `NULL` | Correo electrónico para órdenes |
| `direccion` | VARCHAR | 150 | Sí | - | `NULL` | Ubicación física o sede comercial |
| `estado` | ENUM | - | No | - | `'ACTIVO'` (`'ACTIVO','INACTIVO'`) | Estado operativo para compras |

---

### 6.7. Tabla: `compras`
Cabecera de facturas y órdenes de adquisición de insumos a proveedores.

| Campo | Tipo | Tamaño | Nulo | Llave | Defecto / Restricción | Descripción |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| `id_compra` | INT | 11 | No | PK | `AUTO_INCREMENT` | Identificador único de la compra |
| `numero_factura`| VARCHAR | 30 | No | - | - | Número de factura física del proveedor |
| `fecha_compra` | DATETIME | - | No | - | `DEFAULT CURRENT_TIMESTAMP` | Fecha y hora en que se causó la compra |
| `id_proveedor` | INT | 11 | No | FK | `proveedores(id_proveedor)` | Proveedor que emitió la factura |
| `id_usuario` | INT | 11 | No | FK | `usuarios(id_usuario)` | Usuario del sistema que registró la compra |
| `total` | DECIMAL | 12,2 | No | - | `DEFAULT 0.00` | Monto total liquidado de la compra |

---

### 6.8. Tabla: `detalle_compra`
Líneas de detalle de insumos adquiridos en una factura de compra.

| Campo | Tipo | Tamaño | Nulo | Llave | Defecto / Restricción | Descripción |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| `id_detalle_compra`| INT | 11 | No | PK | `AUTO_INCREMENT` | Identificador único del ítem comprado |
| `id_compra` | INT | 11 | No | FK | `compras(id_compra)` ON DELETE CASCADE | Factura de compra a la que pertenece |
| `id_insumo` | INT | 11 | No | FK | `insumos(id_insumo)` | Insumo recibido en inventario |
| `cantidad` | DECIMAL | 10,2 | No | - | `CHECK (cantidad > 0)` | Cantidad física ingresada al almacén |
| `costo_unitario`| DECIMAL | 10,2 | No | - | `CHECK (costo_unitario >= 0)` | Precio acordado por unidad de medida |
| `subtotal` | DECIMAL | 12,2 | No | - | `CHECK (subtotal >= 0)` | `cantidad * costo_unitario` |

---

### 6.9. Tabla: `clientes`
Registro de consumidores de la cafetería y restaurante pedagógico.

| Campo | Tipo | Tamaño | Nulo | Llave | Defecto / Restricción | Descripción |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| `id_cliente` | INT | 11 | No | PK | `AUTO_INCREMENT` | Identificador único del cliente |
| `identificacion` | VARCHAR | 20 | No | UQ | Restricción `UNIQUE` | Documento de identidad |
| `nombres` | VARCHAR | 80 | No | - | - | Nombres del cliente |
| `apellidos` | VARCHAR | 80 | No | - | - | Apellidos del cliente |
| `telefono` | VARCHAR | 20 | Sí | - | `NULL` | Teléfono de contacto |
| `correo` | VARCHAR | 120 | Sí | - | `NULL` | Correo electrónico |
| `tipo_cliente` | ENUM | - | No | - | `'APRENDIZ','INSTRUCTOR','FUNCIONARIO','EXTERNO'` | Vinculación institucional con el SENA |
| `estado` | ENUM | - | No | - | `'ACTIVO'` (`'ACTIVO','INACTIVO'`) | Estado para borrado lógico (RN04) |

---

### 6.10. Tabla: `pedidos`
Cabecera de órdenes de consumo o comandas de servicio.

| Campo | Tipo | Tamaño | Nulo | Llave | Defecto / Restricción | Descripción |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| `id_pedido` | INT | 11 | No | PK | `AUTO_INCREMENT` | Identificador numérico de la comanda |
| `fecha_pedido` | DATETIME | - | No | - | `DEFAULT CURRENT_TIMESTAMP` | Fecha y hora de apertura del pedido |
| `id_cliente` | INT | 11 | No | FK | `clientes(id_cliente)` | Cliente titular de la comanda |
| `id_usuario` | INT | 11 | No | FK | `usuarios(id_usuario)` | Cajero o mesero que tomó la orden |
| `tipo_pedido` | ENUM | - | No | - | `'MESA','PARA_LLEVAR','EVENTO'` | Modalidad de despacho del pedido |
| `estado` | ENUM | - | No | - | `'PENDIENTE'` (`'PENDIENTE','EN_PREPARACION','ENTREGADO','ANULADO'`) | Estado en cocina y servicio |
| `total` | DECIMAL | 12,2 | No | - | `DEFAULT 0.00` | Total liquidado por la API (RN01) |
| `observaciones`| TEXT | - | Sí | - | `NULL` | Indicaciones especiales (sin sal, etc.) |

---

### 6.11. Tabla: `detalle_pedido`
Líneas de productos solicitados en una comanda.

| Campo | Tipo | Tamaño | Nulo | Llave | Defecto / Restricción | Descripción |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- |
| `id_detalle` | INT | 11 | No | PK | `AUTO_INCREMENT` | Identificador único del renglón de pedido |
| `id_pedido` | INT | 11 | No | FK | `pedidos(id_pedido)` ON DELETE CASCADE | Pedido al que pertenece el ítem |
| `id_producto` | INT | 11 | No | FK | `productos(id_producto)` | Plato o bebida solicitada |
| `cantidad` | INT | 11 | No | - | `CHECK (cantidad > 0)` | Número de porciones solicitadas |
| `precio_unitario`| DECIMAL | 10,2 | No | - | `CHECK (precio_unitario >= 0)` | Precio vigente tomado del producto (RN01) |
| `subtotal` | DECIMAL | 12,2 | No | - | `CHECK (subtotal >= 0)` | `cantidad * precio_unitario` (RN01) |

---

### 6.12. Colección NoSQL MongoDB: `calificaciones`
Colección orientada a documentos en la base `bd_gastronomia_nosql`.

- **Mecanismo de Integridad:** Validador formal `$jsonSchema` a nivel de motor.
- **Índices:**
  - `{ "id_pedido": 1 }` (Único): Garantiza que una orden no se califique por duplicado.
  - `{ "id_cliente": 1 }`: Optimiza consultas de satisfacción por cliente.
  - `{ "productos.id_producto": 1 }`: Acelera agregaciones y promedios por producto (RF12).

| Propiedad BSON | Tipo BSON | Requerido | Restricción | Descripción |
| :--- | :--- | :---: | :--- | :--- |
| `_id` | ObjectId | Sí | Generado automáticamente | Llave primaria nativa de MongoDB |
| `id_pedido` | Int (NumberInt) | Sí | Referencia a `pedidos.id_pedido` | Identificador de la comanda evaluada |
| `id_cliente` | Int (NumberInt) | Sí | Referencia a `clientes.id_cliente` | Identificador del cliente evaluador |
| `fecha` | String | Sí | Formato ISO-8601 UTC | Marca temporal de la calificación |
| `calificacion_servicio` | Int | Sí | `minimum: 1, maximum: 5` | Evaluación general de atención y servicio |
| `comentario` | String | Sí | Texto descriptivo | Opinión cualitativa del cliente |
| `productos` | Array de Objetos | Sí | Mínimo 1 elemento | Lista de platos evaluados |
| `productos[].id_producto`| Int | Sí | Referencia a `productos.id_producto` | Identificador del plato evaluado |
| `productos[].nombre` | String | Sí | Nombre descriptivo | Nombre comercial del plato |
| `productos[].calificacion`| Int | Sí | `minimum: 1, maximum: 5` | Puntuación específica del plato |

---

## 7. MODELO RELACIONAL (DISEÑO FÍSICO WORKBENCH)

El modelo relacional físico fue generado mediante ingeniería inversa conectando MySQL Workbench al puerto 3306 de MySQL 8.0.

```
+-------------------------------------------------------------------------------------------------------+
|                    [MARCADOR OBLIGATORIO DE CAPTURA: MODELO RELACIONAL FÍSICO]                        |
|                                                                                                       |
| Pegue aquí el diagrama EER físico generado desde MySQL Workbench:                                     |
| Database -> Reverse Engineer -> Host: localhost, Port: 3306, User: usr_gastronomia -> bd_gastronomia  |
| El diagrama debe evidenciar todas las 11 tablas, tipos de datos, llaves primarias (amarillas) y        |
| líneas de relación con patas de gallo (1:N y N:M resueltas).                                          |
+-------------------------------------------------------------------------------------------------------+
```

---

## 8. JUSTIFICACIÓN DEL MOTOR SELECCIONADO

### 8.1. Comparativa de Motores Relacionales frente a MySQL 8.0

| Criterio de Selección | MySQL 8.0 (Seleccionado) | PostgreSQL | Microsoft SQL Server | Oracle Database |
| :--- | :--- | :--- | :--- | :--- |
| **Licenciamiento y Costos** | Código abierto (GPL v2), gratuito para producción y aprendizaje SENA. | Código abierto (PostgreSQL License), gratuito. | Comercial con licencias de alto costo por núcleo (Express limitado a 10 GB). | Altamente costoso, licenciamiento corporativo por CPU. |
| **Consumo de Recursos** | Muy ligero (~200 MB RAM en contenedor Docker). Ideal para computadores formativos. | Moderado (~350 MB RAM base). | Pesado (> 1.5 GB RAM). No apto para entornos con recursos limitados. | Muy pesado (> 2 GB RAM mínimos). Complejo de contenerizar. |
| **Ecosistema con Python** | Soporte nativo y masivo con SQLAlchemy y PyMySQL puro (sin compiladores C). | Excelente con psycopg2/asyncpg, pero requiere librerías binarias nativas en Windows. | Requiere controladores ODBC específicos (`pyodbc`, `msodbcsql17`). | Requiere `oracledb` y librerías cliente Oracle Instant Client. |
| **Facilidad Operativa** | Despliegue inmediato en Docker, herramientas gratuitas (Workbench, DBeaver). | Muy potente en tipos avanzados, pero mayor complejidad de configuración inicial. | Alta dependencia del ecosistema Microsoft Windows. | Curva de aprendizaje empinada, excesivo para una unidad productiva. |

### 8.2. Justificación del Uso de MongoDB 7.0 para Calificaciones

Para el módulo de calificaciones y opiniones (RF12), se seleccionó **MongoDB 7.0** por las siguientes razones:
1. **Esquema Flexible y Anidado:** Cada pedido evaluado contiene una cantidad variable de productos calificados. En MongoDB, esto se modela naturalmente como un documento que contiene una sub-lista (`productos: [{ id_producto, nombre, calificacion }]`) sin requerir sentencias complejas `JOIN` o tablas relacionales adicionales.
2. **Alta Velocidad de Escritura sin Bloqueos:** La retroalimentación de clientes en horas pico de almuerzo genera alta concurrencia de inserciones. MongoDB procesa documentos independientes sin generar contención ni bloqueos de filas en las tablas transaccionales de inventario y pedidos de MySQL.
3. **Agregaciones Potentes:** El Pipeline de Agregación de MongoDB permite calcular promedios de satisfacción ponderados por producto en milisegundos (`$unwind`, `$match`, `$group`, `$avg`).

---

## 9. REQUISITOS DE CONFIGURACIÓN

### 9.1. Plataforma y Herramientas
- **Sistema Operativo:** Windows 10/11 x64, Linux o macOS.
- **Docker Engine:** Versión 24.0+ con Docker Desktop y WSL 2 backend.
- **Python:** Versión 3.11 a 3.13 de 64 bits.
- **Git:** Versión 2.40+ para control de versiones.

### 9.2. Imágenes de Contenedores
- `mysql:8.0` (Configurada con `--character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci --default-time-zone='-05:00'`).
- `mongo:7.0` (Con volumen persistente de base de datos).

### 9.3. Librerías Python de Conectividad
- `sqlalchemy`: ORM relacional v2.1+.
- `pymysql`: Conector puro de Python para MySQL.
- `cryptography`: Cifrado y negociación segura de conexiones MySQL.
- `pymongo`: Controlador oficial para MongoDB 7.0.
- `pydantic` & `email-validator`: Validación estricta de datos de entrada y salida.
- `passlib[bcrypt]` & `bcrypt==4.0.1`: Algoritmo seguro de hashing de contraseñas.
- `PyJWT`: Generación y verificación de tokens de acceso Bearer.
- `python-dotenv`: Carga de configuración desde archivos locales protegidos.

---

## 10. SCRIPTS DE BASE DE DATOS

Todos los scripts se ubican en la carpeta `database/` del repositorio:
- `01_ddl_bd_gastronomia.sql`: Creación de la base de datos `bd_gastronomia`, 11 tablas relacionales, llaves primarias, foráneas, índices de optimización y restricciones `CHECK`.
- `02_dml_datos_prueba.sql`: Carga de datos iniciales con mínimo 10 registros reales de contexto gastronómico colombiano por tabla, incluyendo usuarios con hashes bcrypt auténticos.
- `03_dcl_usuarios.sql`: Creación del usuario de aplicación `usr_gastronomia` y asignación de privilegios mínimos DML (`SELECT`, `INSERT`, `UPDATE`, `DELETE`).
- `04_mongo_calificaciones.js`: Creación de la colección `calificaciones` en `bd_gastronomia_nosql`, validador `$jsonSchema`, índices y documentos iniciales.

---

## 11. CONFIGURACIÓN Y EJECUCIÓN PASO A PASO

### Paso 1: Levantar los contenedores de Docker
En una terminal ubicada en la carpeta `api_gastronomia/`:
```bash
docker compose up -d
```
Verificar que los contenedores estén en estado activo:
```bash
docker ps
```

```
+-------------------------------------------------------------------------------------------------------+
|                    [MARCADOR OBLIGATORIO DE CAPTURA: DOCKER PS CON FECHA Y HORA]                      |
|                                                                                                       |
| Pegue aquí la captura de pantalla de su terminal ejecutando `docker ps` y mostrando la fecha/hora.    |
| Debe observarse `mysql_gastronomia` en puerto 3306 y `mongo_gastronomia` en puerto 27017 en estado Up |
+-------------------------------------------------------------------------------------------------------+
```

### Paso 2: Ejecutar los scripts de MySQL
```bash
# Ejecutar DDL
docker exec -i mysql_gastronomia mysql -u root -pRootSecret2026* < database/01_ddl_bd_gastronomia.sql

# Ejecutar DML
docker exec -i mysql_gastronomia mysql -u root -pRootSecret2026* < database/02_dml_datos_prueba.sql

# Ejecutar DCL
docker exec -i mysql_gastronomia mysql -u root -pRootSecret2026* < database/03_dcl_usuarios.sql
```

Evidenciar las tablas creadas conectándose con el usuario de la API `usr_gastronomia`:
```bash
docker exec mysql_gastronomia mysql -u usr_gastronomia -pGastronomiaPass2026* bd_gastronomia -e "SHOW TABLES;"
```

```
+-------------------------------------------------------------------------------------------------------+
|                   [MARCADOR OBLIGATORIO DE CAPTURA: SHOW TABLES CON FECHA Y HORA]                     |
|                                                                                                       |
| Pegue aquí la captura de pantalla de la terminal mostrando las 11 tablas creadas en `bd_gastronomia`. |
| La captura debe evidenciar la fecha y hora de la consola del sistema.                                 |
+-------------------------------------------------------------------------------------------------------+
```

Evidenciar la estructura de las tablas `productos` y `pedidos`:
```bash
docker exec mysql_gastronomia mysql -u usr_gastronomia -pGastronomiaPass2026* bd_gastronomia -e "DESCRIBE productos; DESCRIBE pedidos;"
```

```
+-------------------------------------------------------------------------------------------------------+
|                   [MARCADOR OBLIGATORIO DE CAPTURA: DESCRIBE TABLAS CON FECHA Y HORA]                 |
|                                                                                                       |
| Pegue aquí la captura de pantalla mostrando la estructura de columnas, tipos, nulos, llaves y         |
| valores por defecto de las tablas principales, incluyendo el campo `observaciones` en `pedidos`.      |
+-------------------------------------------------------------------------------------------------------+
```

### Paso 3: Ejecutar el script de MongoDB
```bash
docker exec -i mongo_gastronomia mongosh < database/04_mongo_calificaciones.js
```
Verificar los documentos insertados:
```bash
docker exec mongo_gastronomia mongosh bd_gastronomia_nosql --eval "db.calificaciones.find().pretty()"
```

```
+-------------------------------------------------------------------------------------------------------+
|               [MARCADOR OBLIGATORIO DE CAPTURA: DOCUMENTOS MONGODB CON FECHA Y HORA]                  |
|                                                                                                       |
| Pegue aquí la captura de la consulta a la colección `calificaciones` en MongoDB mostrando documentos  |
| con su validación $jsonSchema, sub-documentos de productos y la fecha/hora de la consola.             |
+-------------------------------------------------------------------------------------------------------+
```

---

## 12. OTRAS CONSIDERACIONES TÉCNICAS Y OPERATIVAS

### 12.1. Codificación de Caracteres (`utf8mb4`)
Se configuró globalmente `utf8mb4` con colación `utf8mb4_unicode_ci` tanto a nivel de servidor MySQL como de base de datos y tablas. Esto garantiza:
- Soporte completo para caracteres del idioma español (tildes, letra ñ, diéresis).
- Almacenamiento seguro de caracteres especiales y emojis sin riesgo de truncamiento o corrupción de datos.

### 12.2. Zona Horaria (`America/Bogota`)
Se estableció la variable de entorno `TZ=America/Bogota` en los contenedores y el parámetro `--default-time-zone='-05:00'` en MySQL. Esto asegura que:
- Las marcas temporales automáticas (`CURRENT_TIMESTAMP`) en compras, pedidos y calificaciones coincidan exactamente con la hora legal de Colombia (UTC-5), evitando desfasajes de auditoría.

### 12.3. Respaldo y Restauración (Backup & Restore)
Para la operación continua de la unidad productiva, se definen los siguientes procedimientos de contingencia:

#### Respaldo MySQL:
```bash
# Generar volcado completo en archivo SQL comprimido
docker exec mysql_gastronomia mysqldump -u root -pRootSecret2026* --default-character-set=utf8mb4 --routines --triggers bd_gastronomia > backup_bd_gastronomia_$(date +%Y%m%d_%H%M%S).sql
```

#### Restauración MySQL:
```bash
# Restaurar sobre una base de datos limpia
docker exec -i mysql_gastronomia mysql -u root -pRootSecret2026* bd_gastronomia < backup_bd_gastronomia.sql
```

#### Respaldo MongoDB:
```bash
# Generar volcado BSON de la base de calificaciones
docker exec mongo_gastronomia mongodump --db bd_gastronomia_nosql --out /data/backup_mongo
```

#### Restauración MongoDB:
```bash
# Restaurar colección
docker exec mongo_gastronomia mongorestore --db bd_gastronomia_nosql /data/backup_mongo/bd_gastronomia_nosql
```

### 12.4. Manejo Seguro de Credenciales (Principio de Menor Privilegio)
1. **Conexión de la API:** La API REST **NUNCA** utiliza el superusuario `root`. Se conecta a través de `usr_gastronomia`, que solo tiene privilegios `SELECT`, `INSERT`, `UPDATE`, `DELETE` sobre las tablas de `bd_gastronomia`. No puede eliminar bases de datos (`DROP DATABASE`), modificar estructuras (`ALTER`), ni alterar permisos.
2. **Aislamiento en `.env`:** Las credenciales y claves criptográficas (`JWT_SECRET`, contraseñas de bases de datos) residen únicamente en el archivo local `.env`, el cual se encuentra estrictamente ignorado en `.gitignore` para evitar filtraciones en repositorios públicos de GitHub. En el repositorio solo se versiona `.env.example` sin secretos reales.

---
*Fin del Manual de Configuración de Base de Datos - Formato 6.*
