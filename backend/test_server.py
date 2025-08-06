"""
Simple test server to verify FastAPI can run
"""
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World", "status": "working"}

@app.get("/health")
def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    print("Starting test server on http://localhost:8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)
