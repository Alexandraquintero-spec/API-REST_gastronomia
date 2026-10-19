"""
Script integral de verificación funcional y de seguridad de la API Gastronomía.
Utiliza únicamente la librería estándar de Python (urllib y json) para no requerir dependencias adicionales.
"""
from decimal import Decimal
import json
import urllib.error
import urllib.request

BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("INICIANDO VERIFICACIÓN DE REQUISITOS EA4 (API GASTRONOMÍA)")
print("=" * 60)


def request(method, path, body=None, token=None):
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            res_body = response.read().decode("utf-8")
            json_data = json.loads(res_body) if res_body else {}
            return status_code, json_data
    except urllib.error.HTTPError as e:
        status_code = e.code
        res_body = e.read().decode("utf-8")
        try:
            json_data = json.loads(res_body)
        except Exception:
            json_data = {"raw": res_body}
        return status_code, json_data


# 1. Probar ruta raíz y OpenAPI
status_code, data = request("GET", "/")
assert status_code == 200, f"Error en raíz: {data}"
print("[PASS] 1. Ruta raíz responde 200 OK")

status_code, data = request("GET", "/openapi.json")
assert status_code == 200, f"Error en openapi.json: {data}"
print("[PASS] 2. Swagger / OpenAPI schema responde 200 OK")

# 2. Probar 401 sin token en endpoint privado
status_code, data = request("GET", "/api/v1/usuarios")
assert status_code == 401, f"Se esperaba 401 sin token, obtenido: {status_code}"
print("[PASS] 3. Endpoint privado sin token retorna 401 Unauthorized")

# 3. Probar Login ADMIN
login_payload = {
    "correo": "admin@gastronomia.sena.edu.co",
    "password": "Admin123*",
}
status_code, data = request("POST", "/api/v1/auth/login", login_payload)
assert status_code == 200, f"Error en login ADMIN: {data}"
admin_token = data["access_token"]
print("[PASS] 4. Login ADMIN exitoso y token JWT retornado")

# 4. Probar Login CAJERO
status_code, data = request(
    "POST",
    "/api/v1/auth/login",
    {"correo": "cajero@gastronomia.sena.edu.co", "password": "Cajero123*"},
)
assert status_code == 200, f"Error en login CAJERO: {data}"
cajero_token = data["access_token"]
print("[PASS] 5. Login CAJERO exitoso")

# 5. Probar Login COCINERO
status_code, data = request(
    "POST",
    "/api/v1/auth/login",
    {"correo": "cocinero@gastronomia.sena.edu.co", "password": "Cocinero123*"},
)
assert status_code == 200, f"Error en login COCINERO: {data}"
cocinero_token = data["access_token"]
print("[PASS] 6. Login COCINERO exitoso")

# 6. Probar 403 con rol incorrecto
status_code, data = request("GET", "/api/v1/usuarios", token=cajero_token)
assert status_code == 403, f"Se esperaba 403 para CAJERO en /usuarios, obtenido: {status_code}"
print("[PASS] 7. Validación de roles: CAJERO recibe 403 Forbidden en recurso exclusivo de ADMIN")

status_code, data = request(
    "POST",
    "/api/v1/categorias",
    {"nombre": "Prueba Denegada", "descripcion": "Desc"},
    token=cocinero_token,
)
assert status_code == 403, f"Se esperaba 403 para COCINERO en POST /categorias, obtenido: {status_code}"
print("[PASS] 8. Validación de roles: COCINERO recibe 403 Forbidden en creación de categoría")

# 7. RN06: Contraseñas cifradas y NUNCA devueltas en respuestas
status_code, usuarios = request("GET", "/api/v1/usuarios", token=admin_token)
assert status_code == 200
for u in usuarios:
    assert "password" not in u, f"FALLO DE SEGURIDAD RN06: contraseña expuesta en {u}"
print("[PASS] 9. RN06 verificado: las contraseñas nunca se exponen en las respuestas de la API")

# 8. RN01: Creación de pedido y cálculo de subtotales y total por la API
pedido_payload = {
    "id_cliente": 1,
    "tipo_pedido": "MESA",
    "observaciones": "Verificación RN01",
    "detalles": [
        {"id_producto": 1, "cantidad": 2},
        {"id_producto": 3, "cantidad": 3},
    ],
}
status_code, nuevo_pedido = request("POST", "/api/v1/pedidos", pedido_payload, token=admin_token)
assert status_code == 201, f"Error al crear pedido RN01: {nuevo_pedido}"
assert Decimal(str(nuevo_pedido["total"])) == Decimal("51000.00"), f"Total esperado 51000, obtenido {nuevo_pedido['total']}"
id_pedido_creado = nuevo_pedido["id_pedido"]
print(f"[PASS] 10. RN01 verificado: total calculado exactamente por la API (51000.00) para pedido ID {id_pedido_creado}")

