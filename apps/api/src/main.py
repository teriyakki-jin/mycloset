from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.database import engine
from src.models import Base
from src.routers.auth import router as auth_router
from src.routers.garments import router as garments_router
from src.routers.health import router as health_router
from src.routers.recommendations import router as recommendations_router
from src.routers.wear_logs import router as wear_logs_router
from src.routers.style import router as style_router
from src.routers.tryon import router as tryon_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="ClosetIQ API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(garments_router)
app.include_router(recommendations_router)
app.include_router(wear_logs_router)
app.include_router(style_router)
app.include_router(tryon_router)
