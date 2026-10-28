
```
app/
├── a_main.py              # crea la app, registra los routers (como ORM/main.py)
├── core/
│   ├── a_config.py        # variables del .env y fecha de Bogotá
│   └── a_security.py      # bcrypt (RN06), JWT y validación de roles (401/403)
├── database/
│   ├── a_connection.py    # MongoClient, A_Base, a_get_db() (como ORM/database/connection.py)
│   └── a_seeder.py        # datos iniciales si la base está vacía
├── models/                # una clase por colección (como ORM/models)
├── schemas/               # validaciones Pydantic Create/Update/Response (como ORM/schemas)
├── controllers/           # lógica y reglas de negocio (como ORM/controllers)
└── routers/               # endpoints /api/v1/... (como ORM/routers)
```

Flujo de una petición: **router** → valida rol y body con el **schema** → llama al **controller** → usa el **model** para llegar a la colección.

Entidades: `a_auth`, `a_usuario`, `a_categoria`, `a_producto`, `a_insumo`, `a_receta`, `a_proveedor`, `a_compra`, `a_cliente`, `a_pedido`, `a_reporte`, `a_calificacion`.

## 2. Requisitos

- Python 3.11+
- MongoDB corriendo como servicio local en `localhost:27017` (sin Docker). Base: `bd_gastronomia_nosql`.

## 3. Puesta en marcha

Desde la carpeta `api_gastronomia`, activando **siempre primero** el entorno virtual (si no, sale `No module named 'pymongo'`):

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.a_main:app --port 3000 --reload --reload-dir app
```

El archivo de arranque es `app/a_main.py`, por eso el comando es `app.a_main:app` (y no `main:app`). El puerto puede ser otro, por ejemplo `--port 8000`.

También se puede arrancar con el botón ▶ de VS Code sobre `app/a_main.py`. Para detenerla: `Ctrl+C` en esa terminal.

Si es la primera vez, copie `.env.example` a `.env` y cambie `JWT_SECRET`.

Si no arranca, el mensaje de error dice la causa:

| Mensaje | Solución |
|---|---|
| MongoDB no responde en localhost:27017 | PowerShell como administrador: `Start-Service MongoDB` |
| El disco está lleno | Liberar al menos 500 MB en el disco C: |
| MongoDB rechazó el usuario o la contraseña | Revisar `MONGO_USER` y `MONGO_PASSWORD` en `.env` |
| Falta la variable JWT_SECRET | Copiar `.env.example` a `.env` |
| `[Errno 10048]` / address already in use | Ya hay otra API corriendo: cerrarla con `Ctrl+C` o cerrar esa terminal |
| `No module named 'pymongo'` o "se está usando el Python global" | No se activó el entorno virtual: active con `.\venv\Scripts\Activate.ps1` (PowerShell) o `venv\Scripts\activate.bat` (CMD) |

Scripts de la base de datos (carpeta `database/`, en Python; se ejecutan con el entorno virtual activado, por ejemplo `python database/01_ddl_colecciones.py`):

| Script | Equivale a | Qué hace |
|---|---|---|
| `01_ddl_colecciones.py` | DDL | Colecciones con validador `$jsonSchema` e índices únicos |
| `02_dml_datos_prueba.py` | DML | Carga los datos de prueba (**borra** los documentos actuales) |
| `03_dcl_usuario_api.py` | DCL | Crea `usr_gastronomia_api` con mínimos privilegios |

Si MongoDB tiene la autenticación activada, ponga en el `.env` `MONGO_USER` y `MONGO_PASSWORD` del usuario creado con el script 03. Si no, déjelos vacíos.

Al arrancar, la API crea los índices únicos (correo, documento, código, NIT...) y, solo si la base está vacía, carga 10 registros por colección.

- API: http://127.0.0.1:3000
- Swagger: http://127.0.0.1:3000/docs
- ReDoc: http://127.0.0.1:3000/redoc

## 4. Usuarios de prueba

| Rol | Correo | Contraseña |
|---|---|---|
| ADMIN | admin@gastronomia.sena.edu.co | Admin123* |
| CAJERO | cajero@gastronomia.sena.edu.co | Cajero123* |
| COCINERO | cocinero@gastronomia.sena.edu.co | Cocinero123* |

## 5. Obtener el token

`POST /api/v1/auth/login` (único endpoint público):

```json
{ "correo": "admin@gastronomia.sena.edu.co", "password": "Admin123*" }
```

Respuesta:

```json
{ "access_token": "eyJhbGciOi...", "token_type": "bearer", "rol": "ADMIN", "id_usuario": 1, "nombres": "Wilson Gomez" }
```

En las demás peticiones se envía el encabezado `Authorization: Bearer <access_token>`. El token dura 120 minutos.
Sin token o token inválido → **401**. Rol sin permiso → **403**.

## 6. Probar en Swagger (/docs)

1. Abra http://127.0.0.1:3000/docs.
2. Despliegue **Autenticación → POST /api/v1/auth/login**, pulse **Try it out**, pegue el JSON del login y pulse **Execute**.
3. Copie el valor de `access_token` (sin comillas).
4. Pulse el botón verde **Authorize** (arriba a la derecha), pegue el token en *Value* y pulse **Authorize** → **Close**. No escriba la palabra `Bearer`: Swagger la agrega.
5. Ya puede usar cualquier endpoint: **Try it out** → editar parámetros/body → **Execute**.
6. Para probar otro rol, pulse **Authorize** → **Logout**, haga login con otro usuario y vuelva a autorizar.

## 7. Probar con Thunder Client (VS Code)

1. Instale la extensión **Thunder Client** y abra el ícono del rayo en la barra lateral.
2. **Importar la colección:** pestaña *Collections* → menú `≡` → **Import** → seleccione `postman_collection.json` de este proyecto.
3. **Variables:** la colección trae `base_url` = `http://127.0.0.1:3000/api/v1`. Si su versión no importa las variables, cree un *Environment* (pestaña *Env*) con:
   - `base_url` = `http://127.0.0.1:3000/api/v1`
   - `token_admin`, `token_cajero`, `token_cocinero` (vacías)
   y márquelo como activo.
