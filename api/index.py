from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path

app = FastAPI()

# Enable CORS for any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods
    allow_headers=["*"],  # allow all headers
)

# Load telemetry
telemetry_file = Path(__file__).parent / "telemetry.json"
telemetry_df = pd.read_json(telemetry_file)

@app.post("/analytics")
def analytics(payload: dict):
    regions = payload.get("regions", [])
    threshold = payload.get("threshold_ms", 180)

    result = {}
    for region in regions:
        df_region = telemetry_df[telemetry_df["region"] == region]
        if df_region.empty:
            continue
        avg_latency = df_region["latency_ms"].mean()
        p95_latency = df_region["latency_ms"].quantile(0.95)
        avg_uptime = df_region["uptime_pct"].mean()
        breaches = (df_region["latency_ms"] > threshold).sum()

        result[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": int(breaches),
        }
    return result
