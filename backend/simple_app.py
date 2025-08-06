from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello from DocuGenie Ultra!", "status": "working"}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "docugenie"}
