from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.config import ENV, DEBUG
from app.routes import auth, notes
from app.session import session_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    session_store.cleanup_expired()


app = FastAPI(
    title="SecretNotes",
    description="Encrypted notes application",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(notes.router, prefix="/api/notes", tags=["notes"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if DEBUG:
        return JSONResponse(status_code=500, content={"detail": str(exc)})
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
async def health():
    return {"status": "ok", "environment": ENV}