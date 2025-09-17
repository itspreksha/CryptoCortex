from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from fastapi import FastAPI
import os
from dotenv import load_dotenv

from models import User, Transaction, Portfolio

load_dotenv()
mongo_uri = os.getenv("MONGO_URI")
DATABASE_NAME = "CryptoCortex"

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = AsyncIOMotorClient(mongo_uri)
    db = client[DATABASE_NAME]

    # Register Beanie document models
    await init_beanie(
        database=db,
        document_models=[User, Transaction, Portfolio]
    )

    yield

    client.close()
