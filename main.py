from fastapi import FastAPI
from routes import user , product
from database import db
from Exceptions.exception_handler import register_exception_handlers
from Exceptions.decorators import handle_exceptions

app = FastAPI()

# Register global exception handlers
register_exception_handlers(app)

@app.get("/")
@handle_exceptions
async def test():
    return {"msg": "working"}

app.include_router(user.router, prefix="/user")
app.include_router(product.router)