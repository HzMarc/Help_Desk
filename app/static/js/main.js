let currentTicketId = null;

async function abrirModalTicket(id) {
    currentTicketId = id;
    const modalEl = document.getElementById('modalTicket');
    let modal = bootstrap.Modal.getInstance(modalEl);
    if (!modal) {
        modal = new bootstrap.Modal(modalEl);
    }
    modal.show();

    // Resetear modal mientras carga
    document.getElementById('modalTicketLabel').innerHTML = `Cargando Ticket #${id}...`;
    document.getElementById('modalTicketBody').innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border text-cyan" role="status"><span class="visually-hidden">Cargando...</span></div>
        </div>`;
    document.getElementById('modalTicketFooter').innerHTML = '';

    try {
        const res = await fetch(`/api/ticket/${id}/completo`);
        const data = await res.json();
        
        if (!res.ok) {
            document.getElementById('modalTicketBody').innerHTML = `<div class="alert alert-danger">${data.error || 'Error cargando ticket'}</div>`;
            return;
        }

        const t = data.ticket;
        const r = data.respuestas;

        document.getElementById('modalTicketLabel').innerHTML = `<strong>#${t.id}</strong> - ${t.titulo}`;

        let html = `
            <div class="bg-white p-3 rounded shadow-sm mb-4 border-top border-4 border-cyan">
                <div class="d-flex justify-content-between mb-2">
                    <span class="badge bg-${t.estado === 'abierto' ? 'primary' : t.estado === 'resuelto' ? 'success' : t.estado === 'cerrado' ? 'secondary' : t.estado === 'en_progreso' ? 'warning text-dark' : 'danger'} fs-6">${t.estado.toUpperCase()}</span>
                    <span class="text-muted small"><i class="far fa-calendar-alt"></i> Creado: ${t.created_at}</span>
                </div>
                <p style="white-space: pre-wrap;" class="mb-0 text-dark">${t.descripcion}</p>
            </div>
            <h6 class="text-deep-blue mb-3 border-bottom pb-2"><i class="far fa-comments"></i> Hilo de Conversación</h6>
            <div class="respuestas-container mb-4">
        `;

        if (r.length === 0) {
            html += `<p class="text-muted fst-italic text-center">No hay respuestas aún.</p>`;
        } else {
            r.forEach(msg => {
                const esCliente = msg.rol === 'cliente';
                html += `
                    <div class="msg-bubble ${esCliente ? 'msg-cliente' : 'msg-agente'}">
                        <div class="d-flex justify-content-between mb-1">
                            <strong>${msg.nombre} <span class="badge ${esCliente ? 'bg-secondary' : 'bg-info text-dark'} ml-2">${msg.rol}</span></strong>
                            <small class="text-muted">${msg.created_at}</small>
                        </div>
                        <p class="mb-0" style="white-space: pre-wrap;">${msg.mensaje}</p>
                    </div>
                `;
            });
        }
        
        if (t.estado !== 'cancelado' && t.estado !== 'resuelto' && t.estado !== 'cerrado') {
            html += `
                </div>
                <div class="bg-white p-3 rounded shadow-sm">
                    <form id="form-responder">
                        <textarea id="txt-mensaje" class="form-control mb-2" rows="3" required placeholder="Escribe tu respuesta..."></textarea>
                        <div class="text-end">
                            <button type="submit" class="btn btn-cyan fw-bold"><i class="fas fa-paper-plane"></i> Enviar</button>
                        </div>
                    </form>
                </div>
            `;
        } else {
            let razon = t.estado === 'cancelado' ? 'cancelado' : 'resuelto/cerrado';
            html += `</div><div class="alert alert-danger text-center">Ticket ${razon}. No admite nuevas respuestas.</div>`;
        }

        document.getElementById('modalTicketBody').innerHTML = html;

        let footerHtml = ``;
        if (data.puede_cancelar && typeof ROL_USUARIO !== 'undefined' && ROL_USUARIO === 'cliente') {
            footerHtml += `<button class="btn btn-outline-danger" onclick="cancelarTicketModal(${t.id})"><i class="fas fa-ban"></i> Cancelar Ticket</button>`;
        } else {
            footerHtml += `<div></div>`;
        }
        
        document.getElementById('modalTicketFooter').innerHTML = footerHtml;

        const formResponder = document.getElementById('form-responder');
        if (formResponder) {
            formResponder.addEventListener('submit', async (e) => {
                e.preventDefault();
                const msj = document.getElementById('txt-mensaje').value;
                const btnSubmit = formResponder.querySelector('button');
                btnSubmit.disabled = true;
                btnSubmit.innerHTML = 'Enviando...';

                const resPost = await fetch(`/ticket/${id}/responder`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mensaje: msj })
                });

                if (resPost.ok) {
                    abrirModalTicket(id);
                } else {
                    Swal.fire('Error', 'No se pudo enviar la respuesta', 'error');
                    btnSubmit.disabled = false;
                    btnSubmit.innerHTML = '<i class="fas fa-paper-plane"></i> Enviar';
                }
            });
        }

    } catch (e) {
        document.getElementById('modalTicketBody').innerHTML = `<div class="alert alert-danger">Error conectando con el servidor.</div>`;
    }
}

