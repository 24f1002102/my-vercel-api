from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import statistics

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Embed telemetry data
telemetry = [
    {"region": "apac", "service": "payments", "latency_ms": 200.45, "uptime_pct": 97.13, "timestamp": 20250301},
    {"region": "apac", "service": "analytics", "latency_ms": 178.08, "uptime_pct": 98.635, "timestamp": 20250302},
    # Add more telemetry records here
]

@app.post("/analytics")
async def analytics(request: Request):
    data = await request.json()
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
        p95 = statistics.quantiles(latencies, n=100)[-5]  # safer 95th percentile
        result[region] = {
            "avg_latency": statistics.mean(latencies),
            "p95_latency": p95,
            "avg_uptime": statistics.mean(uptimes),
            "breaches": breaches
        }
    return result
