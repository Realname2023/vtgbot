from aiogram import types, Router, F, Bot, html
from aiogram.types import ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest
from contextlib import suppress
from sqlalchemy.ext.asyncio import AsyncSession
from handlers.states import OrderHist
from foundation import (url_webhook, b24rest_request, method_deal_add, method_contact_list, 
                        method_contact_update, method_contact_add, method_products_set)
from data_base.orm_query import (select_client, get_user_orders, delete_cur_orders, get_comment,
                                 add_order, get_orders_history, get_order_by_id, delete_comment)
from keyboards.client_kb import order_kb, kb_client


order_router= Router()


async def create_order(session: AsyncSession, user_id: int, bot: Bot):
    client = await select_client(session=session, user_id=user_id)
    user_orders = await get_user_orders(session=session, user_id=user_id)
    if user_orders == [] or client is None:
        await bot.send_message(
            user_id, "У Вас еще нет текущих заказов. Выберите товары и создайте заказ", reply_markup=kb_client
        )
    else:
        client_city = client.city
        org_name = client.org_name
        address = client.address
        phone = client.phone
        info_client = html.bold(f'Заказ от {org_name} из {client_city}:\nорганизация: {org_name}\nАдрес: {address}\nТелефон: {phone}\n')
        asum = 0
        strpos = ''
        for ret in user_orders:
            if ret.good.is_arenda==1:
                pos = (
                    f'{ret.good.name}\n в количестве {ret.quantity} {ret.good.unit} на {ret.arenda_time} месяцев '
                    f'по цене {f"{ret.good.price:,}".replace(",", " ")} тенге\n на сумму {f"{ret.total_price:,}".replace(",", " ")} тенге\nСклад:{ret.good.city}\n--------------------------------------------\n')
           
            else:
                pos = (
                    f'{ret.good.name}\n в количестве {ret.quantity} {ret.good.unit}\n по цене {f"{ret.good.price:,}".replace(",", " ")} тенге\n'
                    f' на сумму {f"{ret.total_price:,}".replace(",", " ")} тенге\nСклад:{ret.good.city}\n--------------------------------------------\n'
                )
            strpos = strpos + pos
            asum = asum + ret.total_price
        comment = ''
        comments = await get_comment(user_id=user_id)
        print(comments)
        if comments is not None:
            comment = comments.decode('utf-8')
        all_sum = f'Общая сумма Вашего заказа {f"{asum:,}".replace(",", " ")} тенге\n'
        order = info_client + '--------------------------------------------\n' + strpos + all_sum + f"Комментарий: {comment}"
        await bot.send_message(
            user_id,
            'Ваш заказ добавлен. Если у Вас изменился адрес доставки или другие данные, то укажите'
            ' это в комментарии (кнопка "Добавить комментарий к заказу")'
            ' Нажмите кнопку "Отправить заказ", '
            'чтобы заказать товары, либо дополните заказ, используя остальные кнопки.',
            reply_markup=ReplyKeyboardRemove(),
        )
        await bot.send_message(
            user_id, order, reply_markup=order_kb
        )


@order_router.callback_query(F.data=='myorder')
async def client_order(call: types.CallbackQuery, session: AsyncSession, bot: Bot):
    await call.message.edit_reply_markup()
    user_id = call.from_user.id
    await create_order(session=session, user_id=user_id, bot=bot)


