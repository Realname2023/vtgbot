import re
from aiogram import types, Router, F, Bot
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from handlers.states import DeleteItem, NewQuant, FSMOrder
from handlers.order import create_order
from data_base.orm_query import (get_user_orders, delete_cur_orders, 
                                 delete_cur_order, get_user_order, change_quantity_cur_order,
                                 change_arenda_time, store_comment, delete_comment)
from keyboards.client_kb import kb_client, cancel_change_kb


update_order_router = Router()

@update_order_router.message(StateFilter("*"), Command("отменить"))
async def cancel_order(message: types.Message, session: AsyncSession,
                        state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    current_state = await state.get_state()
    await message.answer('Ok', reply_markup=ReplyKeyboardRemove())
    await create_order(session, user_id, bot)
    if current_state is None:
        return
    await state.clear()


@update_order_router.callback_query(F.data=='addorder')
async def order_add(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer("Выберите товары для того, чтобы добавить их в заказ", 
                              reply_markup=kb_client)
    await call.answer()


@update_order_router.callback_query(F.data=='delitem')
async def delete_item_button(call: types.CallbackQuery, session: AsyncSession):
    await call.message.edit_reply_markup()
    user_id = call.from_user.id
    user_orders = await get_user_orders(session=session, user_id=user_id)
    keyboard = InlineKeyboardBuilder()
    for item in user_orders:
        keyboard.add(
            InlineKeyboardButton(
                text=item.good.name, callback_data=DeleteItem(good_id=item.good_id).pack()))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='myorder'))
    keyboard.adjust(1)
    await call.message.answer('Выберите товар, который вы хотите удалить',
                              reply_markup=keyboard.as_markup())
    await call.answer()


@update_order_router.callback_query(DeleteItem.filter())
async def delete_item(call: types.CallbackQuery, callback_data: DeleteItem,
                      session: AsyncSession, bot: Bot):
    await call.message.edit_reply_markup()
    user_id = call.from_user.id
    good_id = callback_data.good_id
    item = await get_user_order(session, user_id, good_id)
    await delete_cur_order(session, user_id, good_id)
    await call.message.answer(text=f'{item.good.name} удалена')
    await create_order(session, user_id, bot)
    await call.answer(text=f'{item.good.name} удалена', show_alert=True)


@update_order_router.callback_query(F.data=='change')
async def change_quantity(call: types.CallbackQuery, session: AsyncSession):
    await call.message.edit_reply_markup()
    user_id = call.from_user.id
    user_orders = await get_user_orders(session=session, user_id=user_id)
    keyboard = InlineKeyboardBuilder()
    for item in user_orders:
        keyboard.add(
            InlineKeyboardButton(
                text=item.good.name, callback_data=NewQuant(good_id=item.good_id).pack()))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data='myorder'))
    keyboard.adjust(1)
    await call.message.answer(
        'Выберите товар количество или время аренды, которого вы хотите изменить',
                              reply_markup=keyboard.as_markup())
    await call.answer()


@update_order_router.callback_query(NewQuant.filter())
async def callback_new_quantity(call: types.CallbackQuery, callback_data: NewQuant,
                      session: AsyncSession, state: FSMContext):
    await call.message.edit_reply_markup()
    user_id = call.from_user.id
    good_id = callback_data.good_id
    item = await get_user_order(session, user_id, good_id)
    await call.answer(
            text=f"Укажите новое количество {item.good.verbose_name}.", show_alert=True
        )
    await call.message.answer(f"Укажите новое количество {item.good.verbose_name}.",
                              reply_markup=cancel_change_kb)
    await state.set_state(FSMOrder.new_quantity)
    await state.update_data(order_item_id=good_id)
    await state.update_data(order_is_arenda=item.good.is_arenda)


@update_order_router.message(FSMOrder.new_quantity)
async def load_new_quantity(message: types.Message, session: AsyncSession,
                             state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    pat = r"[^0-9]"
    answer = re.sub(pat, "", message.text)
    try:
        answer = int(message.text)
    except ValueError:
        await message.answer("Укажите количество в цифрах")
        return
    answer = message.text
    await state.update_data(new_quantity=answer)
    data = await state.get_data()
    new_quantity = int(data.get("new_quantity"))
    good_id = data.get("order_item_id")
    is_arenda = data.get("order_is_arenda")
    await change_quantity_cur_order(session=session, user_id=user_id, good_id=good_id,
                                    new_quantity=new_quantity)
    await message.answer("Количество товара успешно изменено", 
                         reply_markup=ReplyKeyboardRemove())
    if is_arenda==1:
        await message.answer("Укажите новое время аренды в месяцах", 
                             reply_markup=cancel_change_kb)
        await state.set_state(FSMOrder.new_arenda_time)
    else:
        await state.clear()
        await create_order(session, user_id, bot)


@update_order_router.message(FSMOrder.new_arenda_time)
async def load_new_arenda_time(message: types.Message, session: AsyncSession, 
                               state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    pat = r"[^0-9]"
    answer = re.sub(pat, "", message.text)
    try:
        answer = int(message.text)
    except ValueError:
        await message.answer("Укажите время аренды в цифрах")
        return
    answer = message.text
    data = await state.get_data()
    good_id = data.get("order_item_id")
    new_time_arenda = int(answer)
    await change_arenda_time(session=session, user_id=user_id, good_id=good_id,
                             new_arenda_time=new_time_arenda)
    await state.clear()
    await create_order(session, user_id, bot)


@update_order_router.callback_query(F.data=='comment')
async def get_comment(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()
    await call.message.answer('Напишите Ваш комментарий к заказу', 
                              reply_markup=cancel_change_kb)
    await state.set_state(FSMOrder.comment)
    await call.answer()


@update_order_router.message(FSMOrder.comment)
async def set_comments(message: types.Message, session: AsyncSession, 
                      state: FSMContext, bot: Bot):
    user_id = message.from_user.id
    comment = message.text
    await store_comment(user_id=user_id, comment=comment)
    await state.clear()
    await create_order(session, user_id, bot)
    

@update_order_router.callback_query(F.data=='delorder')
async def delete_all_items(call: types.CallbackQuery, session: AsyncSession):
    await call.message.edit_reply_markup()
    user_id = call.from_user.id
    await delete_cur_orders(session, user_id)
    await delete_comment(user_id)
    await call.message.answer(text='Заказ удален. У вас нет заказов. Выберите товары и создайте заказ',
                              reply_markup=kb_client)
    await call.answer()

