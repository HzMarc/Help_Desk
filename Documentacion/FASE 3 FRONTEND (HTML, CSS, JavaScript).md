### Paso 11: Estructura de plantillas base (Jinja2 + Bootstrap 5 + SweetAlert)

**11.1 `base.html` - Layout principal**

Elementos obligatorios:

- **CDNs en `<head>`:**
```html
	<!-- Bootstrap 5 CSS -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<!-- Font Awesome (iconos) -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<!-- SweetAlert2 CSS (opcional, la JS ya trae estilos) -->
```

- **Scripts antes de cerrar `</body>`:**
```html
	<!-- Bootstrap JS + Popper -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
<!-- SweetAlert2 JS -->
<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
<!-- Tu JS personalizado -->
<script src="{{ url_for('static', filename='js/main.js') }}"></script>
```

- **Navbar dinámico según rol:**
    
    - Si `session.rol == 'cliente'`: enlaces a "Mis Tickets", "Nuevo Ticket"
        
    - Si `session.rol == 'agente'`: enlaces a "Todos los tickets", "Sin asignar", "Mi panel"
        
    - Si `session.rol == 'admin'`: enlaces a "Dashboard Admin", "Gestión de agentes", "Reportes"
        
- **Bloque de mensajes flash** (para errores de permisos o validaciones simples)

### Paso 12: Vista de tickets para agente (`tickets_agente.html`)

**12.1 Diseño general**

- Título: "Gestión de tickets"
    
- Subtítulo: "Selecciona un ticket para asignar prioridad y estado"
    

**12.2 Tabla o grid de tickets** (usa Bootstrap grid para cards)

**Cada card tiene:**
```html
<div class="card mb-3 ticket-card" data-ticket-id="14">
  <div class="card-body">
    <h5 class="card-title">Ticket #14 - Problema con facturación</h5>
    <p class="card-text">
      <strong>Cliente:</strong> marco@email.com<br>
      <strong>Creado:</strong> 10/04/2025 10:30
    </p>
    <!-- Badges de estado y prioridad (si existen) -->
    <div class="mb-2">
      <span class="badge bg-secondary">Estado: sin asignar</span>
      <span class="badge bg-secondary">Prioridad: sin asignar</span>
    </div>
    <!-- Botón principal -->
    <button class="btn btn-primary btn-gestionar" data-id="14">
      <i class="fas fa-clipboard-list"></i> Seleccionar y gestionar
    </button>
    <!-- Botones de acción (ocultos inicialmente, se muestran tras gestionar) -->
    <div class="acciones-ticket d-none mt-3">
      <button class="btn btn-sm btn-outline-success btn-responder" data-id="14">
        <i class="fas fa-reply"></i> Responder
      </button>
      <button class="btn btn-sm btn-outline-warning btn-reasignar" data-id="14">
        <i class="fas fa-user-plus"></i> Reasignar
      </button>
      <button class="btn btn-sm btn-outline-info btn-cambiar-estado" data-id="14">
        <i class="fas fa-exchange-alt"></i> Cambiar estado
      </button>
      <button class="btn btn-sm btn-outline-secondary btn-historial" data-id="14">
        <i class="fas fa-history"></i> Historial
      </button>
    </div>
  </div>
</div>
```

**12.3 Lógica de visibilidad de botones**

- Por defecto: solo se ve el botón "Seleccionar y gestionar"
    
- Cuando el ticket ya tiene `prioridad NOT NULL` y `estado != 'abierto'` (o al menos prioridad asignada), se muestran los botones de acción
    
- Esto se controla desde el backend al renderizar la plantilla (pasando una variable `gestionado = True/False`)
    

### Paso 13: Modal de gestión (prioridad + estado)

