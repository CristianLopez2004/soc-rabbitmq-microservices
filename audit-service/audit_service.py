import json, os, sqlite3, time
from pathlib import Path
import pika

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
DB_PATH = "/app/data/audit.db"
EX_FANOUT = "soc.fanout.exchange"
QUEUE_AUDIT = "q.auditoria.fanout"

Path("/app/data").mkdir(exist_ok=True)

def db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS audit_events(
        id TEXT PRIMARY KEY,
        timestamp TEXT,
        source TEXT,
        severity TEXT,
        description TEXT,
        ip TEXT
    )
    """)
    conn.commit()
    return conn

conn_db = db()

def save_event(event):
    with conn_db:
        conn_db.execute("""
        INSERT OR IGNORE INTO audit_events(id, timestamp, source, severity, description, ip)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (event["id"], event["timestamp"], event["source"], event["severity"], event["description"], event["ip"]))

def on_message(ch, method, properties, body):
    event = json.loads(body.decode("utf-8"))
    save_event(event)
    print(f"[AuditService] Evento auditado desde fanout: {event}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
            channel = connection.channel()
            channel.exchange_declare(exchange=EX_FANOUT, exchange_type="fanout", durable=True)
            channel.queue_declare(queue=QUEUE_AUDIT, durable=True)
            channel.queue_bind(exchange=EX_FANOUT, queue=QUEUE_AUDIT)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=QUEUE_AUDIT, on_message_callback=on_message)
            print("[AuditService] Esperando todos los eventos por fanout...")
            channel.start_consuming()
        except Exception as e:
            print(f"[AuditService] Error de conexion: {e}. Reintentando...")
            time.sleep(5)

if __name__ == "__main__":
    main()
