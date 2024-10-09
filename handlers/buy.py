import re
from aiogram import types, Router, F, Bot
from aiogram.types import ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from .states import BuyItem, FSMBuy
from .order import create_order
from data_base.orm_query import (get_product, select_client, 
                                 add_current_order, select_user, orm_add_user)
from data_base.models import Client
from keyboards.client_kb import phone_button_kb, kb_client, cancel_buy_kb


buy_router = Router()


@buy_router.message(StateFilter("*"), Command("отмена"))
async def cancel_buy(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    await message.answer('Ok', reply_markup=ReplyKeyboardRemove())
    await message.answer('Выберите товары и создайте заказ', reply_markup=kb_client)
    if current_state is None:
        return
    await state.clear()
    

@buy_router.callback_query(BuyItem.filter())
async def callback_buy(call: types.CallbackQuery, callback_data: BuyItem, 
                       session: AsyncSession, state: FSMContext):
    await call.message.edit_reply_markup()
    user_id = call.from_user.id
    user = await select_user(session=session, user_id=user_id)
    if user is None:
        await orm_add_user(session=session, user_id=user_id, full_name=call.from_user.full_name, 
                           user_name=call.from_user.username)
    item_id = callback_data.id
    good = await get_product(session=session, good_id=item_id)
    item_b_id = good.b_id
    # item_name = good.name
    item_verbosename = good.verbose_name
    item_unit = good.unit
    item_price = good.price
    item_is_arenda = good.is_arenda
    item_city = good.city
    await call.answer(text=f'Укажите количество {item_unit} {item_verbosename}.', show_alert=True)
    await call.message.answer(text=f"Укажите количество {item_unit} {item_verbosename}",
                              reply_markup=cancel_buy_kb)
    await state.set_state(FSMBuy.buy_quantity)
    await state.update_data(buy_item_id=item_id)
    await state.update_data(buy_b_id=item_b_id)
    await state.update_data(buy_verbosename=item_verbosename)
    await state.update_data(buy_unit=item_unit)
    await state.update_data(city=item_city)
    await state.update_data(buy_price=item_price)
    await state.update_data(buy_is_arenda=item_is_arenda)


@buy_router.message(FSMBuy.buy_quantity, F.text)
async def load_quantity(message: types.Message, session: AsyncSession, state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    pat = r"[^0-9]"
    answer = re.sub(pat, "", message.text)
    try:
        answer = int(answer)
    except ValueError:
        await message.answer("Укажите количество в цифрах")
        return
    await state.update_data(buy_quantity=answer)
    data = await state.get_data()
    verbose_name = data.get('buy_verbosename')
    is_arenda = data.get('buy_is_arenda')
    client = await select_client(session=session, user_id=user_id)
    if is_arenda==1:
        await message.answer(f"Укажите на сколько месяцев Вы арендуете {verbose_name}")
        await state.set_state(FSMBuy.buy_arenda_time)
    elif client is None:
        await message.answer("Укажите нименование Вашей организации  если Вы физ лицо, то напишите как к Вам обращаться")
        await state.set_state(FSMBuy.org_name)
    else:
        item_id = data.get("buy_item_id")
        price = data.get('buy_price')
        quantity = int(data.get('buy_quantity'))
        arenda_time = 0
        total_price = price*quantity
        await add_current_order(session=session, user_id=user_id, good_id=item_id,
                            quantity=quantity, arenda_time=arenda_time, 
                            total_price=total_price)
        await message.answer("ok")
        await state.clear()
        await create_order(session=session, user_id=user_id, bot=bot)


@buy_router.message(FSMBuy.buy_arenda_time, F.text)
async def indicate_arenda_time(message: types.Message, session: AsyncSession, 
                               state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    pat = r"[^0-9]"
    answer = re.sub(pat, "", message.text)
    try:
        answer = int(answer)
    except ValueError:
        await message.answer("Укажите время аренды в цифрах")
        return
    await state.update_data(buy_arenda_time=answer)
    client = await select_client(session=session, user_id=user_id)
    if client is None:
        await message.answer("Укажите нименование Вашей организации  если Вы физ лицо, то напишите как к Вам обращаться")
        await state.set_state(FSMBuy.org_name)
    else:
        data = await state.get_data()
        item_id = data.get("buy_item_id")
        price = data.get('buy_price')
        quantity = int(data.get('buy_quantity'))
        arenda_time = int(data.get("buy_arenda_time"))
        total_price = price*quantity*arenda_time
        await add_current_order(session=session, user_id=user_id, good_id=item_id, 
                                quantity=quantity, arenda_time=arenda_time, 
                                total_price=total_price)
        await message.answer("ok")
        await state.clear()
        await create_order(session=session, user_id=user_id, bot=bot)


@buy_router.message(FSMBuy.org_name, F.text)
async def indicate_org(message: types.Message, state: FSMContext):
    org_name = message.text
    await state.update_data(org_name=org_name)
    await message.answer("Укажите адрес доставки")
    await state.set_state(FSMBuy.address)


@buy_router.message(FSMBuy.address, F.text)
async def indicate_address(message: types.Message, state: FSMContext):
    address = message.text
    await state.update_data(address=address)
    await message.answer("Для обратной связи поделитесь контактом. Нажмите /Поделиться_контактом", 
                         reply_markup=phone_button_kb)
    await state.set_state(FSMBuy.phone)


@buy_router.message(FSMBuy.phone)
async def indicate_phone(message: types.Message, session: AsyncSession,
                          state: FSMContext, bot: Bot):
    phone = message.contact.phone_number
    user_id = message.from_user.id
    data = await state.get_data()
    city = data.get("city")
    org_name = data.get("org_name")
    address = data.get("address")
    session.add(Client(user_id=user_id, city=city, org_name=org_name, address=address,
                    phone=phone))
    await session.commit()
    item_id = data.get("buy_item_id")
    price = data.get('buy_price')
    quantity = int(data.get('buy_quantity'))
    is_arenda = data.get('buy_is_arenda')
    city = data.get("city")
    total_price = price * quantity
    if is_arenda==1:
        arenda_time = int(data.get("buy_arenda_time"))
        total_price = price*quantity*arenda_time
    else:
        arenda_time=0    
    await add_current_order(session=session, user_id=user_id, good_id=item_id, 
                            quantity=quantity, arenda_time=arenda_time, 
                            total_price=total_price)
    await message.answer("ok")
    await state.clear()
    await create_order(session=session, user_id=user_id, bot=bot)
