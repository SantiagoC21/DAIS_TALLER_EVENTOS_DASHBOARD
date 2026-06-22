# Bluetooth Guardian Dashboard

API de monitoreo para Bluetooth Guardian — Dashboard Module. Sistema de monitoreo en tiempo real de dispositivos Bluetooth con alertas por email y panel de control web.

## 🚀 Características

- **Monitoreo de Dispositivos Bluetooth**: Registro y seguimiento de dispositivos Bluetooth con dirección MAC y nombre
- **Sistema de Alertas**: Detección de desconexiones y envío de alertas por email
- **Heartbeat en Tiempo Real**: Monitoreo del estado de conexión de dispositivos
- **Panel de Control Web**: Dashboard interactivo para visualizar el estado del sistema
- **Gestión de Sesiones de Alarma**: Registro histórico de alarmas y desconexiones
- **API RESTful**: Endpoints completos para integración con clientes externos
- **Base de Datos Relacional**: PostgreSQL con SQLAlchemy ORM
- **Configuración Flexible**: Variables de entorno para fácil despliegue

## 🛠️ Stack Tecnológico

- **Framework**: FastAPI 0.115.5
- **Servidor ASGI**: Uvicorn
- **Base de Datos**: PostgreSQL con SQLAlchemy 2.0.36
- **Validación**: Pydantic 2.10.3
- **Email**: aiosmtplib para notificaciones SMTP
- **Migraciones**: Alembic
- **Gestión de Configuración**: pydantic-settings

## 📋 Requisitos Previos

- Python 3.11 o superior
- PostgreSQL 12 o superior
- pip (gestor de paquetes de Python)

## 🔧 Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd dashboard
   ```

2. **Crear y activar entorno virtual**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   ```bash
   cp .env.example .env
   ```
   Editar el archivo `.env` con tus credenciales:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/dbname
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=tu_email@gmail.com
   SMTP_PASSWORD=tu_app_password
   EMAIL_FROM=tu_email@gmail.com
   EMAIL_TO=destinatario@ejemplo.com
   ```

5. **Configurar base de datos**
   ```bash
   # Crear la base de datos en PostgreSQL
   createdb bluetooth_guardian
   
   # Ejecutar migraciones (si usas Alembic)
   alembic upgrade head
   ```

## 🚀 Ejecución

### Modo Desarrollo
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Modo Producción
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Usando Procfile (Heroku/Render)
```bash
# Instalar dependencies
pip install honcho

# Ejecutar
honcho start
```

## 📚 Documentación de la API

Una vez iniciado el servidor, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## 🏗️ Estructura del Proyecto

```
dashboard/
├── main.py                 # Punto de entrada de la aplicación
├── config.py               # Configuración y settings
├── database.py             # Conexión a base de datos
├── requirements.txt        # Dependencias de Python
├── Procfile               # Configuración de despliegue
├── models/                # Modelos SQLAlchemy
│   ├── device.py          # Modelo de dispositivo Bluetooth
│   ├── event.py           # Modelo de eventos
│   ├── alarm_session.py   # Modelo de sesiones de alarma
│   ├── heartbeat.py       # Modelo de heartbeats
│   └── email_log.py       # Modelo de logs de email
├── schemas/               # Esquemas Pydantic
│   ├── device.py
│   ├── event.py
│   ├── alarm_session.py
│   ├── heartbeat.py
│   └── dashboard.py
├── routers/               # Routers de FastAPI
│   ├── devices.py         # Endpoints de dispositivos
│   ├── events.py          # Endpoints de eventos
│   ├── heartbeat.py       # Endpoints de heartbeat
│   └── dashboard.py       # Endpoints del dashboard
├── services/              # Lógica de negocio
├── static/                # Archivos estáticos
│   └── dashboard.html     # Panel de control web
└── .env                   # Variables de entorno (no versionado)
```

## 🔌 Endpoints Principales

### Health Check
- `GET /` - Estado de la API
- `GET /health` - Health check

### Dispositivos
- `GET /devices` - Listar todos los dispositivos
- `POST /devices` - Registrar nuevo dispositivo
- `GET /devices/{mac_address}` - Obtener dispositivo por MAC
- `PUT /devices/{mac_address}` - Actualizar dispositivo
- `DELETE /devices/{mac_address}` - Eliminar dispositivo

### Eventos
- `GET /events` - Listar eventos
- `POST /events` - Crear nuevo evento
- `GET /events/{id}` - Obtener evento por ID

### Heartbeat
- `POST /heartbeat` - Reportar heartbeat de dispositivo
- `GET /heartbeat` - Listar heartbeats recientes

### Dashboard
- `GET /dashboard/summary` - Resumen del sistema
- `GET /dashboard` - Panel web

## ⚙️ Configuración

### Variables de Entorno

| Variable | Descripción | Default |
|----------|-------------|---------|
| `DATABASE_URL` | URL de conexión a PostgreSQL | Requerido |
| `SMTP_HOST` | Servidor SMTP | `smtp.gmail.com` |
| `SMTP_PORT` | Puerto SMTP | `587` |
| `SMTP_USER` | Usuario SMTP | Requerido |
| `SMTP_PASSWORD` | Contraseña SMTP (App Password) | Requerido |
| `EMAIL_FROM` | Remitente de emails | Igual a SMTP_USER |
| `EMAIL_TO` | Destinatario de alertas | Requerido |
| `APP_TITLE` | Nombre de la aplicación | `Bluetooth Guardian API` |
| `APP_VERSION` | Versión de la aplicación | `1.0.0` |
| `DEBUG` | Modo debug | `False` |
| `HEARTBEAT_TIMEOUT_SECS` | Timeout para considerar offline | `120` |
| `MIN_SEVERITY_TO_NOTIFY` | Severidad mínima para notificar | `2` |

## 🧪 Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=.

# Con reporte detallado
pytest -v
```

## 🚀 Despliegue

### Heroku
```bash
heroku create bluetooth-guardian-dashboard
heroku addons:create heroku-postgresql:mini
git push heroku main
```

### Render
1. Crear nuevo servicio web en Render
2. Conectar repositorio
3. Configurar variables de entorno
4. Desplegar

### Docker
```bash
# Construir imagen
docker build -t bluetooth-guardian-dashboard .

# Ejecutar contenedor
docker run -p 8000:8000 --env-file .env bluetooth-guardian-dashboard
```

## 📝 Notas Importantes

- **Seguridad**: En producción, reemplazar `allow_origins=["*"]` en CORS con el dominio específico del dashboard
- **Email**: Para Gmail, usar una "App Password" en lugar de la contraseña normal
- **Base de Datos**: Asegurarse de que PostgreSQL esté configurado para aceptar conexiones desde el servidor
- **Heartbeat**: El timeout de 120 segundos significa que si un dispositivo no envía heartbeat en 2 minutos, se marca como offline

## 🤝 Contribución

1. Fork del repositorio
2. Crear rama para la feature (`git checkout -b feature/nueva-feature`)
3. Commit de cambios (`git commit -am 'Añadir nueva feature'`)
4. Push a la rama (`git push origin feature/nueva-feature`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto es parte del desarrollo adaptativo del ciclo 10MO. Consultar con el equipo de desarrollo para más información sobre licenciamiento.

## 👥 Autores

- Equipo de Desarrollo Adaptativo
- Ciclo 10MO

## 📞 Soporte

Para reportar issues o solicitar ayuda, abrir un issue en el repositorio o contactar al equipo de desarrollo.
