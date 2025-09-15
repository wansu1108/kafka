import time, random, heapq, json, math, os
from dataclasses import dataclass


@dataclass
class Device:
    id: str
    lam: float # 평균 초당 이벤트 수 (람다)
    seq: int = 0
    value: float = 50.0


def exp_interval(lam: float) -> float:

    return random.expovariate(lam) if lam > 0 else 1.0


def step(x: float) -> float:

    return x + random.uniform(-0.5, 0.5)


def gen_devices(n=1000, lam_mean=1.0, lam_std=0.5):
    devs = []

    for i in range(n):
        lam = max(0.1, random.gauss(lam_mean, lam_std))
        devs.append(Device(id=f"dev-{i:04d}", lam=lam))

    return devs


def stream_events(n=1000, lam_mean=1.0, lam_std=0.5):
    devs = gen_devices(n, lam_mean, lam_std)

    q = []

    now = time.time()

    for idx, d in enumerate(devs):
        heapq.heappush(q, (now + exp_interval(d.lam), idx))


    while True:
        next_ts, idx = heapq.heappop(q)
        wait = next_ts - time.time()

        if wait > 0: time.sleep(wait)

        d = devs[idx]
        d.seq += 1
        d.value = round(step(d.value), 3)

        evt = {
            "ts" : time.time(),
            "device_id" : d.id,
            "seq" : d.seq,
            "params" : {"value": d.value}
        }
        yield evt

        heapq.heappush(q, (next_ts + exp_interval(d.lam), idx))

if __name__ == "__main__":

    for i, e in zip(range(10), stream_events(n=5, lam_mean = 1.0, lam_std = 0.5)):
        print(json.dumps(e, ensure_ascii=False))