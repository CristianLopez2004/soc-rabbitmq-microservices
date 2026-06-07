# Taller RabbitMQ - Gestor de Alertas de Seguridad SOC

## Integrante
Cristianlopez
## Objetivo
Implementar un productor y dos consumidores de mensajes usando RabbitMQ, demostrando los patrones de exchange Direct, Fanout y Topic. Luego mejorar la solución como microservicios con despliegue independiente, comunicación asíncrona, almacenamiento propio y API.

## Caso real elegido
Gestor de Alertas de Seguridad SOC. Un productor simula eventos de seguridad de fuentes como firewall, EDR, IDS y autenticación. Los consumidores procesan alertas críticas y auditoría general.
## Estructura del repositorio
soc-rabbitmq-microservices/
│
├── alert-service/
│   ├── alert_service.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── audit-service/
│   ├── audit_service.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── docs/
│   └── plan-tarea.md
│
├── producer/
│   ├── producer.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml
└── README.md
## Arquitectura
- RabbitMQ
- Producer: publica eventos SOC.
- Alert Service: consume alertas high/critical y eventos de autenticación. Tiene almacenamiento propio SQLite y expone API REST.
- Audit Service: consume todos los eventos por Fanout y los guarda en su propio SQLite.

## Exchanges, colas y bindings

| Exchange | Tipo | Routing key / Binding | Cola | Uso |
|---|---|---|---|---|
| soc.direct.exchange | Direct | critical, high | q.alertas.direct | Alertas de severidad alta/crítica |
| soc.fanout.exchange | Fanout | No aplica | q.auditoria.fanout | Copia todos los eventos para auditoría |
| soc.topic.exchange | Topic | seguridad.*.critical, seguridad.auth.* | q.alertas.topic | Reglas flexibles por fuente/severidad |

## Requisitos
- Docker Desktop
- Git
- Navegador web

## Ejecución
```bash
git clone URL_DEL_REPOSITORIO
cd soc-rabbitmq-microservices
docker compose up --build
```

## Vista RabbitMQ Management
Abrir en el navegador:

```text
http://localhost:15672
```

Usuario: `guest`  
Contraseña: `guest`

## Prueba API del microservicio Alert Service
Abrir:

```text
http://localhost:8001/health
http://localhost:8001/alerts
```


## Conclusión
El proyecto aplica mensajería asíncrona con RabbitMQ. Direct permite enrutar por severidad exacta, Fanout permite difundir todos los eventos a auditoría, y Topic permite crear reglas flexibles mediante patrones. La segunda versión se implementa como microservicios con despliegue independiente, almacenamiento propio y exposición de API REST.
