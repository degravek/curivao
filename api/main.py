import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from api.routes.rooms import router as rooms_router  # noqa: E402 — after load_dotenv


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Curivo API", lifespan=lifespan)

_frontend_origin = os.getenv("NEXT_PUBLIC_API_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", _frontend_origin],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(rooms_router)
