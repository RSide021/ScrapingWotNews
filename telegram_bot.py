import asyncio
import json

from aiogram import Bot, Dispatcher, executor, types
from auth_data import token
from aiogram.utils.markdown import hbold, hunderline, hcode, hlink
from main import check_news_update, load_all_news_from_page
from aiogram.dispatcher.filters import Text
import logging

logging.basicConfig(level=logging.INFO)

bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


@dp.message_handler(commands="start")
async def start(message: types.Message):
    user_id = message.from_id

    check_user_id(user_id)
    start_buttons = ["Последние новости", "Проверить обновления"]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)

    await message.answer("Лента новостей", reply_markup=keyboard)
    await message.reply("Приветствую!")


@dp.message_handler(Text(equals="Последние новости"))
async def get_all_news(message: types.Message):
    load_all_news_from_page()
    news_dict = get_dict_news()
    for key, value in reversed(news_dict.items()):
        news = f"{hunderline(value['card_date'])}\n\n" \
               f"{hlink(value['card_title'], value['card_href'])}"
        await message.answer(news)


@dp.message_handler(Text(equals="Проверить обновления"))
async def get_all_news(message: types.Message):
    fresh_news = check_news_update()

    if is_news_available(fresh_news):
        for key, value in reversed(fresh_news.items()):
            news = create_block_news(value)
            await message.answer(news)
    else:
        await message.answer("Пока нет свежих новостей...")


def check_user_id(user_id):
    users_id_info = get_users_id_info()
    if user_id not in users_id_info:
        users_id_info[user_id] = user_id
        write_users_id_info(users_id_info)


def get_users_id_info():
    with open("users_id_info.json", encoding="utf-8") as file:
        return json.load(file)


def write_users_id_info(users_id_info):
    with open("users_id_info.json", "w", encoding="utf-8") as file:
        json.dump(users_id_info, file, indent=4, ensure_ascii=False)


def get_dict_news():
    with open("news_dict.json", encoding="utf-8") as file:
        return json.load(file)


async def news_every_hour():
    while True:
        fresh_news = check_news_update()

        if is_news_available(fresh_news):
            for key, value in reversed(fresh_news.items()):
                news = create_block_news(value)
                await send_news_all_users(news)
        await asyncio.sleep(3600)


def is_news_available(fresh_news):
    return len(fresh_news) >= 1


def create_block_news(value):
    return f"{hunderline(value['card_date'])}\n\n" \
           f"{hlink(value['card_title'], value['card_href'])}"


async def send_news_all_users(news):
    users_id = get_users_id_info()
    for key_user, value_user in users_id.items():
        await bot.send_message(value_user, news, disable_notification=True)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(news_every_hour())
    executor.start_polling(dp)
