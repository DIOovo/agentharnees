from fastapi import FastAPI

app = FastAPI(
    title="Agent Dashboard Demo",
    description="A simple backend for managing agent tasks.",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"message": "Agent Dashboard Demo is running"}