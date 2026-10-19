// ============================================================
// PROYECTO FORMATIVO: API REST GASTRONOMIA - SENA CGDSS
// FICHA: 3312744
// INSTRUCTIVO: EA4
// SCRIPT: 04_mongo_calificaciones.js
// MOTOR: MongoDB 7.0
// BASE DE DATOS: bd_gastronomia_nosql
// COLECCIÓN: calificaciones
// ============================================================

const dbName = "bd_gastronomia_nosql";
const dbInstance = db.getSiblingDB(dbName);

// Eliminar colección si existe para inicialización limpia
dbInstance.calificaciones.drop();

// Crear colección con validador $jsonSchema según el documento de ejemplo
dbInstance.createCollection("calificaciones", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["id_pedido", "id_cliente", "fecha", "calificacion_servicio", "comentario", "productos"],
      properties: {
        id_pedido: {
          bsonType: "int",
          description: "Identificador del pedido calificado (entero obligatorio)"
        },
        id_cliente: {
          bsonType: "int",
          description: "Identificador del cliente que califica (entero obligatorio)"
        },
        fecha: {
          bsonType: "string",
          description: "Fecha y hora de la calificacion en formato ISO-8601"
        },
        calificacion_servicio: {
          bsonType: "int",
          minimum: 1,
          maximum: 5,
          description: "Calificacion del servicio general (1 a 5)"
        },
        comentario: {
          bsonType: "string",
          description: "Comentario u opinion cualitativa del cliente"
        },
        productos: {
          bsonType: "array",
          description: "Lista de productos evaluados en el pedido",
          items: {
            bsonType: "object",
            required: ["id_producto", "nombre", "calificacion"],
            properties: {
              id_producto: {
                bsonType: "int",
                description: "Identificador del producto evaluado"
              },
              nombre: {
                bsonType: "string",
                description: "Nombre del producto evaluado"
              },
              calificacion: {
                bsonType: "int",
                minimum: 1,
                maximum: 5,
                description: "Puntuacion del producto especifico (1 a 5)"
              }
            }
          }
        }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
});

// Crear índices para optimización de consultas
dbInstance.calificaciones.createIndex({ "id_pedido": 1 }, { unique: true });
dbInstance.calificaciones.createIndex({ "id_cliente": 1 });
dbInstance.calificaciones.createIndex({ "productos.id_producto": 1 });

// Inserción de documentos de prueba
dbInstance.calificaciones.insertMany([
  {
    id_pedido: NumberInt(1),
    id_cliente: NumberInt(1),
    fecha: "2026-10-10T12:45:00",
    calificacion_servicio: NumberInt(5),
    comentario: "Excelente sabor tradicional y atencion muy rapida en la mesa.",
    productos: [
      { id_producto: NumberInt(1), nombre: "Bandeja Paisa", calificacion: NumberInt(5) },
      { id_producto: NumberInt(3), nombre: "Jugo de Lulo", calificacion: NumberInt(5) }
    ]
  },
  {
    id_pedido: NumberInt(2),
    id_cliente: NumberInt(2),
    fecha: "2026-10-10T13:10:00",
    calificacion_servicio: NumberInt(4),
    comentario: "El ajiaco estaba delicioso, llego bien caliente el empaque.",
    productos: [
      { id_producto: NumberInt(2), nombre: "Ajiaco Santafereño", calificacion: NumberInt(5) }
    ]
  },
  {
    id_pedido: NumberInt(3),
    id_cliente: NumberInt(3),
    fecha: "2026-10-11T13:40:00",
    calificacion_servicio: NumberInt(5),
    comentario: "El café huilense tiene un aroma inigualable. Gran preparacion.",
    productos: [
      { id_producto: NumberInt(1), nombre: "Bandeja Paisa", calificacion: NumberInt(4) },
      { id_producto: NumberInt(4), nombre: "Café Especial Huila", calificacion: NumberInt(5) }
    ]
  },
  {
    id_pedido: NumberInt(4),
    id_cliente: NumberInt(4),
    fecha: "2026-10-12T13:30:00",
    calificacion_servicio: NumberInt(5),
    comentario: "Excelente servicio para eventos de coordinacion.",
    productos: [
      { id_producto: NumberInt(1), nombre: "Bandeja Paisa", calificacion: NumberInt(5) }
    ]
  },
  {
    id_pedido: NumberInt(5),
    id_cliente: NumberInt(5),
    fecha: "2026-10-13T13:50:00",
    calificacion_servicio: NumberInt(4),
    comentario: "Porcion generosa y presentacion impecable.",
    productos: [
      { id_producto: NumberInt(1), nombre: "Bandeja Paisa", calificacion: NumberInt(4) }
    ]
  },
  {
    id_pedido: NumberInt(6),
    id_cliente: NumberInt(6),
    fecha: "2026-10-14T12:55:00",
    calificacion_servicio: NumberInt(5),
    comentario: "Las empanadas y el pan de bono recien horneados estaban increibles.",
    productos: [
      { id_producto: NumberInt(6), nombre: "Empanada de Carne", calificacion: NumberInt(5) },
      { id_producto: NumberInt(5), nombre: "Pan de Bono", calificacion: NumberInt(5) }
    ]
  }
]);

print("Colección 'calificaciones' creada exitosamente con esquema de validación e índices.");
