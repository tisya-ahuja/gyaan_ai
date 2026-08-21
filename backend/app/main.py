from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.documents import router as documents_router


app = FastAPI(
    title="GyaanAI API",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://gyaanai.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    documents_router
)


@app.get("/")
def root():
    return {
        "message": "GyaanAI API is running."
    }


# ============================================================
# ROUTERS
# ============================================================

app.include_router(
    documents_router
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "GyaanAI API is running."
    }