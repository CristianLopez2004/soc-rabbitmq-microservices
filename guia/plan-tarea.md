#  Deber RabbitMQ

**Materia:** ISWZ2202 - Diseño y Arquitectura de Software  
**Caso:** Gestor de Alertas de Seguridad SOC  
**Repositorio:** soc-rabbitmq-microservices

---

## pasos

 Crear repositorio público y estructura base.
 Levantar RabbitMQ con Docker.
 Crear exchanges, colas y bindings.
 Implementar productor de alertas.
Implementar dos consumidores.
Ejecutar pruebas del flujo completo.
 Tomar capturas de RabbitMQ Management.
- Completar documento final con evidencias.
 Preparar demo en clase.

---

## Arquitectura Objetivo

- **Productor:** envía alertas de seguridad con categoría, severidad, origen, IP y mensaje.
- **Alert Service:** consume eventos críticos e importantes, almacena alertas y expone una API REST.
- **Audit Service:** consume eventos generales para auditoría y almacenamiento propio.
- **RabbitMQ:** broker central con exchanges `topic`, `direct` y `fanout`.

---

## Estructura del repositorio

```text
soc-rabbitmq-microservices/
│
├── rabbit-services/
│   ├── alert-service/
│   │   ├── alert_service.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── audit-service/
│   │   ├── audit_service.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   └── producer/
│       ├── producer.py
│       ├── Dockerfile
│       └── requirements.txt
│
├── guia/
│   └── plan-tarea.md
│
├── docker-compose.yml
└── README.md
```

---

## Exchanges

| Exchange | Tipo | Uso |
|---|---|---|
| `soc.direct.exchange` | `direct` | Enrutamiento exacto por severidad, por ejemplo `critical` y `high`. |
| `soc.fanout.exchange` | `fanout` | Difusión general de eventos a las colas enlazadas. |
| `soc.topic.exchange` | `topic` | Enrutamiento por patrones, por ejemplo `seguridad.*.critical` y `seguridad.auth.*`. |

---

## Colas

| Cola | Consumidor | Descripción |
|---|---|---|
| `q.alertas.direct` | Alert Service | Recibe alertas por clave exacta desde el exchange Direct. |
| `q.alertas.topic` | Alert Service | Recibe alertas mediante patrones desde el exchange Topic. |
| `q.auditoria.fanout` | Audit Service | Recibe eventos generales desde el exchange Fanout. |

---

## Bindings

| Exchange | Cola | Routing Key / Patrón |
|---|---|---|
| `soc.direct.exchange` | `q.alertas.direct` | `critical` |
| `soc.direct.exchange` | `q.alertas.direct` | `high` |
| `soc.topic.exchange` | `q.alertas.topic` | `seguridad.*.critical` |
| `soc.topic.exchange` | `q.alertas.topic` | `seguridad.auth.*` |
| `soc.fanout.exchange` | `q.auditoria.fanout` | No aplica |

---

## Flujo de ejecución

1. Se levanta RabbitMQ mediante Docker Compose.
2. El productor genera eventos de seguridad simulados.
3. Los eventos se publican en los exchanges configurados.
4. RabbitMQ enruta los mensajes hacia las colas correspondientes.
5. `Alert Service` consume alertas críticas o importantes.
6. `Audit Service` consume eventos generales para auditoría.
7. `Alert Service` expone una API para consultar las alertas procesadas.

---

## Comandos principales

### Ejecutar el proyecto

```bash
docker compose up --build
```

### Acceder a RabbitMQ Management

```text
http://localhost:15672
```

Credenciales:

```text
Usuario: guest
Contraseña: guest
```

### Probar API del Alert Service

```text
http://localhost:8001/health
http://localhost:8001/alerts
```

### Detener el proyecto

```bash
docker compose down
```

---

## Evidencias necesarias en el documento

- Captura de Docker Compose ejecutándose.
- Captura del panel principal de RabbitMQ.
- Captura de exchanges.
- Captura de colas.
- Captura de bindings.
- Captura del endpoint `/health`.
- Captura del endpoint `/alerts`.
- Captura del repositorio en GitHub.

---

## Cumplimiento de requisitos

| Requisito | Cumplimiento |
|---|---|
| Productor de mensajes | Implementado con el servicio `producer`. |
| Dos consumidores | Implementados con `alert-service` y `audit-service`. |
| Topic | Implementado con `soc.topic.exchange`. |
| Fanout | Implementado con `soc.fanout.exchange`. |
| Direct | Implementado con `soc.direct.exchange`. |
| Caso real | Gestor de Alertas de Seguridad SOC. |
| Repositorio público GitHub | Proyecto publicado en GitHub. |
| Comunicación asíncrona | Garantizada mediante RabbitMQ. |
| Despliegue independiente | Cada servicio tiene Dockerfile propio. |
| Almacenamiento propio | Servicios consumidores usan almacenamiento individual. |
| API expuesta | `alert-service` expone endpoints REST. |

---

## Conclusión del plan

El proyecto permite demostrar el uso de RabbitMQ como broker de mensajería dentro de una arquitectura distribuida. La implementación cumple con los patrones Direct, Fanout y Topic, además de aplicar principios de microservicios como despliegue independiente, comunicación asíncrona, almacenamiento propio y exposición de API REST.
