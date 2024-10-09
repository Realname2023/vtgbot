from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from foundation import redis
from data_base.models import User, Category, Goods, Client, CurrentOrder, Actions, Order


async def orm_add_user(
    session: AsyncSession,
    user_id: int,
    full_name: str | None = None,
    user_name: str | None = None,
):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    if result.first() is None:
        session.add(
            User(user_id=user_id, full_name=full_name, user_name=user_name)
        )
        await session.commit()


async def select_user(session: AsyncSession, user_id: int):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    user = result.first()
    return user


async def category_select(session: AsyncSession, callback: str):
    query = select(Category).where(Category.callback == callback)
    result = await session.execute(query)
    return result.scalar()


async def get_product(session: AsyncSession, good_id: int):
    query = select(Goods).where(Goods.id == good_id)
    result = await session.execute(query)
    return result.scalar()


async def select_client(session: AsyncSession, user_id: int):
    query = select(Client).options(joinedload(Client.user)).where(Client.user_id == user_id)
    result = await session.execute(query)
    return result.scalar()


async def add_current_order(session: AsyncSession, user_id: int, good_id: int,
                            quantity: int, arenda_time: int, total_price: int):
    query = select(CurrentOrder).options(joinedload(CurrentOrder.good)).where(
        CurrentOrder.user_id == user_id,
        CurrentOrder.good_id == good_id
    )
    order = await session.execute(query)
    order = order.scalar()
    if order:
        quantity2 = order.quantity + quantity
        arenda_time2 = order.arenda_time + arenda_time
        order.total_price += total_price
        if order.good.is_arenda == 1:
            order.total_price = quantity2*arenda_time2*order.good.price
        order.quantity = quantity2
        order.arenda_time = arenda_time2
        await session.commit()
        return order
    else:
        session.add(CurrentOrder(user_id=user_id, good_id=good_id, quantity=quantity,
                                 arenda_time=arenda_time, total_price=total_price))
        await session.commit()


async def get_user_orders(session: AsyncSession, user_id):
    query = select(CurrentOrder).filter(CurrentOrder.user_id == user_id).options(joinedload(CurrentOrder.good))
    result = await session.execute(query)
    return result.scalars().all()


async def get_user_order(session: AsyncSession, user_id: int, good_id: int):
    query = select(CurrentOrder).options(joinedload(CurrentOrder.good)).where(
        CurrentOrder.user_id == user_id,
        CurrentOrder.good_id == good_id
    )
    order = await session.execute(query)
    order = order.scalar()
    return order


async def delete_cur_order(session: AsyncSession, user_id: int, good_id: int):
    query = delete(CurrentOrder).where(CurrentOrder.user_id == user_id, 
                                       CurrentOrder.good_id == good_id)
    await session.execute(query)
    await session.commit()


async def delete_cur_orders(session: AsyncSession, user_id: int):
    query = delete(CurrentOrder).where(CurrentOrder.user_id == user_id)
    await session.execute(query)
    await session.commit()


async def change_quantity_cur_order(session: AsyncSession, user_id: int, good_id: int,
                            new_quantity: int):
    query = select(CurrentOrder).options(joinedload(CurrentOrder.good)).where(
        CurrentOrder.user_id == user_id,
        CurrentOrder.good_id == good_id
    )
    order = await session.execute(query)
    order = order.scalar()
    order.quantity = new_quantity
    order.total_price = order.good.price*new_quantity
    if order.good.is_arenda == 1:
        order.total_price = order.good.price*order.arenda_time*new_quantity
    await session.commit()
    return order


async def change_arenda_time(session: AsyncSession, user_id: int, good_id: int,
                            new_arenda_time: int):
    query = select(CurrentOrder).options(joinedload(CurrentOrder.good)).where(
        CurrentOrder.user_id == user_id,
        CurrentOrder.good_id == good_id
    )
    order = await session.execute(query)
    order = order.scalar()
    order.arenda_time = new_arenda_time
    order.total_price = order.good.price*order.quantity*new_arenda_time
    await session.commit()
    return order


async def add_order(session: AsyncSession, user_id: int, order_text: str):
    session.add(Order(user_id=user_id, order_text=order_text))
    await session.commit()


async def get_orders_history(session: AsyncSession, user_id: int):
    query = select(Order).filter(Order.user_id == user_id)
    result = await session.execute(query)
    orders = result.scalars().all()
    return orders


async def get_order_by_id(session: AsyncSession, order_id: int):
    query = select(Order).where(Order.id == order_id)
    result = await session.execute(query)
    order = result.scalar()
    return order

async def select_action(session: AsyncSession):
    query = select(Actions)
    result = await session.execute(query)
    action = result.scalar()
    
    return action


async def store_comment(user_id: int, comment: str):
    
    await redis.set(f"comment:{user_id}", comment)


async def get_comment(user_id: int):
    
    return await redis.get(f"comment:{user_id}")


async def delete_comment(user_id: int):
    return await redis.delete(f"comment:{user_id}")