**13.1 HTML del modal** (se incluye una vez en `base.html` o en la misma plantilla)
```html
<div class="modal fade" id="modalGestionTicket" tabindex="-1">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">Gestionar ticket <span id="modalTicketId"></span></h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
      </div>
      <div class="modal-body">
        <p><strong>Título:</strong> <span id="modalTitulo"></span></p>
        <p><strong>Cliente:</strong> <span id="modalCliente"></span></p>
        
        <hr>
        
        <label class="form-label fw-bold">📌 Asignar prioridad (obligatorio)</label>
        <div class="mb-3">
          <div class="form-check form-check-inline">
            <input class="form-check-input" type="radio" name="prioridad" value="baja"> Baja
          </div>
          <div class="form-check form-check-inline">
            <input class="form-check-input" type="radio" name="prioridad" value="media"> Media
          </div>
          <div class="form-check form-check-inline">
            <input class="form-check-input" type="radio" name="prioridad" value="alta"> Alta
          </div>
          <div class="form-check form-check-inline">
            <input class="form-check-input" type="radio" name="prioridad" value="urgente"> Urgente
          </div>
        </div>
        
        <label class="form-label fw-bold">🔄 Cambiar estado (obligatorio)</label>
        <div class="mb-3">
          <div class="form-check form-check-inline">
            <input class="form-check-input" type="radio" name="estado" value="abierto"> Abierto
          </div>
          <div class="form-check form-check-inline">
            <input class="form-check-input" type="radio" name="estado" value="en_progreso"> En progreso
          </div>
          <div class="form-check form-check-inline">
            <input class="form-check-input" type="radio" name="estado" value="resuelto"> Resuelto
          </div>
          <div class="form-check form-check-inline">
            <input class="form-check-input" type="radio" name="estado" value="cerrado"> Cerrado
          </div>
        </div>
        
        <label class="form-label fw-bold">👤 Asignar a</label>
        <select class="form-select" id="selectAgente">
          <option value="yo">Yo mismo</option>
          <!-- Aquí se cargan otros agentes desde backend -->
        </select>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
        <button type="button" class="btn btn-primary" id="btnGuardarGestion">Guardar cambios</button>
      </div>
    </div>
  </div>
</div>
```

