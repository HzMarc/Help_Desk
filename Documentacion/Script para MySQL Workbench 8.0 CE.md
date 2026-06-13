```sql
-- ==============================================
-- SISTEMA DE TICKETS (HELPDESK)
-- Base de datos: ticket_system
-- ==============================================

CREATE DATABASE IF NOT EXISTS ticket_system;
USE ticket_system;

-- ==============================================
-- TABLA: usuarios
-- ==============================================
CREATE TABLE usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    rol ENUM('cliente', 'agente', 'admin') NOT NULL DEFAULT 'cliente',
    fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- TABLA: tickets
-- ==============================================
CREATE TABLE tickets (
    id INT PRIMARY KEY AUTO_INCREMENT,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT NOT NULL,
    prioridad ENUM('baja', 'media', 'alta', 'urgente') DEFAULT NULL,
    estado ENUM('abierto', 'en_progreso', 'resuelto', 'cerrado', 'cancelado') DEFAULT 'abierto',
    usuario_id INT NOT NULL,
    agente_asignado_id INT DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    cancelado_por_cliente BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (agente_asignado_id) REFERENCES usuarios(id) ON DELETE SET NULL
);

-- ==============================================
-- TABLA: respuestas
-- ==============================================
CREATE TABLE respuestas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT NOT NULL,
    usuario_id INT NOT NULL,
    mensaje TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- ==============================================
-- TABLA: logs_estados (historial de cambios)
-- ==============================================
CREATE TABLE logs_estados (
    id INT PRIMARY KEY AUTO_INCREMENT,
    ticket_id INT NOT NULL,
    estado_anterior ENUM('abierto', 'en_progreso', 'resuelto', 'cerrado', 'cancelado'),
    estado_nuevo ENUM('abierto', 'en_progreso', 'resuelto', 'cerrado', 'cancelado') NOT NULL,
    cambiado_por INT NOT NULL,
    fecha_cambio DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
    FOREIGN KEY (cambiado_por) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- ==============================================
-- TABLA: reportes_enviados
-- ==============================================
CREATE TABLE reportes_enviados (
    id INT PRIMARY KEY AUTO_INCREMENT,
    enviado_a_email VARCHAR(100) NOT NULL,
    filtros_usados JSON NOT NULL,
    fecha_envio DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================
-- ÍNDICES para mejorar rendimiento
-- ==============================================
CREATE INDEX idx_tickets_estado ON tickets(estado);
CREATE INDEX idx_tickets_usuario_id ON tickets(usuario_id);
CREATE INDEX idx_tickets_agente_asignado_id ON tickets(agente_asignado_id);
CREATE INDEX idx_respuestas_ticket_id ON respuestas(ticket_id);
CREATE INDEX idx_logs_estados_ticket_id ON logs_estados(ticket_id);
CREATE INDEX idx_usuarios_email ON usuarios(email);

-- ==============================================
-- DATOS DE PRUEBA (opcional)
-- ==============================================
-- Usuario admin por defecto (contraseña: admin123)
INSERT INTO usuarios (nombre, email, password_hash, rol) VALUES 
('Admin Principal', 'admin@ticketsystem.com', '$2b$12$6QvE7Z9QvE7Z9QvE7Z9Qve', 'admin');

-- Usuario agente por defecto
INSERT INTO usuarios (nombre, email, password_hash, rol) VALUES 
('Agente Soporte', 'agente@ticketsystem.com', '$2b$12$6QvE7Z9QvE7Z9QvE7Z9Qve', 'agente');

-- Usuario cliente por defecto
INSERT INTO usuarios (nombre, email, password_hash, rol) VALUES 
('Cliente Ejemplo', 'cliente@ticketsystem.com', '$2b$12$6QvE7Z9QvE7Z9QvE7Z9Qve', 'cliente');

-- Nota: Los password_hash son placeholders. Deberás generar hashes reales con bcrypt en tu aplicación Flask.
```