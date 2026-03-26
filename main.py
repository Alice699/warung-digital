from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import create_tables
from routers import menu, orders, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield

app = FastAPI(
    title="Warung Digital API",
    description="REST API untuk sistem menu & pemesanan warung/UMKM lokal 🍜",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(menu.router, prefix="/menu", tags=["Menu"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])

@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Selamat datang di Warung Digital API! 🍜",
        "docs": "/docs",
        "version": "1.0.0"
    }
