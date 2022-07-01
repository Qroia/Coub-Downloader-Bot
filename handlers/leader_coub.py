import wget
from utils import States

from create_bot import dp, bot, config, db, collection, collection_theard

from emoji import emojize
from aiogram import types, Dispatcher
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

#@dp.message_handler(state=States.STATE_LEADERCOUBS)
async def state_get_leader_coubs(message: types.Message):
	...

def register_handlers_leader_coub(dp: Dispatcher):
    dp.register_message_handler(state_get_leader_coubs, state=States.STATE_LEADERCOUBS)