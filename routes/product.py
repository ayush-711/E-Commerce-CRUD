from fastapi import APIRouter, Depends , HTTPException
from utils.auth import verify_token
from schemas.product_schema import ProductCreate
from database import db
from bson import ObjectId

router = APIRouter()

@router.post("/")
@router.post("/create-product")
async def create_product(product: ProductCreate, user=Depends(verify_token)):
    
    product_dict = product.model_dump() #used model_dump() instead of dict()
    
    product_dict["owner"] = user["email"]
    
    await db.products.insert_one(product_dict)
    
    return {"msg": "Product added"}

@router.get("/protected")
async def protected_route(user=Depends(verify_token)):
    return {"msg": "Authorized", "user": user}

@router.get("/get-products")
async def get_products(user=Depends(verify_token)):
    
    products = []
    
    async for product in db.products.find({"owner": user["email"]}):
        product["_id"] = str(product["_id"])
        products.append(product)
    
    return products

@router.put("/update-product/{id}")
async def update_product(id: str, product: ProductCreate, user=Depends(verify_token)):
    
    result = await db.products.update_one(
        {"_id": ObjectId(id), "owner": user["email"]},
        {"$set": product.model_dump()} #used model_dump() instead of dict()
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"msg": "Product updated"}


@router.delete("/delete-product/{id}")
async def delete_product(id: str, user=Depends(verify_token)):
    
    result = await db.products.delete_one({
        "_id": ObjectId(id),
        "owner": user["email"]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"msg": "Product deleted"}