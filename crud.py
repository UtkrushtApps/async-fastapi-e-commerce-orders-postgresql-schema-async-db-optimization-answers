from sqlalchemy.future import select
from sqlalchemy import update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from models import Product, Order, OrderItem, User

async def get_product_list(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Product).offset(skip).limit(limit))
    return result.scalars().all()

async def create_order(db: AsyncSession, user_id: int, items: list):
    # lock rows for update to safely decrement stock
    product_ids = [item['product_id'] for item in items]
    stmt = select(Product).where(Product.id.in_(product_ids)).with_for_update()
    result = await db.execute(stmt)
    products = {p.id: p for p in result.scalars().all()}

    # Check products exist and stock
    order_items = []
    for item in items:
        product = products.get(item['product_id'])
        if product is None:
            raise ValueError(f"Product {item['product_id']} not found")
        if product.stock < item['quantity']:
            raise ValueError(f"Insufficient stock for product {product.id}")

    # Deduct stock
    for item in items:
        product = products[item['product_id']]
        product.stock -= item['quantity']
        order_item = OrderItem(
            product_id=product.id,
            quantity=item['quantity'],
            price_at_purchase=product.price
        )
        order_items.append(order_item)

    order = Order(user_id=user_id, items=order_items)
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order

async def get_order(db: AsyncSession, order_id: int):
    stmt = select(Order).where(Order.id == order_id).options(selectinload(Order.items))
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    return order

async def increment_product_stock(db: AsyncSession, product_id: int, qty: int):
    stmt = (
        update(Product)
        .where(Product.id == product_id)
        .values(stock=Product.stock + qty)
        .execution_options(synchronize_session="fetch")
    )
    await db.execute(stmt)
    await db.commit()

async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