// ================= LÓGICA DE AGENTES Y ADMINS =================

function cancelarTicketModal(id) {
    Swal.fire({
      title: '¿Cancelar ticket?',
      text: 'Esta acción no se puede deshacer.',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#6c757d',
      confirmButtonText: 'Sí, cancelar'
    }).then((result) => {
      if (result.isConfirmed) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/ticket/${id}/cancelar`;
        document.body.appendChild(form);
        form.submit();
      }
    });
}

// Nuevo: Modal Inicial Exacto de Fase 2 (Paso 8.2)
async function gestionarTicketInicialModal(id) {
    // Necesitamos cargar agentes y datos actuales para mostrarlos
    const res = await fetch(`/api/ticket/${id}/completo`);
    const data = await res.json();
    const t = data.ticket;
    const agentes = data.agentes || [];

    let opcionesAgentes = '<option value="">Yo mismo / Seleccionar</option>';
    agentes.forEach(ag => {
        opcionesAgentes += `<option value="${ag.id}">${ag.nombre}</option>`;
    });

    const htmlForm = `
        <div class="text-start">
            <h6 class="fw-bold mb-3 border-bottom pb-2">📌 ASIGNAR PRIORIDAD (obligatorio)</h6>
            <div class="mb-4 d-flex justify-content-between" id="grupo-prioridad">
                <label><input type="radio" name="swal-prioridad" value="baja"> Baja</label>
                <label><input type="radio" name="swal-prioridad" value="media"> Media</label>
                <label><input type="radio" name="swal-prioridad" value="alta"> Alta</label>
                <label><input type="radio" name="swal-prioridad" value="urgente"> Urgente</label>
            </div>
            
            <h6 class="fw-bold mb-3 border-bottom pb-2">🔄 CAMBIAR ESTADO (obligatorio)</h6>
            <div class="mb-4 d-flex justify-content-between" id="grupo-estado">
                <label><input type="radio" name="swal-estado" value="abierto"> Abierto</label>
                <label><input type="radio" name="swal-estado" value="en_progreso"> En progreso</label>
                <label><input type="radio" name="swal-estado" value="resuelto"> Resuelto</label>
                <label><input type="radio" name="swal-estado" value="cerrado"> Cerrado</label>
            </div>

            <h6 class="fw-bold mb-2">👤 ASIGNAR A (opcional)</h6>
            <select id="swal-agente" class="form-select">
                ${opcionesAgentes}
            </select>
        </div>
    `;

    const result = await Swal.fire({
      title: 'Gestionar Ticket',
      html: htmlForm,
      width: '600px',
      showCancelButton: true,
      confirmButtonText: 'Guardar Cambios',
      confirmButtonColor: '#00B5C9',
      didOpen: () => {
          if(t.prioridad) document.querySelector(`input[name="swal-prioridad"][value="${t.prioridad}"]`).checked = true;
          if(t.estado) document.querySelector(`input[name="swal-estado"][value="${t.estado}"]`).checked = true;
      },
      preConfirm: () => {
        const prioEl = document.querySelector('input[name="swal-prioridad"]:checked');
        const estEl = document.querySelector('input[name="swal-estado"]:checked');
        if (!prioEl || !estEl) {
            Swal.showValidationMessage('Debes seleccionar prioridad y estado');
            return false;
        }
        return { 
            prioridad: prioEl.value, 
            estado: estEl.value, 
            agente_id: document.getElementById('swal-agente').value || null 
        };
      }
    });
    
    if (result.isConfirmed) {
        const response = await fetch(`/api/ticket/${id}/gestionar`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(result.value)
        });
        const dataResp = await response.json();
        
        if (dataResp.success) {
            Swal.fire({icon: 'success', title: 'Ticket actualizado', text: 'Prioridad y estado asignados correctamente', timer: 2000, showConfirmButton: false}).then(() => location.reload());
        }
    }
}

// Botones de acción individuales (Paso 8.4)
async function cambiarEstadoModal(id) {
    const htmlForm = `
        <div class="text-start">
            <div class="d-flex justify-content-between mb-4">
                <label><input type="radio" name="swal-nuevo-estado" value="abierto"> Abierto</label>
                <label><input type="radio" name="swal-nuevo-estado" value="en_progreso"> En progreso</label>
                <label><input type="radio" name="swal-nuevo-estado" value="resuelto"> Resuelto</label>
                <label><input type="radio" name="swal-nuevo-estado" value="cerrado"> Cerrado</label>
            </div>
        </div>
    `;

    const { value: result } = await Swal.fire({
      title: 'Cambiar estado',
      html: htmlForm,
      showCancelButton: true,
      confirmButtonText: 'Cambiar',
      confirmButtonColor: '#00B5C9',
      preConfirm: () => {
          const el = document.querySelector('input[name="swal-nuevo-estado"]:checked');
          if(!el) { Swal.showValidationMessage('Selecciona un estado'); return false; }
          return el.value;
      }
    });
    
    if (result) {
        const response = await fetch(`/api/ticket/${id}/cambiar_estado`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ nuevo_estado: result })
        });
        const data = await response.json();
        if (data.success) {
            Swal.fire('¡Actualizado!', 'El estado ha cambiado.', 'success').then(()=> location.reload());
        }
    }
}

async function reasignarModal(id) {
    const res = await fetch(`/api/ticket/${id}/completo`);
    const data = await res.json();
    const agentes = data.agentes || [];
    
    let opcionesAgentes = '<option value="">Sin Asignar</option>';
    agentes.forEach(ag => {
        opcionesAgentes += `<option value="${ag.id}">${ag.nombre}</option>`;
    });

    const { value: agenteId } = await Swal.fire({
      title: 'Reasignar Agente',
      html: `<select id="swal-reasignar" class="form-select">${opcionesAgentes}</select>`,
      showCancelButton: true,
      confirmButtonText: 'Reasignar',
      preConfirm: () => document.getElementById('swal-reasignar').value
    });

    if (agenteId !== undefined) {
        // Aprovechamos el endpoint /gestionar, pero mantenemos prioridad y estado actual
        const t = data.ticket;
        const response = await fetch(`/api/ticket/${id}/gestionar`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ prioridad: t.prioridad, estado: t.estado, agente_id: agenteId || null })
        });
        const resp = await response.json();
        if(resp.success) Swal.fire('Reasignado', 'Agente modificado correctamente', 'success').then(() => location.reload());
    }
}

async function verHistorialModal(id) {
    const response = await fetch(`/api/ticket/${id}/historial`);
    const historial = await response.json();
    
    let html = '<div class="table-responsive"><table class="table table-sm text-start"><thead><tr><th>Fecha</th><th>De</th><th>A</th><th>Usuario</th></tr></thead><tbody>';
    if (historial.length === 0) {
        html += '<tr><td colspan="4" class="text-center">Sin cambios registrados</td></tr>';
    } else {
        historial.forEach(log => {
          html += `<tr>
            <td><small>${new Date(log.fecha_cambio).toLocaleString()}</small></td>
            <td><span class="badge bg-secondary">${log.estado_anterior || '-'}</span></td>
            <td><span class="badge bg-info">${log.estado_nuevo}</span></td>
            <td>${log.nombre_usuario}</td>
          </tr>`;
        });
    }
    html += '</tbody></table></div>';
    
    Swal.fire({
      title: `Historial Ticket #${id}`,
      html: html,
      width: '600px',
      confirmButtonColor: '#1C3166'
    });
}

