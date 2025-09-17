from fastapi import FastAPI
from db import lifespan
from routes import trading, auth 

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)     
app.include_router(trading.router)  
