"""
Minimal test handler - Vercel native ASGI support
"""
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
@app.get("/api/test")
async def test():
    return {"message": "Vercel Python function is working!", "status": "success"}

# Vercel supports ASGI apps directly - just export 'app'
# No Mangum needed!
