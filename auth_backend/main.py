from fastapi import FastAPI
from auth_backend.routes.auth import router as auth_router
from auth_backend.routes.users import router as users_router
from fastapi.middleware.cors import CORSMiddleware
import fastapi_swagger_dark as fsd
from auth_backend.database.db import database

app = FastAPI(
    docs_url=None
)
fsd.install(app)

app.include_router(auth_router)
app.include_router(users_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        # "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "checking!!"}

@app.on_event("startup")
async def startup():
    await database.connect()
    await database.init_db()
    print("Database connected")


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    print("Database disconnected")
