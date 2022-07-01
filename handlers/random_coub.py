import wget
from utils import States

from create_bot import bot,  log_write

from emoji import emojize
from aiogram import types, Dispatcher

#@dp.message_handler(state=States.STATE_RANDOMCOUB)
async def state_random_coubs(message: types.Message):
	...

#@dp.callback_query_handler(func=lambda c: c.data and c.data.startswith('rcb'))
async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
    permalink = callback_query.data[3:]
    await bot.send_message(callback_query.from_user.id, f'https://coub.com/view/{permalink}')

def register_handlers_random_coubs(dp: Dispatcher):
	dp.register_message_handler(state_random_coubs, state=States.STATE_RANDOMCOUB)
	dp.register_callback_query_handler(process_callback_kb1btn1, lambda c: c.data and c.data.startswith('rcb'))