# 9. RN02: Registrar compra, incremento de stock_actual y actualización de costo_unitario
status_code, insumo_antes = request("GET", "/api/v1/insumos/1", token=admin_token)
stock_previo = Decimal(str(insumo_antes["stock_actual"]))

compra_payload = {
    "numero_factura": "TEST-FAC-999",
    "id_proveedor": 2,
    "detalles": [
        {"id_insumo": 1, "cantidad": 10.00, "costo_unitario": 17500.00}
    ],
}
status_code, compra_res = request("POST", "/api/v1/compras", compra_payload, token=admin_token)
assert status_code == 201, f"Error al registrar compra RN02: {compra_res}"
status_code, insumo_despues = request("GET", "/api/v1/insumos/1", token=admin_token)
assert Decimal(str(insumo_despues["stock_actual"])) == stock_previo + Decimal("10.00"), "Stock no se incrementó correctamente"
assert Decimal(str(insumo_despues["costo_unitario"])) == Decimal("17500.00"), "Costo unitario no se actualizó"
print("[PASS] 11. RN02 verificado: compra incrementó existencias y actualizó costo unitario")

# 10. RN03 y RN05: Flujo de estados de pedido
status_code, data = request(
    "PATCH",
    f"/api/v1/pedidos/{id_pedido_creado}/estado",
    {"estado": "EN_PREPARACION"},
    token=cocinero_token,
)
assert status_code == 200, f"Error al pasar a EN_PREPARACION: {data}"
print("[PASS] 12. Flujo de estados: pedido pasó a EN_PREPARACION con rol COCINERO")

# Pasar a ENTREGADO con stock suficiente: debe descontar insumos
status_code, insumo_lulo_antes = request("GET", "/api/v1/insumos/4", token=admin_token)
stock_lulo_antes = Decimal(str(insumo_lulo_antes["stock_actual"]))

status_code, data = request(
    "PATCH",
    f"/api/v1/pedidos/{id_pedido_creado}/estado",
    {"estado": "ENTREGADO"},
    token=cocinero_token,
)
assert status_code == 200, f"Error al pasar a ENTREGADO: {data}"

status_code, insumo_lulo_despues = request("GET", "/api/v1/insumos/4", token=admin_token)
stock_lulo_despues = Decimal(str(insumo_lulo_despues["stock_actual"]))
assert stock_lulo_despues == stock_lulo_antes - Decimal("0.450"), f"No se descontó el insumo: antes {stock_lulo_antes}, despues {stock_lulo_despues}"
print("[PASS] 13. RN03 verificado: pedido ENTREGADO descontó inventario según recetas")

# Probar RN05: Un pedido ENTREGADO no se puede modificar (409)
status_code, data = request(
    "PATCH",
    f"/api/v1/pedidos/{id_pedido_creado}/estado",
    {"estado": "ANULADO"},
    token=cocinero_token,
)
assert status_code == 409, f"Se esperaba 409 al modificar pedido ENTREGADO, obtenido: {status_code}"
print("[PASS] 14. RN05 verificado: pedido ENTREGADO no puede modificarse (409 Conflict)")

# Probar RN03 con stock insuficiente
pedido_enorme = {
    "id_cliente": 2,
    "tipo_pedido": "EVENTO",
    "detalles": [{"id_producto": 1, "cantidad": 5000}],
}
status_code, res_enorme = request("POST", "/api/v1/pedidos", pedido_enorme, token=admin_token)
id_enorme = res_enorme["id_pedido"]
request("PATCH", f"/api/v1/pedidos/{id_enorme}/estado", {"estado": "EN_PREPARACION"}, token=cocinero_token)

status_code, insumo_carne_antes = request("GET", "/api/v1/insumos/1", token=admin_token)
stock_carne_antes = Decimal(str(insumo_carne_antes["stock_actual"]))

status_code, res_sin_stock = request(
    "PATCH",
    f"/api/v1/pedidos/{id_enorme}/estado",
    {"estado": "ENTREGADO"},
    token=cocinero_token,
)
assert status_code == 409, f"Se esperaba 409 por stock insuficiente, obtenido: {status_code}"

