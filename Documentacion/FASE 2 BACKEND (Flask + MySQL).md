# Paso 4: Estructura del proyecto
Crea esta estructura de carpetas:
```text
Help_Desk/
├── app/                   # Módulo principal de la aplicación
│   ├── services/          # Lógica de negocio y servicios externos
│   │   └── .gitkeep
│   ├── static/            # Archivos estáticos (CSS, JS, Imágenes)
│   │   ├── css/
│   │   │   └── .gitkeep
│   │   ├── img/
│   │   │   └── .gitkeep
│   │   └── js/
│   │       └── .gitkeep
│   ├── templates/         # Plantillas HTML
│   │   ├── login/
│   │   │   └── login.html
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   └── index.html
│   ├── __init__.py        # Inicialización de la aplicación Flask/paquete
│   ├── forms.py           # Definición de formularios (ej. WTForms)
│   ├── models.py          # Modelos de bases de datos
│   ├── routes.py          # Definición de rutas y controladores
│   └── utils.py           # Funciones de utilidad y helpers
├── config.py              # Configuraciones de entorno y variables globales
├── README.md              # Documentación del proyecto
├── requirements.txt       # Dependencias del proyecto
└── run.py                 # Script de entrada para ejecutar la aplicación
```

# Paso 5: Autenticación

### 5.1 Registro de usuarios

- Solo se pueden registrar usuarios con rol `cliente` desde el formulario público.
    
- Los usuarios con rol `agente` o `admin` solo pueden ser creados por un admin desde el panel de administración.
    

### 5.2 Login con sesiones Flask

- Usar `flask.session` para mantener la sesión del usuario.
    
- Guardar en sesión: `user_id`, `nombre`, `rol`.
    

### 5.3 Hash de contraseñas (bcrypt)

**Código para probar bcrypt en consola (fuera de la app):**

Crea un archivo temporal `test_hash.py` en la raíz de tu proyecto:
```python
# test_hash.py
# Instalar primero: pip install bcrypt

import bcrypt

def generar_hash(contrasena):
    # Generar salt y hash
    salt = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(contrasena.encode('utf-8'), salt)
    return hash_bytes.decode('utf-8')

def verificar_hash(contrasena, hash_guardado):
    return bcrypt.checkpw(contrasena.encode('utf-8'), hash_guardado.encode('utf-8'))

if __name__ == "__main__":
    print("=== PRUEBA DE BCRYPT ===\n")
    texto = input("Introduce una contraseña para hashear: ")
    hash_resultado = generar_hash(texto)
    print(f"\nHash generado: {hash_resultado}\n")
    
    print("=== VERIFICACIÓN ===")
    prueba = input("Introduce la misma contraseña para verificar: ")
    if verificar_hash(prueba, hash_resultado):
        print("Correcto. La contraseña coincide.")
    else:
        print("Incorrecto. La contraseña NO coincide.")
```

**Ejecutar en consola:**
```bash
python test_hash.py
```

**En la app (models.py o utils.py):**

```python
# Ejemplo de cómo se usará
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

# Para hashear al crear usuario
password_hash = bcrypt.generate_password_hash("mi_password").decode('utf-8')

# Para verificar al login
es_correcto = bcrypt.check_password_hash(password_hash_guardado, "password_introducido")
```

### 5.4 Decoradores para proteger rutas

Son **necesarios**. Los crearás en `app/utils.py` o directamente en `app/routes.py`:

**Decoradores a implementar:**

- `@login_requerido` → cualquier usuario logueado (clientes, agentes, admin)
    
- `@rol_requerido('agente')` → solo agentes y admin (herencia)
    
- `@rol_requerido('admin')` → solo admin
    

**Lógica del reto de visibilidad:**  
En la ruta que muestra un ticket específico (`/ticket/<id>`), harás:

```python
# Pseudo-código de la lógica
ticket = obtener_ticket_por_id(id)
if usuario.rol == 'cliente' and ticket.usuario_id != usuario.id:
    # Redirigir con error "No tienes permiso para ver este ticket"
```

# Paso 6: CRUD de tickets (explicado con detalles de UI)
**Ubicación:** Vista `crear_ticket.html` (botón "Nuevo Ticket" en el dashboard)

**Elementos del formulario:**
# Campos del formulario

| Campo       | Tipo de input | ¿Obligatorio? | Observaciones                  |
|-------------|---------------|---------------|--------------------------------|
| Título      | Input text    | ✅ Sí          | Máximo 200 caracteres          |
| Descripción | Textarea      | ✅ Sí          | Mínimo 10 caracteres           |
| Prioridad   | NO aparece    | ❌ No          | La asigna el agente después    |
**omportamiento esperado:**

- Cliente rellena título + descripción
    
- Al enviar POST, se guarda con:
    
    - `estado = 'abierto'`
        
    - `prioridad = NULL` (pendiente de asignar)
        
    - `agente_asignado_id = NULL`
        
    - `usuario_id = id_del_cliente_logueado`