@order_router.callback_query(F.data=='order')
async def send_order(call: types.CallbackQuery, session: AsyncSession):
    with suppress(TelegramBadRequest):
        await call.message.edit_reply_markup()
    user_id = call.from_user.id
    client = await select_client(session=session, user_id=user_id)
    user_orders = await get_user_orders(session=session, user_id=user_id)
    client_city = client.city
    client_address = client.address
    client_phone = client.phone
    tittle = client.user.full_name
    linc = "не указан"
    user_name = client.user.user_name
    if user_name is not None:
        linc = f"https://t.me/{user_name}"
    order = call.message.text
    parametr_contact_list = {
		'filter': {"PHONE": client_phone},
		'select': ["ID", "NAME"]
	}
    response4 = await b24rest_request(url_webhook, method_contact_list, parametr_contact_list)
    if response4.get('result') != []:

        contact_id = response4.get('result')[-1].get('ID')
        contact_name = response4.get('result')[-1].get('NAME')
        if contact_name == 'Без имени':
            parametr_contact_update = {
                "id": contact_id,
                "fields": {'NAME': tittle}
            }

            await b24rest_request(url_webhook, method_contact_update, parametr_contact_update)
    else:
        parametr_contact_add = {"fields": {
                    "NAME": tittle,
                    "PHONE": [{'VALUE': client_phone, "VALUE_TYPE": "WORK"}],
                    "ADDRESS": client_address,
                    "ADDRESS_2": linc,
                    "ADDRESS_CITY": client_city,
                    "IM": [{
                        "VALUE": "Telegram",	
                        "VALUE_TYPE": "Telegram"}],
                    "SOURCE_ID": "UC_SLN7SG"
                    }}
        response2 = await b24rest_request(url_webhook, method_contact_add, parametr_contact_add)
        contact_id = str(response2.get('result'))
        

    parametr_deal_add = {"fields": {
                    "TITLE": tittle,
                    "STAGE_ID": "NEW",
                    "SOURCE_ID": "UC_SLN7SG",
                    "CONTACT_ID": contact_id,
                    "UF_CRM_1708511776232": client_city,
                    "COMMENTS": order}}
    response = await b24rest_request(url_webhook, method_deal_add, parametr_deal_add)

    deal_id = str(response.get('result'))
    poses = []
    for ret in user_orders:
        quantity = ret.quantity
        price = ret.good.price
        
        if ret.good.is_arenda==1:
            for i in range(quantity):
                i = {"PRODUCT_ID": ret.good.b_id,
                        "PRICE": float(price),
                        "QUANTITY": ret.arenda_time,
                        "MEASURE_CODE": 323
                        }
                poses.append(i)
        else:
            pos = {"PRODUCT_ID": ret.good.b_id,
                "PRICE": float(price),
                "QUANTITY": quantity
                }
            poses.append(pos)
    
    parametr_products_set = {
        "id": deal_id,
        "rows": poses}

    await b24rest_request(url_webhook, method_products_set, parametr_products_set)
    
    await call.message.answer("Спасибо, ваш заказ в работе. Напишите нам, если у вас остались вопросы.",
                              reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Написать оператору", url='https://t.me/VTGonlinebot')]]))
    await call.message.answer("==================================", reply_markup=kb_client)
    await add_order(session=session, user_id=user_id, order_text=order)
    await delete_cur_orders(session=session, user_id=user_id)
    await delete_comment(user_id=user_id)
    await call.answer()


@order_router.callback_query(F.data=='ordhist')
async def get_users_orders_history(call: types.CallbackQuery, session: AsyncSession):
    await call.message.edit_reply_markup()
    user_id = call.from_user.id
    print(user_id)
    orders = await get_orders_history(session=session, user_id=user_id)
    if orders==[]:
        await call.message.answer("У Вас еще нет заказов. Выберите товары и создайте заказ", 
                                  reply_markup=kb_client)
    else:
        keyboard=InlineKeyboardBuilder()
        for ret in orders:
            keyboard.add(InlineKeyboardButton(
                text=f'Заказ №{ret.id} от {ret.created.strftime("%d.%m.%Y %H:%M")}', 
                callback_data=OrderHist(id=ret.id).pack()))
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data='back'))
        keyboard.adjust(1)
        await call.message.answer("Выберите заказ, который Вы хотите посмотреть", 
                                  reply_markup=keyboard.as_markup())
    await call.answer()


@order_router.callback_query(OrderHist.filter())
async def get_sended_order(call: types.CallbackQuery, callback_data: OrderHist,
                      session: AsyncSession):
    await call.message.edit_reply_markup()
    order_id = callback_data.id
    order = await get_order_by_id(session=session, order_id=order_id)
    date = order.created.strftime("%d.%m.%Y %H:%M")
    await call.message.answer(f'{date}\n{order.order_text}', reply_markup=
                              InlineKeyboardMarkup(inline_keyboard=[
                                  [InlineKeyboardButton(text='Назад', callback_data='back')]
                              ]))
    await call.answer()
