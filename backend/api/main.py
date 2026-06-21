from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import approval, workflow

app = FastAPI(
    title="OpsMind AI",
    version="2.0.0",
    description="Autonomous Multi-Agent Decision Intelligence Platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(workflow.router, prefix="/api")
app.include_router(approval.router, prefix="/api")