**13.2 JavaScript para abrir modal y cargar datos**
```js
// Cuando se hace clic en "Seleccionar y gestionar"
document.querySelectorAll('.btn-gestionar').forEach(btn => {
  btn.addEventListener('click', async function() {
    const ticketId = this.dataset.id;
    
    // Fetch para obtener datos del ticket (título, cliente, prioridad actual, estado actual)
    const response = await fetch(`/api/ticket/${ticketId}`);
    const ticket = await response.json();
    
    // Llenar modal
    document.getElementById('modalTicketId').textContent = `#${ticketId}`;
    document.getElementById('modalTitulo').textContent = ticket.titulo;
    document.getElementById('modalCliente').textContent = ticket.cliente_email;
    
    // Preseleccionar prioridad y estado si ya existían
    if (ticket.prioridad) {
      document.querySelector(`input[name="prioridad"][value="${ticket.prioridad}"]`).checked = true;
    }
    if (ticket.estado) {
      document.querySelector(`input[name="estado"][value="${ticket.estado}"]`).checked = true;
    }
    
    // Guardar ticketId en el botón de guardar
    document.getElementById('btnGuardarGestion').dataset.id = ticketId;
    
    // Abrir modal
    const modal = new bootstrap.Modal(document.getElementById('modalGestionTicket'));
    modal.show();
  });
});
```

**13.3 Guardar cambios desde modal**
```js
document.getElementById('btnGuardarGestion').addEventListener('click', async function() {
  const ticketId = this.dataset.id;
  const prioridad = document.querySelector('input[name="prioridad"]:checked');
  const estado = document.querySelector('input[name="estado"]:checked');
  
  // Validar que ambos estén seleccionados
  if (!prioridad || !estado) {
    Swal.fire({
      icon: 'error',
      title: 'Campos incompletos',
      text: 'Debes seleccionar prioridad y estado antes de guardar'
    });
    return;
  }
  
  const agenteAsignado = document.getElementById('selectAgente').value;
  
  // Enviar al backend
  const response = await fetch(`/ticket/${ticketId}/gestionar`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      prioridad: prioridad.value,
      estado: estado.value,
      agente_asignado: agenteAsignado
    })
  });
  
  if (response.ok) {
    Swal.fire({
      icon: 'success',
      title: 'Ticket actualizado',
      text: 'Prioridad y estado asignados correctamente',
      timer: 2000,
      showConfirmButton: false
    });
    
    // Cerrar modal
    bootstrap.Modal.getInstance(document.getElementById('modalGestionTicket')).hide();
    
    // Recargar la card/fila para mostrar badges y botones de acción
    location.reload(); // o actualizar solo esa card vía fetch
  } else {
    Swal.fire('Error', 'No se pudo actualizar el ticket', 'error');
  }
});
```

### Paso 14: Botones de acción con SweetAlert

**14.1 Responder ticket (SweetAlert con textarea)**
```js
document.querySelectorAll('.btn-responder').forEach(btn => {
  btn.addEventListener('click', async function() {
    const ticketId = this.dataset.id;
    
    const { value: mensaje } = await Swal.fire({
      title: 'Responder ticket',
      input: 'textarea',
      inputPlaceholder: 'Escribe tu respuesta aquí...',
      inputAttributes: {
        'aria-label': 'Escribe tu respuesta'
      },
      showCancelButton: true,
      confirmButtonText: 'Enviar',
      cancelButtonText: 'Cancelar'
    });
    
    if (mensaje && mensaje.trim()) {
      const response = await fetch(`/ticket/${ticketId}/responder`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ mensaje: mensaje })
      });
      
      if (response.ok) {
        Swal.fire('Enviado', 'Respuesta agregada al ticket', 'success');
      } else {
        Swal.fire('Error', 'No se pudo enviar la respuesta', 'error');
      }
    }
  });
});
```

**14.2 Cambiar estado (SweetAlert con selector)**
```js
document.querySelectorAll('.btn-cambiar-estado').forEach(btn => {
  btn.addEventListener('click', async function() {
    const ticketId = this.dataset.id;
    
    const { value: nuevoEstado } = await Swal.fire({
      title: 'Cambiar estado',
      text: 'Selecciona el nuevo estado',
      input: 'select',
      inputOptions: {
        'abierto': 'Abierto',
        'en_progreso': 'En progreso',
        'resuelto': 'Resuelto',
        'cerrado': 'Cerrado'
      },
      showCancelButton: true,
      confirmButtonText: 'Cambiar'
    });
    
    if (nuevoEstado) {
      const response = await fetch(`/ticket/${ticketId}/cambiar_estado`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ estado: nuevoEstado })
      });
      
      if (response.ok) {
        Swal.fire('Actualizado', 'El estado ha cambiado', 'success');
        location.reload();
      } else {
        Swal.fire('Error', 'No se pudo cambiar el estado', 'error');
      }
    }
  });
});
```

**14.3 Historial (SweetAlert con tabla HTML)**
```js
document.querySelectorAll('.btn-historial').forEach(btn => {
  btn.addEventListener('click', async function() {
    const ticketId = this.dataset.id;
    const response = await fetch(`/api/ticket/${ticketId}/historial`);
    const historial = await response.json();
    
    let html = '<table class="table table-sm"><tr><th>Fecha</th><th>De</th><th>A</th><th>Usuario</th></tr>';
    historial.forEach(log => {
      html += `<tr>
        <td>${log.fecha_cambio}</td>
        <td>${log.estado_anterior || '-'}</td>
        <td>${log.estado_nuevo}</td>
        <td>${log.cambiado_por_nombre}</td>
      </tr>`;
    });
    html += '</table>';
    
    Swal.fire({
      title: 'Historial de cambios',
      html: html,
      width: '600px'
    });
  });
});
```

### Paso 15: Dashboard del cliente (más simple)

**15.1 Vista `dashboard_cliente.html`**

- Tabla con sus tickets (similar a la de agente, pero sin botones de gestión complejos)
    
- Botón "Nuevo Ticket" que abre un modal (sin prioridad, solo título + descripción)
    
- Cada ticket tiene botón "Ver detalle" y "Cancelar" (si cumple regla 30 min)
    
- SweetAlert para confirmar cancelación
    

**15.2 Cancelar ticket (con SweetAlert y validación de tiempo)**
```js
Swal.fire({
  title: '¿Cancelar ticket?',
  text: 'Solo puedes cancelar tickets abiertos creados hace menos de 30 minutos',
  icon: 'warning',
  showCancelButton: true,
  confirmButtonColor: '#d33',
  confirmButtonText: 'Sí, cancelar'
}).then((result) => {
  if (result.isConfirmed) {
    fetch(`/ticket/${ticketId}/cancelar`, { method: 'POST' })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          Swal.fire('Cancelado', 'Ticket cancelado correctamente', 'success');
          location.reload();
        } else {
          Swal.fire('Error', data.mensaje || 'No se puede cancelar', 'error');
        }
      });
  }
});
```

### Paso 16: Responsive y estilos finales

- Usar `.table-responsive` en tablas
    
- En móvil, las cards de tickets se apilan verticalmente
    
- SweetAlert ya es responsive por defecto
    
- Usar Font Awesome para iconos en todos los botones