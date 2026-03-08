from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.base import get_engine
from app.db.config import Settings
from app.routers.category import router as category_router
from app.routers.hangout import router as hangout_router
from app.routers.subcategory import router as subcategory_router
from app.routers.transaction import router as transaction_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = get_engine()
    app.state.engine = engine
    yield
    engine.dispose()


app = FastAPI(title="Streetrack API", lifespan=lifespan)

settings = Settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Streetrack API"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(category_router)
app.include_router(hangout_router)
app.include_router(subcategory_router)
app.include_router(transaction_router)
