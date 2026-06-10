# Paso 1: Roles y permisos

| Acción                                | Cliente | Agente | Admin |
|---------------------------------------|---------|--------|-------|
| Crear ticket                          | ✅      | ✅     | ✅    |
| Ver sus propios tickets               | ✅      | ✅     | ✅    |
| Ver tickets de otros                  | ❌      | ✅     | ✅    |
| Ver respuestas de sus tickets         | ✅      | ✅     | ✅    |
| Cancelar ticket (con límite de tiempo)| ✅      | ❌     | ✅    |
| Asignarse tickets                     | ❌      | ✅     | ✅    |
| Cambiar estados del ticket            | ❌      | ✅     | ✅    |
| Responder a cualquier ticket          | ❌      | ✅     | ✅    |
| Crear/eliminar agentes                | ❌      | ❌     | ✅    |
| Ver estadísticas globales             | ❌      | ❌     | ✅    |
| Borrar tickets (soft delete)          | ❌      | ❌     | ✅    |
| Recibir reportes por email con filtros| ❌      | ❌     | ✅    |

**Regla de cancelación:**  
El cliente puede cancelar su ticket solo si el ticket está en estado **"abierto"** y fue creado hace menos de **30 minutos**.

---

# Paso 2: Base de datos (tablas y relaciones)
[[Script para MySQL Workbench 8.0 CE]]
## Tabla 1: usuarios
- id (PK, autoincrement)  
- nombre (VARCHAR(100))  
- email (VARCHAR(100), único)  
- password_hash (VARCHAR(255))  
- rol (ENUM: 'cliente', 'agente', 'admin')  
- fecha_registro (DATETIME, default CURRENT_TIMESTAMP)  

## Tabla 2: tickets
- id (PK, autoincrement)  
- titulo (VARCHAR(200))  
- descripcion (TEXT)  
- prioridad (ENUM: 'baja', 'media', 'alta', 'urgente') → asigna el agente  
- estado (ENUM: 'abierto', 'en_progreso', 'resuelto', 'cerrado', 'cancelado')  
- usuario_id (FK → usuarios.id)  
- agente_asignado_id (FK → usuarios.id, NULL si sin asignar)  
- created_at (DATETIME, default CURRENT_TIMESTAMP)  
- updated_at (DATETIME, on update CURRENT_TIMESTAMP)  
- cancelado_por_cliente (BOOLEAN, default FALSE)  

## Tabla 3: respuestas
- id (PK, autoincrement)  
- ticket_id (FK → tickets.id, ON DELETE CASCADE)  
- usuario_id (FK → usuarios.id)  
- mensaje (TEXT)  
- created_at (DATETIME, default CURRENT_TIMESTAMP)  

## Tabla 4: logs_estados
- id (PK, autoincrement)  
- ticket_id (FK → tickets.id, ON DELETE CASCADE)  
- estado_anterior (ENUM: 'abierto', 'en_progreso', 'resuelto', 'cerrado', 'cancelado')  
- estado_nuevo (ENUM: 'abierto', 'en_progreso', 'resuelto', 'cerrado', 'cancelado')  
- cambiado_por (FK → usuarios.id)  
- fecha_cambio (DATETIME, default CURRENT_TIMESTAMP)  

## Tabla 5: reportes_enviados
- id (PK, autoincrement)  
- enviado_a_email (VARCHAR(100))  
- filtros_usados (JSON) → ej: {"estado": "abierto", "prioridad": "alta"}  
- fecha_envio (DATETIME, default CURRENT_TIMESTAMP)  

### Relaciones clave
- usuarios 1 → N tickets  
- usuarios 1 → N respuestas  
- tickets 1 → N respuestas  
- tickets 1 → N logs_estados  

---

# Paso 3: Estados y prioridades

## Flujo de estados
> [!info] Flujo de Estados
> **Ruta principal:** `abierto` ➔ `en_progreso` ➔ `resuelto` ➔ `cerrado`
> 
> **Rutas de cancelación:** 
> ↳ Desde `abierto` ➔ `cancelado`
> ↳ Desde `en_progreso` ➔ `cancelado`


## Prioridades (solo agente)
- **baja** → No urgente, se atiende cuando haya tiempo  
- **media** → Normal, tiempo de respuesta 24h  
- **alta** → Importante, tiempo de respuesta 4h  
- **urgente** → Crítico, respuesta inmediata  

**¿El cliente puede elegir prioridad?** ❌ No. Solo el agente la asigna al tomar el ticket.