### 6.2 Listado de tickets (index/dashboard)

**Ubicación:** `dashboard.html` (para clientes) e `index.html` (para agentes/admin)

**Para clientes:** Solo ven sus tickets (`usuario_id = session.user_id`)

**Tabla con columnas:**

# Columnas de la tabla

| Columna         | Tipo de dato                  | ¿Se puede ordenar? |
|-----------------|-------------------------------|--------------------|
| ID              | Número                        | Sí                 |
| Título          | Texto                         | No                 |
| Estado          | Badge de color                | Sí                 |
| Prioridad       | Badge (solo si asignada)      | Sí                 |
| Fecha creación  | Fecha                         | Sí                 |
| Agente asignado | Nombre o "Sin asignar"        | No                 |
| Acciones        | Botones                       | N/A                |

**Filtros (encima de la tabla):**

- Selector de estado: `Todos | Abierto | En progreso | Resuelto | Cerrado | Cancelado`
    
- Selector de prioridad: `Todas | Baja | Media | Alta | Urgente`
    

### 6.3 Vista detalle del ticket

**Ubicación:** `ticket_detalle.html` (ruta `/ticket/<id>`)

**Secciones:**

1. **Encabezado:** ID, título, estado (badge), prioridad (badge)
    
2. **Información principal:** Descripción completa, fecha creación, quién lo creó
    
3. **Asignación:** Muestra agente asignado o botón "Asignarme" (si eres agente)
    
4. **Historial de respuestas:** Lista con cada respuesta (avatar, nombre, fecha, mensaje)
    
5. **Formulario de nueva respuesta:** Textarea + botón "Responder"
    
6. **Botones de acción (solo visibles según rol):**
    
    - Cambiar estado (agentes/admin): Selector desplegable
        
    - Cancelar ticket (cliente): Botón rojo (solo si cumple regla 30 min)
        
    - Asignarse (agente): Botón verde

# Paso 7: Sistema de respuestas (explicado en detalle)
### 7.1 Lógica de guardado

Cuando un usuario (cliente, agente o admin) envía una respuesta:

**Validaciones previas:**

- El ticket debe existir
    
- El usuario debe tener permiso para responder (cliente → solo sus tickets / agente o admin → cualquier ticket)
    
- El mensaje no puede estar vacío
    

**Acciones en BD:**

1. `INSERT INTO respuestas (ticket_id, usuario_id, mensaje, created_at) VALUES (...)`
    
2. Si el ticket estaba en estado `resuelto` o `cerrado` y un **cliente** responde → cambiar automáticamente estado a `abierto` (el cliente reabre el ticket)
    
3. Actualizar `tickets.updated_at`
    

### 7.2 Visualización en frontend

- Orden: **De más antigua a más nueva** (la primera respuesta es la más vieja abajo del ticket)
    
- Cada respuesta muestra:
    
    - Nombre del usuario + rol (ej: "Marco (cliente)" o "Ana (agente)")
        
    - Fecha y hora (formato: `dd/mm/yyyy HH:MM`)
        
    - El mensaje en un cuadro con fondo diferenciado según rol (cliente = gris claro, agente = azul claro)
        

### 7.3 Notificaciones (extra, puede ir después)

Al guardar una respuesta:

- Si responde cliente → enviar email al agente asignado (o a todos los agentes si no hay asignado)
    
- Si responde agente → enviar email al cliente

# Paso 8: Gestión de estados (vista de cards con botones)
### 8.1 Vista de lista de tickets para agente

El agente ve una **tabla o cards** con todos los tickets (sin asignar o asignados a él). Cada ticket tiene un botón **"Gestionar"** o **"Seleccionar"**.

**Ejemplo visual de cada fila/card:**
```text
┌─────────────────────────────────────────────────────────────┐
│ Ticket #14 - Problema con facturación                       │
│ Cliente: marco@email.com | Creado: 10/04/2025 10:30         │
│ Estado: abierto (sin badge) | Prioridad: (sin asignar)      │
│                                                             │
│ [SELECCIONAR Y GESTIONAR] ← botón principal                 │
└─────────────────────────────────────────────────────────────┘
```
### 8.2 Modal al hacer clic en "Seleccionar y gestionar"

Al hacer clic, se abre un **modal (popup)** con:
```text
┌─────────────────────────────────────────────────────────┐
│  GESTIONAR TICKET #14                        [X]        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Título: Problema con facturación                       │
│  Cliente: marco@email.com                               │
│                                                         │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│  📌 ASIGNAR PRIORIDAD (obligatorio)                     │
│  ○ Baja    ○ Media    ○ Alta    ○ Urgente               │
│                                                         │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│  🔄 CAMBIAR ESTADO (obligatorio)                        │
│  ○ Abierto    ○ En progreso    ○ Resuelto    ○ Cerrado  │
│                                                         │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│  👤 ASIGNAR A (opcional si ya está asignado)            │
│  [Selector: Yo mismo ▼]  (o elegir otro agente)        │
│                                                         │
│  ─────────────────────────────────────────────────────  │
│                                                         │
│     [CANCELAR]              [GUARDAR CAMBIOS]           │
└─────────────────────────────────────────────────────────┘
```

