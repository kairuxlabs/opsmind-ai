from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import approval, feedback, playground, workflow

app = FastAPI(
    title="OpsMind AI",
    version="5.0.0",
    description="Enterprise AI Operating System — Autonomous Multi-Agent Decision Intelligence",
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
app.include_router(feedback.router, prefix="/api")
app.include_router(playground.router, prefix="/api")
