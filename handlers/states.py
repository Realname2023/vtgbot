from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup


class CategoryFactory(CallbackData, prefix="sel"):
    cat: str


class BuyItem(CallbackData, prefix="buy"):
    id: int


class DeleteItem(CallbackData, prefix="del"):
    good_id: int


class NewQuant(CallbackData, prefix="new"):
    good_id: int


class OrderHist(CallbackData, prefix="ord"):
    id: int


class FSMBuy(StatesGroup):
    buy_item_id = State()
    buy_b_id = State()
    item = State()
    buy_verbosename = State()
    buy_price = State()
    buy_is_arenda = State()
    buy_quantity = State()
    buy_arenda_time = State()
    buy_unit = State()
    city = State()
    org_name = State()
    address = State()
    phone = State()


class FSMOrder(StatesGroup):
    comment = State()
    new_quantity = State()
    new_arenda_time = State()
    order_item_id = State()
    order_is_arenda = State()
