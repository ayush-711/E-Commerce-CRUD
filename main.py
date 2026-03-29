from fastapi import FastAPI
from routes import user , product
from database import db

app = FastAPI()

@app.get("/")
async def test():
    return {"msg": "working"}

app.include_router(user.router, prefix="/user")
app.include_router(product.router)