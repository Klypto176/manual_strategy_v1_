from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

from indicators import process_stock_tick

app = FastAPI(
    title="Stock Indicator API",
    description="Process stock ticks with SMA, RSI, SSL indicators and return trade signals",
    version="1.0.0",
)


class TickData(BaseModel):
    datetime: str
    open: float
    high: float
    low: float
    close: float
    volume: Optional[int] = 0
    stock_code: Optional[str] = "UNKNOWN"


class PredictRequest(BaseModel):
    historic_data: List[dict]
    tick: TickData


class HealthResponse(BaseModel):
    status: str
    service: str


@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", service="stock-indicator-api")


@app.post("/predict")
def predict(request: PredictRequest):
    result = process_stock_tick(request.historic_data, request.tick.model_dump())
    if result is None:
        raise HTTPException(status_code=204, detail="No trade signal generated")
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=False)
