# API REST Gastronomía - SENA CGDSS (EA4)

Prototipo de API REST desarrollada con **FastAPI**, **MySQL 8.0** y **MongoDB 7.0** para la Unidad Productiva de Gastronomía del Centro de Gestión y Desarrollo Sostenible Surcolombiano (CGDSS).

Ficha: **3312744** | Aprendiz Letra: **[A]**

---

## 1. Requisitos Previos

- **Python 3.11+**
- **Docker Desktop** (con soporte para Linux containers)
- **Git**

---

## 2. Configuración y Ejecución Paso a Paso

### Paso 1: Configurar variables de entorno
Copiar la plantilla `.env.example` a un archivo `.env` y configurar las credenciales:
```bash
cp .env.example .env
```

### Paso 2: Levantar Contenedores Docker (MySQL y MongoDB)
```bash
docker compose up -d
```
Verificar que los contenedores `mysql_gastronomia` y `mongo_gastronomia` estén en estado `Up`:
```bash
docker ps
```

### Paso 3: Ejecutar los Scripts de Base de Datos
Desde la raíz del proyecto `api_gastronomia/`:
```bash
# 1. DDL (Tablas, llaves, restricciones y comprobaciones)
docker exec -i mysql_gastronomia mysql -u root -pRootSecret2026* < database/01_ddl_bd_gastronomia.sql

# 2. DML (Datos de prueba con contraseñas bcrypt reales)
docker exec -i mysql_gastronomia mysql -u root -pRootSecret2026* < database/02_dml_datos_prueba.sql

# 3. DCL (Usuario con privilegios mínimos SELECT, INSERT, UPDATE, DELETE)
docker exec -i mysql_gastronomia mysql -u root -pRootSecret2026* < database/03_dcl_usuarios.sql

# 4. MongoDB (Colección calificaciones con validador $jsonSchema)
docker exec -i mongo_gastronomia mongosh < database/04_mongo_calificaciones.js
```

### Paso 4: Activar Entorno Virtual e Instalar Dependencias
```bash
# En Windows (Git Bash o CMD)
source venv/Scripts/activate  # o .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Paso 5: Iniciar el Servidor API
```bash
uvicorn app.a_main:app --reload
```
La API estará disponible en: `http://127.0.0.1:8000`

---

## 3. Documentación y Pruebas

- **Swagger UI (OpenAPI):** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`
- **Colección de Postman:** Importar el archivo `postman_collection.json` incluido en el repositorio.

### Usuarios de Prueba Iniciales
| Rol | Correo | Contraseña |
| :--- | :--- | :--- |
| **ADMIN** | `admin@gastronomia.sena.edu.co` | `Admin123*` |
| **CAJERO** | `cajero@gastronomia.sena.edu.co` | `Cajero123*` |
| **COCINERO** | `cocinero@gastronomia.sena.edu.co` | `Cocinero123*` |

---

## 4. Reglas de Negocio Implementadas

- **RN01:** Cálculo de subtotal y total por la API; el precio se toma del producto y se ignora el enviado por el cliente.
- **RN02:** Al registrar compra se incrementa `stock_actual` y se actualiza `costo_unitario` de cada insumo.
- **RN03:** Al pasar pedido a `ENTREGADO` se descuentan insumos según receta; si no alcanza el stock, responde `409 Conflict`.
- **RN04:** Borrado lógico (`INACTIVO`) en productos, insumos, clientes y proveedores con movimientos; borrado físico si no tienen movimientos.
- **RN05:** Un pedido `ENTREGADO` o `ANULADO` no puede modificarse (`409 Conflict`).
- **RN06:** Contraseñas protegidas con `bcrypt` y nunca devueltas en respuestas JSON.
