# API REST Gastronomía - SENA CGDSS (EA4)

Prototipo de API REST desarrollada con **FastAPI** y **MongoDB** para la Unidad Productiva de Gastronomía del Centro de Gestión y Desarrollo Sostenible Surcolombiano (CGDSS).

Ficha: **3312744** | Aprendiz Letra: **[A]**
Estructura de arquitectura adaptada del modelo del instructor (**ORM**): `controllers/`, `routers/`, `schemas/`, `models/`, `database/`.

---

## 1. Requisitos Previos

- **Python 3.11+**
- **MongoDB 7.0 / 8.0 / 9.0** instalado y corriendo como servicio en Windows (o local en puerto `27017` por defecto).
- **Git**

---

## 2. Configuración y Ejecución Paso a Paso

### Paso 1: Configurar variables de entorno
Copiar la plantilla `.env.example` a un archivo `.env` y configurar las credenciales:
```bash
cp .env.example .env
```

El archivo `.env` incluye la configuración de conexión nativa a MongoDB:
```env
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_DATABASE=bd_gastronomia
JWT_SECRET=supersecretgastronomiakey2026jwtsecrettokenadso3312744
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
TZ=America/Bogota
```

### Paso 2: Activar Entorno Virtual e Instalar Dependencias
Desde la carpeta raíz del proyecto `api_gastronomia`:
```bash
# En Windows (Git Bash o CMD)
source venv/Scripts/activate  # o .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Paso 3: Inicializar Datos de Prueba (Seeder)
Al iniciar la aplicación, MongoDB carga automáticamente los datos de prueba iniciales (mínimo 10 registros por cada colección y contraseñas con hash bcrypt real). Si deseas forzar la reinicialización manual:
```bash
python -c "from app.database.a_connection import a_mongo_db; from app.database.a_seeder import a_inicializar_base_datos; a_inicializar_base_datos(a_mongo_db)"
```

### Paso 4: Iniciar el Servidor API
```bash
uvicorn app.a_main:app --reload
```
La API estará disponible en: `http://127.0.0.1:8000`

---

## 3. Verificación Automatizada (100% de Cumplimiento)
Puedes ejecutar la suite completa de pruebas automatizadas con el comando:
```bash
python a_verificar_api.py
```
Este script prueba los 25 escenarios exigidos por la guía y el instructor:
- Login y roles (ADMIN, CAJERO, COCINERO)
- Respuestas 401 Unauthorized sin token y 403 Forbidden por permisos
- Reglas de negocio RN01, RN02, RN03, RN04, RN05 y RN06
- Consultas de costo de producción, margen, insumos por vencer, reportes y calificaciones en MongoDB.

---

## 4. Documentación y Pruebas Manuales

- **Swagger UI (OpenAPI interactivo):** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`
- **Colección de Postman:** Importar el archivo `postman_collection.json` incluido en el repositorio.

### Usuarios de Prueba Iniciales
| Rol | Correo | Contraseña |
| :--- | :--- | :--- |
| **ADMIN** | `admin@gastronomia.sena.edu.co` | `Admin123*` |
| **CAJERO** | `cajero@gastronomia.sena.edu.co` | `Cajero123*` |
| **COCINERO** | `cocinero@gastronomia.sena.edu.co` | `Cocinero123*` |

---

## 5. Reglas de Negocio Implementadas

- **RN01:** Cálculo de subtotal (`cantidad * precio_unitario`) y total por la API; el precio se toma del producto y se ignora el enviado por el cliente.
- **RN02:** Al registrar compra se incrementa `stock_actual` y se actualiza `costo_unitario` de cada insumo.
- **RN03:** Al pasar pedido a `ENTREGADO` se descuentan insumos según receta; si no alcanza el stock, responde `409 Conflict`.
- **RN04:** Borrado lógico (`INACTIVO`) en productos, insumos, clientes y proveedores con movimientos; borrado físico si no tienen movimientos.
- **RN05:** Un pedido `ENTREGADO` o `ANULADO` no puede modificarse (`409 Conflict`).
- **RN06:** Contraseñas protegidas con `bcrypt` y nunca devueltas en respuestas JSON.
