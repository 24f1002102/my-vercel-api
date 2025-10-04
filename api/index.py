from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
from pathlib import Path

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry.json once at startup
TELEMETRY_FILE = Path(__file__).parent / "telemetry.json"
with open(TELEMETRY_FILE, "r") as f:
    telemetry_data = json.load(f)

# Expected format: list of dicts with keys: region, latency_ms, uptime
# Example:
# [
#   {"region": "apac", "latency_ms": 150, "uptime": 99.9},
#   {"region": "emea", "latency_ms": 200, "uptime": 100},
#   ...
# ]

@app.post("/analytics")
async def analytics(request: Request):
    data = await request.json()
    regions = data.get("regions", [])
    threshold = data.get("threshold_ms", 180)

    response = {}
    for region in regions:
        region_records = [r for r in telemetry_data if r["region"] == region]
        if not region_records:
            continue

        latencies = np.array([r["latency_ms"] for r in region_records])
        uptimes = np.array([r["uptime"] for r in region_records])

        avg_latency = float(np.mean(latencies))
        p95_latency = float(np.percentile(latencies, 95))
        avg_uptime = float(np.mean(uptimes))
        breaches = int(np.sum(latencies > threshold))

        response[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches
        }

    return response
