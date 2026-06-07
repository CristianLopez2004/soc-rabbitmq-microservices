import json, os, sqlite3, threading, time
from pathlib import Path
import pika
from fastapi import FastAPI
import uvicorn

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
DB_PATH = "/app/data/alerts.db"
EX_DIRECT = "soc.direct.exchange"
EX_TOPIC = "soc.topic.exchange"
QUEUE_DIRECT = "q.alertas.direct"
QUEUE_TOPIC = "q.alertas.topic"

app = FastAPI(title="Alert Service API", description="Microservicio que consume alertas SOC y expone API")

Path("/app/data").mkdir(exist_ok=True)

def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS alerts(
        id TEXT PRIMARY KEY,
        timestamp TEXT,
        source TEXT,
        severity TEXT,
        description TEXT,
        ip TEXT,
        exchange_type TEXT
    )
    """)
    conn.commit()
    return conn

conn_db = db()

def save_alert(event, exchange_type):
    with conn_db:
        conn_db.execute("""
        INSERT OR IGNORE INTO alerts(id, timestamp, source, severity, description, ip, exchange_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (event["id"], event["timestamp"], event["source"], event["severity"],
              event["description"], event["ip"], exchange_type))


def callback(exchange_type):
    def inner(ch, method, properties, body):
        event = json.loads(body.decode("utf-8"))
        save_alert(event, exchange_type)
        print(f"[AlertService] Consumido desde {exchange_type}: {event}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
    return inner


def consume():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()
            channel.exchange_declare(exchange=EX_DIRECT, exchange_type="direct", durable=True)
            channel.exchange_declare(exchange=EX_TOPIC, exchange_type="topic", durable=True)

            channel.queue_declare(queue=QUEUE_DIRECT, durable=True)
            channel.queue_bind(exchange=EX_DIRECT, queue=QUEUE_DIRECT, routing_key="critical")
            channel.queue_bind(exchange=EX_DIRECT, queue=QUEUE_DIRECT, routing_key="high")

            channel.queue_declare(queue=QUEUE_TOPIC, durable=True)
            channel.queue_bind(exchange=EX_TOPIC, queue=QUEUE_TOPIC, routing_key="seguridad.*.critical")
            channel.queue_bind(exchange=EX_TOPIC, queue=QUEUE_TOPIC, routing_key="seguridad.auth.*")

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=QUEUE_DIRECT, on_message_callback=callback("direct"))
            channel.basic_consume(queue=QUEUE_TOPIC, on_message_callback=callback("topic"))
            print("[AlertService] Esperando alertas high/critical y auth...")
            channel.start_consuming()
        except Exception as e:
            print(f"[AlertService] Error de conexion: {e}. Reintentando...")
            time.sleep(5)

@app.get("/health")
def health():
    return {"status": "ok", "service": "alert-service"}

@app.get("/alerts")
def list_alerts():
    rows = conn_db.execute("SELECT id, timestamp, source, severity, description, ip, exchange_type FROM alerts ORDER BY timestamp DESC LIMIT 50").fetchall()
    return [
        {"id": r[0], "timestamp": r[1], "source": r[2], "severity": r[3], "description": r[4], "ip": r[5], "exchange_type": r[6]}
        for r in rows
    ]

@app.get("/alerts/{alert_id}")
def get_alert(alert_id: str):
    row = conn_db.execute("SELECT id, timestamp, source, severity, description, ip, exchange_type FROM alerts WHERE id=?", (alert_id,)).fetchone()
    if row is None:
        return {"message": "Alerta no encontrada"}
    return {"id": row[0], "timestamp": row[1], "source": row[2], "severity": row[3], "description": row[4], "ip": row[5], "exchange_type": row[6]}

if __name__ == "__main__":
    threading.Thread(target=consume, daemon=True).start()
    uvicorn.run(app, host="0.0.0.0", port=8001)
