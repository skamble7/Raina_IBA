from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import run_iba

app = FastAPI(
    title="RAINA - Implementation Blueprint Agent",
    description="Service for parsing and reasoning on user stories to extract architecture-ready artifacts",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #For development: allow all. Use specific origins in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Register grouped routers

app.include_router(run_iba.router)
