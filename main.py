from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from typing import List

from database import get_async_session
from models import Base
from schemas import ProductOut, OrderCreate, OrderOut
from crud import (
    get_product_list,
    create_order,
    get_order,
    increment_product_stock,
    get_user_by_id
)

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    # Could initialize alembic migrations or check conn
    pass

@app.get("/products", response_model=List[ProductOut])
async def list_products(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_async_session())):
    products = await get_product_list(db, skip, limit)
    return products

@app.post("/orders", response_model=OrderOut, status_code=201)
async def create_new_order(
    order_in: OrderCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session()),
):
    # User check
    user = await get_user_by_id(db, order_in.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Try create order
    try:
        order = await create_order(db, order_in.user_id, [item.dict() for item in order_in.items])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Example: defer replenishing low-stock products to background
    async def refill_if_needed(product_id, threshold=10, refill_qty=100):
        async with get_async_session()() as session:
            product = await session.get(type(order.items[0].product), product_id)
            if product.stroke is not None and product.stock < threshold:
                # Simulate supplier refill
                await increment_product_stock(session, product_id, refill_qty)

    for item in order.items:
        background_tasks.add_task(refill_if_needed, item.product_id)

    return order

@app.get("/orders/{order_id}", response_model=OrderOut)
async def get_order_endpoint(order_id: int, db: AsyncSession = Depends(get_async_session())):
    order = await get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