4. **Guardar el token automáticamente:** abra *Login ADMIN* → pestaña **Tests** → agregue **Set Env Variable** con `json.access_token` y destino `{{token_admin}}`. Haga lo mismo en *Login CAJERO* (`{{token_cajero}}`) y *Login COCINERO* (`{{token_cocinero}}`).
   Alternativa manual: copie el `access_token` de la respuesta y péguelo en la variable.
5. Ejecute las 3 peticiones de la carpeta **01 - Autenticación**. Cada petición ya tiene en su pestaña **Auth → Bearer** el token del rol que corresponde.
6. Ejecute las carpetas **en orden (01 a 13)**: los IDs de los ejemplos (11, 12, 15, 16...) asumen la base con los datos iniciales. Si ya creó registros antes, use el ID que devuelve cada `POST`.
7. Para una petición nueva a mano: **New Request** → método y URL `{{base_url}}/productos` → pestaña **Auth → Bearer** → `{{token_admin}}` → para POST/PUT/PATCH, pestaña **Body → JSON**.

## 8. Endpoints y roles

| Recurso | Ruta | Roles |
|---|---|---|
| Auth | `POST /auth/login` (público), `POST /auth/registro` (ADMIN), `GET /auth/perfil` | — |
| Usuarios | `/usuarios` | ADMIN |
| Categorías | `/categorias` | ADMIN (consulta: todos) |
| Productos | `/productos`, `/productos/categoria/{id}`, `/productos/{id}/receta`, `/productos/{id}/costo` | ADMIN (consulta: todos; costo: ADMIN y COCINERO) |
| Insumos | `/insumos`, `/insumos/stock-bajo`, `/insumos/por-vencer?dias=7` | ADMIN, COCINERO |
| Recetas | `/recetas` | ADMIN, COCINERO |
| Proveedores | `/proveedores`, `/proveedores/{id}/compras` | ADMIN |
| Compras | `/compras` | ADMIN |
| Clientes | `/clientes`, `/clientes/{id}/pedidos` | ADMIN, CAJERO |
| Pedidos | `/pedidos`, `/pedidos/estado/{estado}`, `PATCH /pedidos/{id}/estado` | ADMIN, CAJERO (estado: también COCINERO) |
| Reportes | `/reportes/ventas?desde=&hasta=`, `/reportes/productos-mas-vendidos?limite=10` | ADMIN |
| Calificaciones | `/calificaciones`, `/calificaciones/producto/{id}` | ADMIN, CAJERO |

Todas las rutas llevan el prefijo `/api/v1`. Cada recurso tiene `GET`, `GET /{id}`, `POST`, `PUT /{id}` y `DELETE /{id}`.

## 9. Reglas de negocio

- **RN01:** la API toma el precio del producto y calcula `subtotal = cantidad × precio_unitario` y el total.
- **RN02:** una compra suma la cantidad a `stock_actual` y actualiza `costo_unitario`. Eliminar la compra revierte el stock.
- **RN03:** al pasar un pedido a `ENTREGADO` se descuentan los insumos según la receta; si no alcanzan → **409** y no se descuenta nada.
- **RN04:** producto, insumo, cliente o proveedor con movimientos → `INACTIVO` (borrado lógico); sin movimientos → borrado físico.
- **RN05:** un pedido `ENTREGADO` o `ANULADO` no se modifica (**409**). Flujo: `PENDIENTE → EN_PREPARACION → ENTREGADO`, y `ANULADO` desde los dos primeros.
- **RN06:** contraseñas con bcrypt; nunca se devuelven en las respuestas.
