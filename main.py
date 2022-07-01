from create_bot import dp, bot, config
from handlers import download_coubs, general, leader_coub, random_coub, identify_music

from aiogram import Dispatcher
from aiogram.utils import executor

async def on_startup(_):
	print('Bot Startup')
	await bot.send_message(int(config['ADMINS']['admin_penidze']), 'Бот запущен')

download_coubs.register_handlers_download_coubs(dp)
leader_coub.register_handlers_leader_coub(dp)
random_coub.register_handlers_random_coubs(dp)
identify_music.register_handlers_identify_music(dp)
general.register_handlers_general(dp)

async def shutdown(dispatcher: Dispatcher):
	await dispatcher.storage.close()
	await dispatcher.storage.wait_closed()

if __name__ == '__main__':
	executor.start_polling(dp, on_shutdown=shutdown, on_startup = on_startup)