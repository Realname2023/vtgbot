from aiogram import types, Router, F, html
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from handlers.states import CategoryFactory, BuyItem
from data_base.orm_query import category_select, get_product
from keyboards.client_kb import kb_client, operator_kb


category_router=Router()


@category_router.callback_query(CategoryFactory.filter())
async def get_keyboard(call: types.CallbackQuery, callback_data: CategoryFactory, 
                       session: AsyncSession):
    await call.message.edit_reply_markup()
    keyboard = InlineKeyboardBuilder()
    param = callback_data.cat
    if param.startswith('buy_'):
        await call.message.answer('Наше предложение')
        param = int(param.replace('buy_', ''))
        try:
            good = await get_product(session=session, good_id=param)
            b_texts=good.button_texts.split('|')
            c_data=good.button_datas.split('|')
            for txt,cd in zip(b_texts,c_data):
                if cd==c_data[-1]:
                    keyboard.add(InlineKeyboardButton(text=txt, 
                                                    callback_data=CategoryFactory(cat=cd).pack()))
                else:
                    keyboard.add(InlineKeyboardButton(text=txt, 
                                                    callback_data=BuyItem(id=int(cd)).pack()))
            keyboard.adjust(1)
            await call.message.answer_photo(good.photo, caption=f'{html.bold(good.name)}\n{good.description}', 
                                            reply_markup=keyboard.as_markup())
        except Exception as e:
            print(f"Произошла ошибка: {type(e).__name__}")
            print(f"Сообщение ошибки: {e}")
            await call.message.answer('Товар не найден. Пожалуйста, обратитесь к оператору'
                                      ' , чтобы уточнить о наличии товара. '
                                      'Нажмите: "Написать оператору"',
                                      reply_markup=operator_kb)
    else:
        result = await category_select(session=session, callback=param)
        edit_text = result.edit_text
        r = tuple(result.row_width)
        rows = tuple(map(int, r))
        button_texts=result.buttons_text.split('|')
        c_datas=result.buttons_data.split('|')
        for txt,cd in zip(button_texts, c_datas):
            if cd in ["myorder", 'back']:
                keyboard.add(InlineKeyboardButton(text=txt, callback_data=cd))
            else:
                keyboard.add(InlineKeyboardButton(text=txt, 
                                                callback_data=CategoryFactory(cat=cd).pack()))
        keyboard.adjust(*rows)
        await call.message.answer(edit_text, reply_markup=keyboard.as_markup())
    await call.answer()


@category_router.callback_query(F.data=='back')
async def back_main(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer('Главное меню. Выберите товары и создайте заказ', 
                              reply_markup=kb_client)
    await call.answer()
