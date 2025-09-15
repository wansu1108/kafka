# producer_kafka.py
# pip install confluent-kafka
import os, json
from confluent_kafka import Producer
from simulator_factory_data import stream_events

BOOTSTRAP = os.getenv("BOOTSTRAP", "localhost:29092")
TOPIC     = os.getenv("TOPIC", "telemetry.raw")
NUM_DEV   = int(os.getenv("NUM_DEV", "10"))
LAM_MEAN  = float(os.getenv("LAM_MEAN", "1.0"))
LAM_STD   = float(os.getenv("LAM_STD", "0.5"))

p = Producer({
    "bootstrap.servers": BOOTSTRAP,
    "linger.ms": 5,
    "compression.type": "zstd",
})

def main():
    for evt in stream_events(n=NUM_DEV, lam_mean=LAM_MEAN, lam_std=LAM_STD):
        key = evt["device_id"].encode()
        val = json.dumps(evt).encode("utf-8")
        p.produce(TOPIC, val, key=key)
        p.poll(0)  # 비동기 에러 콜백 드레인

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        p.flush()
