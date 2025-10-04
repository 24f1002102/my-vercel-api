from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
from pathlib import Path
import statistics

app = FastAPI()

# Enable CORS for any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers
)

# Load telemetry data
telemetry_file = Path(__file__).parent / "telemetry.json"
with open(telemetry_file, "r") as f:
    telemetry = json.load(f)

@app.post("/analytics")
def analytics(data: dict):
    regions = data.get("regions", [])
    threshold_ms = data.get("threshold_ms", 180)
    
    result = {}
    for region in regions:
        region_data = [r for r in telemetry if r["region"] == region]
        if not region_data:
            continue
        latencies = [r["latency_ms"] for r in region_data]
        uptimes = [r["uptime_pct"] for r in region_data]
        breaches = sum(1 for l in latencies if l > threshold_ms)
        result[region] = {
            "avg_latency": statistics.mean(latencies),
            "p95_latency": statistics.quantiles(latencies, n=100)[94],  # 95th percentile
            "avg_uptime": statistics.mean(uptimes),
            "breaches": breaches
        }
    return result
