// app/static/js/main.js

let currentTicketId = null;

async function abrirModalTicket(id) {
    currentTicketId = id;
    const modal = new bootstrap.Modal(document.getElementById('modalTicket'));
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

        // Renderizar Header
        document.getElementById('modalTicketLabel').innerHTML = `<strong>#${t.id}</strong> - ${t.titulo}`;

        // Renderizar Body (Info + Mensajes)
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
        
        // Área para enviar nueva respuesta si no está cancelado
        if (t.estado !== 'cancelado') {
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
            html += `</div><div class="alert alert-danger text-center">Ticket cancelado. No admite respuestas.</div>`;
        }

        document.getElementById('modalTicketBody').innerHTML = html;

        // Renderizar Footer (Controles extra)
        let footerHtml = ``;
        if (data.puede_cancelar && typeof ROL_USUARIO !== 'undefined' && ROL_USUARIO === 'cliente') {
            footerHtml += `<button class="btn btn-outline-danger" onclick="cancelarTicketModal(${t.id})"><i class="fas fa-ban"></i> Cancelar Ticket</button>`;
        } else {
            footerHtml += `<div></div>`; // Spacer
        }

        if (typeof ROL_USUARIO !== 'undefined' && ['admin', 'agente'].includes(ROL_USUARIO)) {
            footerHtml += `
                <div>
                    <button class="btn btn-outline-info" onclick="cambiarEstadoModal(${t.id})"><i class="fas fa-exchange-alt"></i> Estado</button>
                    <button class="btn btn-outline-deep-blue ms-2" onclick="verHistorialModal(${t.id})"><i class="fas fa-history"></i> Historial</button>
                </div>
            `;
        }
        document.getElementById('modalTicketFooter').innerHTML = footerHtml;

        // Event listener para el formulario de responder (dentro del modal dinámico)
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
                    // Recargar contenido del modal simulando tiempo real
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
      confirmButtonText: 'Sí, cancelar',
      cancelButtonText: 'No'
    }).then(async (result) => {
      if (result.isConfirmed) {
        // Hacemos form manual post a /ticket/id/cancelar
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/ticket/${id}/cancelar`;
        document.body.appendChild(form);
        form.submit();
      }
    });
}

async function cambiarEstadoModal(id) {
    const { value: nuevoEstado } = await Swal.fire({
      title: 'Cambiar estado',
      input: 'select',
      inputOptions: {
        'abierto': 'Abierto',
        'en_progreso': 'En progreso',
        'resuelto': 'Resuelto',
        'cerrado': 'Cerrado'
      },
      inputPlaceholder: 'Selecciona un estado',
      showCancelButton: true,
      confirmButtonText: 'Actualizar',
      confirmButtonColor: '#00B5C9'
    });
    
    if (nuevoEstado) {
        const response = await fetch(`/api/ticket/${id}/cambiar_estado`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ nuevo_estado: nuevoEstado })
        });
        const data = await response.json();
        
        if (data.success) {
            Swal.fire('¡Actualizado!', 'El estado ha cambiado.', 'success').then(()=> {
                // Actualizamos Modal si sigue abierto, sino reload
                if (currentTicketId === id) {
                    abrirModalTicket(id);
                } else {
                    location.reload();
                }
            });
        } else {
            Swal.fire('Error', 'Hubo un problema.', 'error');
        }
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
