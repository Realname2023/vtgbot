from aiogram import types, Router, F
from aiogram.types import FSInputFile
from aiogram.filters import CommandStart, StateFilter
from sqlalchemy.ext.asyncio import AsyncSession
from keyboards.client_kb import kb_client
from data_base.orm_query import orm_add_user, select_action
from foundation import all_commands, b24rest_request, method_list_deals, url_webhook


client_router=Router()


@client_router.message(StateFilter(None), F.text.not_in(all_commands))
async def delete_non_command_messages(message: types.Message):
    await message.delete()


@client_router.message(CommandStart())
async def command_start_handler(message: types.Message, session: AsyncSession) -> None:
    photo = FSInputFile('media/VTG.png')
    parametr_deal_list = {
        'select': ['*', 'UF_*']
    }
    res = await b24rest_request(url_webhook, method_list_deals, parametr_deal_list)
    print(res)
    user = message.from_user
    await orm_add_user(
        session,
        user_id=user.id,
        full_name=user.full_name,
        user_name=user.username,
    )
    
    await message.answer_photo(photo=photo,
                         caption='Здравствуйте. Вы написали в компанию ТОО "ВостокТехГаз". Вы можете оставить вашу заявку  и мы обработаем ее в течение часа.',
                            reply_markup=kb_client)


@client_router.callback_query(F.data=='addres')
async def show_place(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer("Адреса:\nг. Семей, ул. Джангильдина 82/1, район областной больницы\n"
        "https://go.2gis.com/us0av\n"
        "\n"
        "г. Усть-Каменогорск, ул. Абая 181, возле рынка 'Дина'\n"
        "https://go.2gis.com/o9b30v\n"
        "\n"
        "г. Павлодар, ул. Малая объездная 9/1, за ТЦ 'Батырмолл'\n"
        "https://go.2gis.com/hdsq0\n"
        "\n"
        "г. Астана, проспект Абая 99/1, бывшая база ВторЧерМет\n"
        "https://go.2gis.com/xhrt6\n"
        "\n"
        "Контакты:\n"
        "Единый номер: +7 777 954 5000 WhatsApp\n",
                                        reply_markup=kb_client)
    await call.answer()



@client_router.callback_query(F.data=='worktime')
async def show_work_time(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer(
        '                                                            '
        'Семей 08.30 - 17.00,\nУсть-Каменогорск 08.00 - 17.00.\nПавлодар 08.30 - 17.30,\nАстана 08.30 - 17.00',
        reply_markup=kb_client)
    await call.answer()


@client_router.callback_query(F.data=='actions')
async def actions(call: types.CallbackQuery, session: AsyncSession):
    await call.message.edit_reply_markup()
    user = call.from_user.id
    action = await select_action(session=session)
    if action != None:
        await call.message.answer_photo(action.photo, caption=action.text,
                             reply_markup=kb_client)
    else:
        await call.message.answer("Пока никаких акций нет",
                                  reply_markup=kb_client)
    await call.answer()


@client_router.callback_query(F.data=='voices')
async def voices(call: types.CallbackQuery):
    await call.message.edit_reply_markup()
    await call.message.answer("Полезные ссылки:\n"
                              "WhatsApp\n"
                              "https://wa.me/77779545000\n"
                              "Instagram\n"
                              "https://www.instagram.com/vtg_gaz/\n"
                              "email\n"
                              "vostoktehgaz@mail.ru\n"
                              "\n"
                              "Отзывы можно оставить по ссылкам:\n"
                              "Семей:\n"
                              "https://go.2gis.com/us0av\n"
                              "Усть-Каменогорск:\n"
                              "https://go.2gis.com/o9b30v\n"
                              "Павлодар:\n"
                              "https://go.2gis.com/hdsq0\n"
                              "Астана:\n"
                              "https://go.2gis.com/xhrt6",
                              reply_markup=kb_client)
