"""
Minimal test handler to verify Vercel Python functions work
"""
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from mangum import Mangum

app = FastAPI()

@app.get("/")
async def test():
    return JSONResponse({"message": "Vercel Python function is working!", "status": "success"})

handler = Mangum(app, lifespan="off")
