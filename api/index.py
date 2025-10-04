from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import numpy as np

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

@app.post("/analytics")
async def post_analytics(request: Request):
    data = await request.json()
    regions = data.get("regions", [])
    threshold = data.get("threshold_ms", 180)

    # Dummy telemetry data example
    # In reality, you’d read from a database or API
    telemetry = {
        "apac": [150, 160, 170, 200, 190],
        "emea": [140, 180, 190, 210, 175],
        "amer": [120, 130, 125, 135, 140]
    }

    response = {}
    for region in regions:
        latencies = telemetry.get(region, [])
        if not latencies:
            continue
        latencies = np.array(latencies)
        avg_latency = float(np.mean(latencies))
        p95_latency = float(np.percentile(latencies, 95))
        avg_uptime = 100.0  # placeholder
        breaches = int(np.sum(latencies > threshold))
        response[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches
        }

    return response