**Reglas dentro del modal:**

- Prioridad y estado deben seleccionarse antes de guardar (validación)
    
- Si el ticket ya tenía prioridad/estado, aparecen preseleccionados
    
- Al guardar, se actualizan en la base de datos
    

### 8.3 Después de guardar (cierre del modal)

Una vez guardado, el ticket **ya tiene prioridad y estado definidos**. Ahora, en la vista principal (tabla/cards), ese ticket muestra:

**Badges visibles:**

- Estado: `abierto` (azul), `en progreso` (naranja), `resuelto` (verde), `cerrado` (gris)
    
- Prioridad: `baja` (gris), `media` (azul), `alta` (naranja), `urgente` (rojo)
    

**Ahora aparecen los botones de acciones en la card/fila del ticket:**
```text
┌─────────────────────────────────────────────────────────────────────┐
│ Ticket #14 - Problema con facturación                               │
│ Cliente: marco@email.com | Creado: 10/04/2025 10:30                 │
│ Estado: [EN PROGRESO]  Prioridad: [ALTA]                            │
│                                                                     │
│ [RESPONDER]  [REASIGNAR]  [CAMBIAR ESTADO]  [HISTORIAL]             │
└─────────────────────────────────────────────────────────────────────┘
```

### 8.4 Botones de acción (después de asignar prioridad+estado)
# Botones de acciones

| Botón        | Acción                                                       | ¿Cómo se muestra?                          |
|--------------|--------------------------------------------------------------|--------------------------------------------|
| RESPONDER    | Abre modal con textarea para escribir respuesta               | SweetAlert con input textarea               |
| REASIGNAR    | Abre selector de agentes (solo si admin o agente con permisos)| Modal pequeño con lista de agentes          |
| CAMBIAR ESTADO | Abre selector de nuevos estados (evoluciones permitidas)    | Modal con radios o botones                  |
| HISTORIAL    | Muestra logs_estados (quién cambió y cuándo)                  | SweetAlert o modal con tabla                |

### 8.5 SweetAlert para confirmaciones y feedback

**Ejemplo 1: Confirmar cambio de estado**
```js
// Cuando el agente hace clic en "CAMBIAR ESTADO"
Swal.fire({
  title: 'Cambiar estado',
  text: '¿A qué estado quieres mover este ticket?',
  input: 'select',
  inputOptions: {
    'en_progreso': 'En progreso',
    'resuelto': 'Resuelto',
    'cerrado': 'Cerrado'
  },
  showCancelButton: true,
  confirmButtonText: 'Cambiar'
}).then((result) => {
  if (result.isConfirmed) {
    // Enviar fetch al backend
    fetch(`/ticket/14/cambiar_estado`, {
      method: 'POST',
      body: JSON.stringify({nuevo_estado: result.value})
    }).then(() => {
      Swal.fire('Actualizado', 'El estado ha cambiado', 'success');
      // Recargar la fila/card del ticket
    });
  }
});
```

**Ejemplo 2: Responder ticket (con SweetAlert)**
```js
Swal.fire({
  title: 'Responder ticket',
  input: 'textarea',
  inputPlaceholder: 'Escribe tu respuesta aquí...',
  inputAttributes: {
    'aria-label': 'Escribe tu respuesta'
  },
  showCancelButton: true,
  confirmButtonText: 'Enviar respuesta'
}).then((result) => {
  if (result.isConfirmed && result.value) {
    // Enviar respuesta al backend
    fetch(`/ticket/14/responder`, {
      method: 'POST',
      body: JSON.stringify({mensaje: result.value})
    }).then(() => {
      Swal.fire('Enviado', 'Respuesta agregada al ticket', 'success');
    });
  }
});
```

**Ejemplo 3: Éxito al guardar desde el modal principal**
```js
// Después de guardar prioridad+estado desde el modal principal
Swal.fire({
  icon: 'success',
  title: 'Ticket actualizado',
  text: 'Prioridad y estado asignados correctamente',
  timer: 2000,
  showConfirmButton: false
});
```

### 8.6 Flujo completo (resumen para que lo entiendas)
```text
1. Agente ve lista de tickets
2. Hace clic en "SELECCIONAR Y GESTIONAR" en un ticket
3. Se abre MODAL con:
   - Radio buttons para PRIORIDAD
   - Radio buttons para ESTADO
   - Selector opcional para ASIGNAR AGENTE
4. Agente elige, hace clic en GUARDAR
5. SweetAlert confirma "Ticket actualizado"
6. Modal se cierra
7. La card/fila del ticket ahora muestra:
   - Badges de estado y prioridad
   - Botones: RESPONDER, REASIGNAR, CAMBIAR ESTADO, HISTORIAL
8. Cada botón abre SweetAlert o modal para su acción específica
```