// ================= FASE 4: ELIMINAR SOFT (PAPELERA) =================
async function eliminarSoftModal(id) {
    const result = await Swal.fire({
        title: '¿Enviar a la Papelera?',
        text: 'Este ticket será ocultado y solo podrá ser visto en la papelera por los administradores.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    });

    if (result.isConfirmed) {
        try {
            const res = await fetch(`/admin/ticket/${id}/eliminar_soft`, { method: 'POST' });
            if (res.ok) {
                Swal.fire('Eliminado', 'El ticket ha sido enviado a la papelera', 'success')
                .then(() => location.reload());
            } else {
                Swal.fire('Error', 'No se pudo eliminar el ticket', 'error');
            }
        } catch (e) {
            Swal.fire('Error', 'Problema de conexión con el servidor', 'error');
        }
    }
}

// ================= LÓGICA DE BÚSQUEDA (FASE 4) =================
const buscador = document.getElementById('buscador');
if (buscador) {
    buscador.addEventListener('input', debounce(async function(e) {
        const termino = e.target.value;
        const contTickets = document.getElementById('contenedor-tickets');
        const contBusqueda = document.getElementById('resultados-busqueda');
        
        if (termino.length < 2) {
            contTickets.classList.remove('d-none');
            contBusqueda.classList.add('d-none');
            return;
        }
        
        contTickets.classList.add('d-none');
        contBusqueda.classList.remove('d-none');
        contBusqueda.innerHTML = `<div class="col-12 text-center py-5"><div class="spinner-border text-cyan" role="status"></div></div>`;
        
        try {
            const response = await fetch(`/api/buscar_tickets?q=${encodeURIComponent(termino)}`);
            const tickets = await response.json();
            
            let html = '<div class="col-12"><h5 class="text-deep-blue mb-3 border-bottom pb-2">Resultados de la búsqueda</h5></div>';
            if (tickets.length === 0) {
                html += '<div class="col-12 text-center py-4 text-muted">No se encontraron tickets</div>';
            } else {
                tickets.forEach(ticket => {
                    const bg = ticket.estado === 'abierto' ? 'primary' : ticket.estado === 'resuelto' ? 'success' : ticket.estado === 'cerrado' ? 'secondary' : 'warning text-dark';
                    html += `
                        <div class="col-md-6 mb-3">
                            <div class="card shadow-sm border-0 border-start border-cyan border-4">
                                <div class="card-body">
                                    <h6 class="fw-bold text-deep-blue">#${ticket.id} - ${ticket.titulo}</h6>
                                    <p class="mb-2 small text-muted">
                                        <i class="fas fa-user"></i> ${ticket.cliente_email} <br>
                                        <span class="badge bg-${bg} mt-1">${ticket.estado.toUpperCase()}</span>
                                    </p>
                                    <button class="btn btn-sm btn-cyan" onclick="abrirModalTicket(${ticket.id})">Ver Detalles</button>
                                </div>
                            </div>
                        </div>
                    `;
                });
            }
            contBusqueda.innerHTML = html;
        } catch(err) {
            contBusqueda.innerHTML = '<div class="col-12 text-center py-4 text-danger">Error en la búsqueda</div>';
        }
    }, 400));
}

function debounce(func, wait) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// ================= FASE 4: EMAIL REPORTES =================
async function enviarReporteEmail() {
    const btn = document.getElementById('btn-enviar-reporte');
    if (!btn) return;

    const contenidoOriginal = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Enviando...';
    btn.disabled = true;

    try {
        const response = await fetch('/admin/enviar_reporte', { method: 'POST' });
        const data = await response.json();
        
        if (data.success) {
            Swal.fire('¡Enviado!', data.message, 'success');
        } else {
            Swal.fire('Error', data.message, 'error');
        }
    } catch (e) {
        Swal.fire('Error', 'No se pudo conectar con el servidor', 'error');
    } finally {
        btn.innerHTML = contenidoOriginal;
        btn.disabled = false;
    }
}
