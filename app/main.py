from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    auth,
    admin_router,
    business_router,
    emergency_router,
    iot_router,   # 🔥 новий router для датчиків
)

app = FastAPI(
    title="GASGUARD",
    version="1.0",
    description="IoT gas monitoring & emergency response system"
)

# -----------------------------
# CORS (важливо для IoT / frontend)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # для лабораторної OK
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# ROUTERS
# -----------------------------
app.include_router(auth.router)
app.include_router(admin_router.router)
app.include_router(business_router.router)
app.include_router(emergency_router.router)
app.include_router(iot_router.router)   # 🔥 підключення IoT