status_code, insumo_carne_despues = request("GET", "/api/v1/insumos/1", token=admin_token)
stock_carne_despues = Decimal(str(insumo_carne_despues["stock_actual"]))
assert stock_carne_despues == stock_carne_antes, "El stock no debe modificarse si se produce error 409"
print("[PASS] 15. RN03 verificado: 409 Conflict por stock insuficiente sin descontar existencias")

# 11. RN04: Borrado lógico si tiene movimientos
status_code, data = request("DELETE", "/api/v1/productos/1", token=admin_token)
assert status_code == 200
status_code, prod1 = request("GET", "/api/v1/productos/1", token=admin_token)
assert prod1["estado"] == "INACTIVO", f"El producto debió quedar INACTIVO, quedó {prod1['estado']}"
print("[PASS] 16. RN04 verificado: producto con movimientos pasó a INACTIVO (borrado lógico)")

status_code, data = request("DELETE", "/api/v1/insumos/1", token=admin_token)
assert status_code == 200
status_code, ins1 = request("GET", "/api/v1/insumos/1", token=admin_token)
assert ins1["estado"] == "INACTIVO", f"El insumo debió quedar INACTIVO, quedó {ins1['estado']}"
print("[PASS] 17. RN04 verificado: insumo con movimientos pasó a INACTIVO (borrado lógico)")

# Crear producto sin movimientos y eliminarlo físicamente
status_code, prod_nuevo = request(
    "POST",
    "/api/v1/productos",
    {
        "codigo": "PRD-TEMP",
        "nombre": "Producto Temporal",
        "precio_venta": 10000.00,
        "unidad_venta": "Unidad",
        "id_categoria": 1,
    },
    token=admin_token,
)
id_temp = prod_nuevo["id_producto"]
status_code, data = request("DELETE", f"/api/v1/productos/{id_temp}", token=admin_token)
assert status_code == 200 and data["tipo_borrado"] == "FISICO"
status_code, data = request("GET", f"/api/v1/productos/{id_temp}", token=admin_token)
assert status_code == 404
print("[PASS] 18. RN04 verificado: producto sin movimientos se eliminó físicamente")

# 12. Consultas y Reportes
status_code, datos_costo = request("GET", "/api/v1/productos/2/costo", token=cocinero_token)
assert status_code == 200
assert "costo_produccion" in datos_costo and "margen_ganancia" in datos_costo
print(f"[PASS] 19. RF06 Cálculo de costo: {datos_costo['nombre']} - Costo: {datos_costo['costo_produccion']}, Margen: {datos_costo['margen_ganancia']}")

status_code, data_ventas = request("GET", "/api/v1/reportes/ventas", token=admin_token)
assert status_code == 200
print(f"[PASS] 20. RF11 Reporte de ventas: {data_ventas}")

status_code, data_top = request("GET", "/api/v1/reportes/productos-mas-vendidos?limite=5", token=admin_token)
assert status_code == 200
print(f"[PASS] 21. RF11 Productos más vendidos: {len(data_top)} productos en ranking")

status_code, data_bajo = request("GET", "/api/v1/insumos/stock-bajo", token=cocinero_token)
assert status_code == 200
print(f"[PASS] 22. RF07 Insumos stock bajo: {len(data_bajo)} insumos")

status_code, data_vencer = request("GET", "/api/v1/insumos/por-vencer?dias=30", token=cocinero_token)
assert status_code == 200
print(f"[PASS] 23. RF07 Insumos por vencer: {len(data_vencer)} insumos")

# 13. MongoDB Calificaciones
status_code, data_calif = request("GET", "/api/v1/calificaciones", token=admin_token)
assert status_code == 200
assert len(data_calif) >= 6
print(f"[PASS] 24. RF12 MongoDB calificaciones listadas: {len(data_calif)} documentos")

status_code, data_prom = request("GET", "/api/v1/calificaciones/producto/1", token=admin_token)
assert status_code == 200
assert "promedio_calificacion" in data_prom
print(f"[PASS] 25. RF12 MongoDB calificación promedio producto 1: {data_prom['promedio_calificacion']}")

print("=" * 60)
print("¡TODAS LAS PRUEBAS AUTOMATIZADAS PASARON CON ÉXITO (100%)!")
print("=" * 60)
