#!/usr/bin/env python3
"""Sustained load generator for the llm-d scaling exercise (Module 6).

Unlike a one-shot `for i in $(seq ...)` burst — which fires every request at once and
drains before the ~30s user-workload-monitoring scrape and 15s KEDA poll can observe it —
this holds a fixed number of concurrent requests in flight for a set duration, so
`vllm:num_requests_waiting` stays above the ScaledObject threshold long enough for KEDA to
add replicas. Standard-library only (no pip install needed on the bastion).

Reads the gateway coordinates from the environment exported earlier in the exercise:
  HOST, MODEL_PATH, MODEL_NAME, API_KEY

Usage:
  python3 manifests/06-llmd/load/load-test.py                 # 16 workers for 300s
  python3 manifests/06-llmd/load/load-test.py -c 24 -d 600    # heavier / longer
  Stop early with Ctrl-C.
"""
import argparse
import json
import os
import ssl
import sys
import threading
import time
import urllib.error
import urllib.request

def worker(stop_at, url, headers, payload, stats, ctx):
    body = json.dumps(payload).encode()
    while time.monotonic() < stop_at:
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120, context=ctx) as resp:
                resp.read()
                if resp.status == 200:
                    stats["ok"] += 1
                elif resp.status == 429:
                    stats["throttled"] += 1
                else:
                    stats["other"] += 1
        except urllib.error.HTTPError as e:
            if e.code == 429:
                stats["throttled"] += 1
            else:
                stats["other"] += 1
        except Exception:
            stats["errors"] += 1

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--concurrency", type=int, default=16,
                    help="number of concurrent requests to hold in flight (default 16)")
    ap.add_argument("-d", "--duration", type=int, default=300,
                    help="how long to sustain load, in seconds (default 300)")
    ap.add_argument("-m", "--max-tokens", type=int, default=32,
                    help="max_tokens per completion (default 32). Kept small so each completion "
                         "finishes well under the gateway's 30s route timeout — a timed-out "
                         "completion returns no 'usage' body, so Limitador meters 0 tokens for it "
                         "(the request still counts as authorized). Concurrency, not response "
                         "length, is what sustains the queue depth KEDA scales on.")
    args = ap.parse_args()

    host = os.environ.get("HOST", "").rstrip("/")
    path = os.environ.get("MODEL_PATH", "")
    model = os.environ.get("MODEL_NAME", "")
    key = os.environ.get("API_KEY", "")
    missing = [n for n, v in (("HOST", host), ("MODEL_PATH", path),
                              ("MODEL_NAME", model), ("API_KEY", key)) if not v]
    if missing:
        sys.exit(f"error: missing env vars: {', '.join(missing)} — re-run the mint/discover step "
                 f"in Exercise 5 (a blank MODEL_PATH means the /models call returned before the "
                 f"gateway was warm).")

    url = f"{host}{path}/v1/completions"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {"model": model, "prompt": "Write a short paragraph about scaling.",
               "max_tokens": args.max_tokens}
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE  # lab gateway uses a self-signed cert

    stats = {"ok": 0, "throttled": 0, "other": 0, "errors": 0}
    print(f"Driving {args.concurrency} concurrent requests at {url} for {args.duration}s "
          f"(Ctrl-C to stop early)")
    stop_at = time.monotonic() + args.duration
    threads = [threading.Thread(target=worker, args=(stop_at, url, headers, payload, stats, ctx),
                                daemon=True) for _ in range(args.concurrency)]
    for t in threads:
        t.start()
    try:
        start = time.monotonic()
        while any(t.is_alive() for t in threads):
            time.sleep(5)
            elapsed = int(time.monotonic() - start)
            print(f"  t={elapsed:>4}s  ok={stats['ok']} throttled={stats['throttled']} "
                  f"other={stats['other']} errors={stats['errors']}", flush=True)
    except KeyboardInterrupt:
        print("\nstopping…")
        stop_at = time.monotonic()
    for t in threads:
        t.join(timeout=125)
    print(f"done: ok={stats['ok']} throttled={stats['throttled']} "
          f"other={stats['other']} errors={stats['errors']}")

if __name__ == "__main__":
    main()
