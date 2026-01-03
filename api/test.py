"""
Minimal test handler to verify Vercel Python functions work
"""
from fastapi import FastAPI
from mangum import Mangum

app = FastAPI()

@app.get("/")
async def test():
    return {"message": "Vercel Python function is working!", "status": "success"}

# Vercel expects 'app' or a function named 'handler'
# Create handler as a function, not just assignment
def handler(event, context):
    asgi_handler = Mangum(app, lifespan="off")
    return asgi_handler(event, context)
