from pydantic import BaseModel

class ProductCreate(BaseModel):
    name: str
    price: int
    description: str
    # quantity : int #Optioinal