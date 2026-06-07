import json, os, random, time, uuid
from datetime import datetime, timezone
import pika

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")

EX_DIRECT = "soc.direct.exchange"
EX_FANOUT = "soc.fanout.exchange"
EX_TOPIC = "soc.topic.exchange"

systems = ["firewall", "edr", "ids", "auth"]
severities = ["low", "medium", "high", "critical"]
events = [
    "Intento de acceso no autorizado",
    "Malware detectado",
    "Escaneo de puertos",
    "Fallo repetido de login",
    "Tráfico sospechoso saliente",
]

def connect():
    params = pika.ConnectionParameters(host=RABBITMQ_HOST)
    return pika.BlockingConnection(params)

def declare(channel):
    # Direct: enruta por severidad exacta: critical, high, medium, low
    channel.exchange_declare(exchange=EX_DIRECT, exchange_type="direct", durable=True)
    # Fanout: difunde cada mensaje a todas las colas enlazadas, sin routing key
    channel.exchange_declare(exchange=EX_FANOUT, exchange_type="fanout", durable=True)
    # Topic: enruta por patron: seguridad.<sistema>.<severidad>
    channel.exchange_declare(exchange=EX_TOPIC, exchange_type="topic", durable=True)


def main():
    connection = connect()
    channel = connection.channel()
    declare(channel)

    print("Producer iniciado. Publicando eventos SOC cada 3 segundos...")
    while True:
        system = random.choice(systems)
        severity = random.choice(severities)
        event = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": system,
            "severity": severity,
            "description": random.choice(events),
            "ip": f"192.168.1.{random.randint(2, 254)}"
        }
        body = json.dumps(event).encode("utf-8")

        # Direct exchange: routing key = severidad exacta
        channel.basic_publish(exchange=EX_DIRECT, routing_key=severity, body=body,
                              properties=pika.BasicProperties(delivery_mode=2))
        # Fanout exchange: todos los auditores/loggers reciben copia
        channel.basic_publish(exchange=EX_FANOUT, routing_key="", body=body,
                              properties=pika.BasicProperties(delivery_mode=2))
        # Topic exchange: routing key jerarquica
        topic_key = f"seguridad.{system}.{severity}"
        channel.basic_publish(exchange=EX_TOPIC, routing_key=topic_key, body=body,
                              properties=pika.BasicProperties(delivery_mode=2))

        print(f"Publicado: direct={severity} topic={topic_key} evento={event['description']}")
        time.sleep(3)

if __name__ == "__main__":
    main()
