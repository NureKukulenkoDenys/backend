from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    auth,
    admin_router,
    business_router,
    emergency_router,
    iot_router,   
)

app = FastAPI(
    title="GASGUARD",
    version="1.0",
    description="IoT gas monitoring & emergency response system"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(admin_router.router)
app.include_router(business_router.router)
app.include_router(emergency_router.router)
app.include_router(iot_router.router)  
