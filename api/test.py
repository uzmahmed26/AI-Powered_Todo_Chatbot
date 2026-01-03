"""
Minimal test handler to verify Vercel Python functions work
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from mangum import Mangum

app = FastAPI()

@app.get("/")
@app.get("/api/test")
async def test():
    return JSONResponse({"message": "Vercel Python function is working!", "status": "success"})

@app.get("/health")
async def health():
    return JSONResponse({"status": "healthy", "service": "test-api"})

handler = Mangum(app, lifespan="off")
