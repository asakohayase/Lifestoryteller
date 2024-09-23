from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os


def add_middleware(app: FastAPI) -> None:
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[frontend_url],
        allow_methods=["*"],
        allow_headers=["*"],
    )
