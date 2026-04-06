from fastapi import APIRouter, Depends , HTTPException, status
from utils.auth import verify_token, verify_role
from schemas.product_schema import ProductCreate
from database import db
from bson import ObjectId
from utils.Constants.app_constants import ERROR_MESSAGES, SUCCESS_MESSAGES
from Exceptions.decorators import (
    handle_validation_exceptions,
    handle_db_exceptions,
    handle_admin_exceptions,
    handle_exceptions
)

router = APIRouter()

# ===================== PRODUCT CREATION =====================

@router.post("/")
@router.post("/create-product")
@handle_validation_exceptions
@handle_db_exceptions
async def create_product(product: ProductCreate, user=Depends(verify_role(["admin", "supplier"]))):
    """
    Admin or Supplier: Create a new product/supply
    """
    product_dict = product.model_dump()
    product_dict["owner"] = user["email"]
    product_dict["owner_role"] = user["role"]
    
    await db.products.insert_one(product_dict)
    
    return {"msg": SUCCESS_MESSAGES["product_added"], "owner": user["email"], "role": user["role"]}

# ===================== PRODUCT RETRIEVAL =====================

@router.get("/protected")
@handle_exceptions
async def protected_route(user=Depends(verify_token)):
    """Test endpoint - all authenticated users"""
    return {"msg": "Authorized", "email": user.get("email"), "role": user.get("role")}

@router.get("/get-products")
@handle_db_exceptions
async def get_products(user=Depends(verify_token)):
    """
    All users: View products based on their role
    - Admin: See all products
    - User: See all products (marketplace view)
    - Supplier: See all products (including competitors)
    """
    products = []
    
    async for product in db.products.find({}):
        product["_id"] = str(product["_id"])
        products.append(product)
    
    return products

@router.get("/my-products")
@handle_db_exceptions
async def get_my_products(user=Depends(verify_token)):
    """
    User/Supplier/Admin: Get products owned by current user
    """
    products = []
    
    async for product in db.products.find({"owner": user["email"]}):
        product["_id"] = str(product["_id"])
        products.append(product)
    
    return products

# ===================== PRODUCT UPDATE =====================

@router.put("/update-product/{id}")
@handle_validation_exceptions
@handle_db_exceptions
async def update_product(id: str, product: ProductCreate, user=Depends(verify_token)):
    """
    Admin: Update any product
    Owner: Update own product
    """
    # Check if admin
    is_admin = user.get("role") == "admin"
    
    query = {"_id": ObjectId(id)}
    if not is_admin:
        # Non-admin can only update their own products
        query["owner"] = user["email"]
    
    result = await db.products.update_one(
        query,
        {"$set": product.model_dump()}
    )
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=ERROR_MESSAGES["product_not_found"]
        )
    
    return {"msg": SUCCESS_MESSAGES["product_updated"]}

# ===================== PRODUCT DELETION =====================

@router.delete("/delete-product/{id}")
@handle_db_exceptions
async def delete_product(id: str, user=Depends(verify_token)):
    """
    Admin: Delete any product
    Owner: Delete own product
    """
    # Check if admin
    is_admin = user.get("role") == "admin"
    
    query = {"_id": ObjectId(id)}
    if not is_admin:
        # Non-admin can only delete their own products
        query["owner"] = user["email"]
    
    result = await db.products.delete_one(query)
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ERROR_MESSAGES["product_not_found"]
        )
    
    return {"msg": SUCCESS_MESSAGES["product_deleted"]}

# ===================== ADMIN ENDPOINTS =====================

@router.delete("/admin/delete-product/{id}")
@handle_admin_exceptions
@handle_db_exceptions
async def admin_delete_product(id: str, admin_user=Depends(verify_role(["admin"]))):
    """
    Admin only: Force delete any product (even if suspected malicious activity)
    """
    result = await db.products.delete_one({"_id": ObjectId(id)})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["product_not_found"])
    
    return {"msg": f"Product {id} forcefully {SUCCESS_MESSAGES['product_deleted'].lower()}"}

@router.get("/admin/all-products")
@handle_admin_exceptions
@handle_db_exceptions
async def admin_view_all_products(admin_user=Depends(verify_role(["admin"]))):
    """
    Admin only: View all products with owner information
    """
    products = []
    
    async for product in db.products.find({}):
        product["_id"] = str(product["_id"])
        products.append(product)
    
    return products

@router.get("/admin/products-by-supplier/{supplier_email}")
@handle_admin_exceptions
@handle_db_exceptions
async def admin_view_supplier_products(
    supplier_email: str,
    admin_user=Depends(verify_role(["admin"]))
):
    """
    Admin only: View all products from a specific supplier
    """
    products = []
    
    async for product in db.products.find({"owner": supplier_email}):
        product["_id"] = str(product["_id"])
        products.append(product)
    
    return products