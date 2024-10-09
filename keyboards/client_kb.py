from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from handlers.states import CategoryFactory


kb_client = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Газы', callback_data=CategoryFactory(cat='cities').pack()),
    InlineKeyboardButton(text='Криогенные жидкости', url="https://wa.me/77779545000")],
    [InlineKeyboardButton(text='Баллоны для газов', callback_data=CategoryFactory(cat='country').pack()), 
    InlineKeyboardButton(text='Запчасти и услуги', callback_data=CategoryFactory(cat='complects').pack())],
    [InlineKeyboardButton(text='Оборудование',
                          callback_data=CategoryFactory(cat='eq_cat').pack())],
    [InlineKeyboardButton(text='Мой заказ', callback_data='myorder')],
    [InlineKeyboardButton(text='Адреса контакты', callback_data='addres'),
    InlineKeyboardButton(text='График работы', callback_data='worktime')],
    [InlineKeyboardButton(text='Акции', callback_data='actions'),
     InlineKeyboardButton(text=f'Отзывы\nи ссылки', callback_data='voices')],
    [InlineKeyboardButton(text='Написать оператору', url='https://t.me/VTGonlinebot')],
    [InlineKeyboardButton(text='История заказов', callback_data='ordhist')]
])

operator_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Написать оператору', url='https://t.me/VTGonlinebot')],
    [InlineKeyboardButton(text='Назад', callback_data='back')]
])

cancel_buy_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='/отмена')]
], resize_keyboard=True)


cancel_change_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='/отменить')]
], resize_keyboard=True)

phone_button_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='/Поделиться_контактом', request_contact=True)]
], resize_keyboard=True)


order_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Отправить заказ', callback_data='order')],
    [InlineKeyboardButton(text='Добавить товар в заказ', callback_data='addorder')],
    [InlineKeyboardButton(text='Удалить товар из заказа', callback_data='delitem')],
    [InlineKeyboardButton(text=f'Изменить количество товаров\nили аренду', callback_data='change')],
    [InlineKeyboardButton(text='Добавить комментарий к заказу', callback_data='comment')],
    [InlineKeyboardButton(text='Удалить заказ', callback_data='delorder')],
    [InlineKeyboardButton(text='Назад', callback_data='back')]
])
