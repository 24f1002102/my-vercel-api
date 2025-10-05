from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json, math
from pathlib import Path
import uvicorn


app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST", "OPTIONS", "GET"],  # include GET for browser
    allow_headers=["*"],
    expose_headers=["*"]
)

# Load telemetry
DATA_PATH = Path(__file__).parent / "telemetry.json"
with open(DATA_PATH, "r", encoding="utf-8") as f:
    telemetry = json.load(f)

def percentile(values, p):
    if not values:
        return None
    values = sorted(values)
    k = (len(values) - 1) * (p / 100)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return values[int(k)]
    return values[f] * (c - k) + values[c] * (k - f)

# POST endpoint (for dashboards)
@app.post("/api/latency")
async def latency_post(request: Request):
    body = await request.json()
    regions = body.get("regions", [])
    threshold = body.get("threshold_ms", 180)

    result = {}
    for region in regions:
        region_data = [r for r in telemetry if r.get("region") == region]
        latencies = [r["latency_ms"] for r in region_data if "latency_ms" in r]
        uptimes = [r["uptime_pct"] for r in region_data if "uptime_pct" in r]

        if not region_data:
            result[region] = {
                "avg_latency": None,
                "p95_latency": None,
                "avg_uptime": None,
                "breaches": 0
            }
            continue

        avg_latency = sum(latencies) / len(latencies)
        p95_latency = percentile(latencies, 95)
        avg_uptime = sum(uptimes) / len(uptimes) if uptimes else None
        breaches = sum(1 for x in latencies if x > threshold)

        result[region] = {
            "avg_latency": round(avg_latency, 3),
            "p95_latency": round(p95_latency, 3),
            "avg_uptime": round(avg_uptime, 3) if avg_uptime else None,
            "breaches": breaches
        }

    return {"regions":[result]}

# GET endpoint (for browser)
@app.get("/api/latency")
def latency_get():
    return {"message": "Latency API is live. Use POST / with JSON body to get metrics."}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)