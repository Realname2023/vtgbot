import aiohttp
from os import getenv
from aiogram.fsm.storage.redis import RedisStorage
from aioredis import Redis
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())



TOKEN = str(getenv("TOKEN"))

# storage = RedisStorage.from_url('redis://localhost:6379/0')

# redis = Redis()

redis = Redis.from_url(str(getenv('REDIS_URL')))

# redis = Redis.from_url('redis://localhost:6379/0')

storage = RedisStorage(redis=redis)

all_commands = ['/отмена', '/отменить', '/start', '/stop', '/Поделиться_контактом']
# ALLOWED_UPDATES=['message', 'callback_query']
url_webhook = 'https://vostoktekhgaz.bitrix24.kz/rest/1/wwkcsklhii78b1r5/'
method_deal_add = 'crm.deal.add'
method_contact_update = 'crm.contact.update'
method_products_set = 'crm.deal.productrows.set'
method_contact_list = 'crm.contact.list'
method_contact_add = 'crm.contact.add'


async def b24rest_request(url_webhook: str, method: str, parametr: dict) -> dict:
    url = url_webhook + method + '.json?'
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=parametr) as response:
            response_data = await response.json()
            if response.status == 200:
                # Запрос выполнен успешно
                print(f"Ответ сервера: {response_data}")
            else:
                print(f"Ошибка при выполнении запроса. Статус код: {response_data}") 
    return response_data

