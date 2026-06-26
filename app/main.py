from fastapi import FastAPI
from app.routers import tasks

app = FastAPI(
    title="Agent Dashboard Demo",
    description="A simple backend for managing agent tasks.",
    version="0.1.0",
)


@app.get("/")
def root():
    return {"message": "Agent Dashboard Demo is running"}


app.include_router(tasks.router)