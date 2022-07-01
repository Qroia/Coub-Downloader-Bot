import datetime
import requests

import keyboards as kb
from utils import States
from create_bot import dp, bot, db, collection, collection_opts, log_write, config

from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardRemove, \
	ReplyKeyboardMarkup, KeyboardButton, \
	InlineKeyboardMarkup, InlineKeyboardButton

#@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
	msg_id = message.chat.id

	await bot.send_message(msg_id, 'CoubSave - бесплатный телеграм бот для скачивания Coubs из сервиса coub.com.\n\nДоп функции: \nЛидерские Coubs\nРаспознавание Музыки', reply_markup = kb.markup3)
	if await db.users.count_documents({"_id": msg_id}) >= 1:
		pass
	else:
		await log_write('+1 User', 'info', "general")
		await collection.insert_one({
			"_id": msg_id,
			"data_reg": datetime.datetime.now()
		})

#@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
	await bot.send_message(message.chat.id, 'Скоро')

#@dp.message_handler(content_types=['text'])
async def process_text_message(message: types.Message):
	class msg:
		id          = message.chat.id
		messageText = message['text']
		fromUserID  = message.from_user.id

	if msg.messageText == 'Скачать Coub':

		count_userActive_kb = await collection_opts.count_documents({"_id": msg.id})

		if count_userActive_kb == 0:

			inline_kb_download_opts_full_loop     = InlineKeyboardButton('Полный Цикл', callback_data = 'optsfull_loop')
			inline_kb_download_opts__loop_on_coub = InlineKeyboardButton('Цикл как в Coub', callback_data = 'optsloop_on_coub')
			inline_kb_download_opts_pass          = InlineKeyboardButton('Пропустить', callback_data = 'optsgo')
			inline_kb_download_opts_back          = InlineKeyboardButton('Отмена', callback_data = 'optsback')

			inline_kb_download_options = InlineKeyboardMarkup(row_width = 2)
			inline_kb_download_options.add(inline_kb_download_opts_full_loop)
			inline_kb_download_options.add(inline_kb_download_opts__loop_on_coub)
			inline_kb_download_options.add(inline_kb_download_opts_pass)
			inline_kb_download_options.add(inline_kb_download_opts_back)

			await collection_opts.insert_one({
				"_id": msg.id,
				"full_loop": 2,
				"loop_on_coub": 2,
				"message_bot": 0
			})

			await bot.send_message(msg.id, 'Выберите параметры, нажмите Пропустить/Продолжить, после чего вы сможете скачать Coub', reply_markup = inline_kb_download_options)

		else:
			await bot.send_message(msg.id, 'Вы уже на подходе к загрузке где-то выше)')

	elif msg.messageText == 'Музыка с Coub':
		await bot.send_message(msg.id, 'Распознование музыки с любого coub и быстрое скачивание\n1. Отправь ссылку на coub(Формат ссылки: https://coub.com/view/2y9z7)\n2.Получи результат: Название + Файл\n\n*Важно знать:\nCoubSave не может распознать музыку нескольких типов: Remix-Версии(40%), Самописные(83%)')

		state = dp.current_state(user = msg.fromUserID)
		await state.set_state(States.all()[1])
	elif msg.messageText == 'Лучшие Coub':
		await bot.send_message(msg.id, 'Лучшие Coubs недели(10)')

		state = dp.current_state(user = msg.fromUserID)
		await state.set_state(States.all()[2])
	elif msg.messageText == 'Рандомный Коуб':
		response = requests.get('http://coub.com/api/v2/timeline/explore/random?per_page=10')
		await bot.send_message(message.chat.id, f'{response.status_code}')
		reqResult = response.json()

		if response:
			inline_kb_random_coub_0 = InlineKeyboardButton(reqResult['coubs'][0]['title'], callback_data = f"rcb{reqResult['coubs'][0]['permalink']}")
			inline_kb_random_coub_1 = InlineKeyboardButton(reqResult['coubs'][1]['title'], callback_data = f"rcb{reqResult['coubs'][1]['permalink']}")
			inline_kb_random_coub_2 = InlineKeyboardButton(reqResult['coubs'][2]['title'], callback_data = f"rcb{reqResult['coubs'][2]['permalink']}")
			inline_kb_random_coub_3 = InlineKeyboardButton(reqResult['coubs'][3]['title'], callback_data = f"rcb{reqResult['coubs'][3]['permalink']}")
			inline_kb_random_coub_4 = InlineKeyboardButton(reqResult['coubs'][4]['title'], callback_data = f"rcb{reqResult['coubs'][4]['permalink']}")
			inline_kb_random_coub_5 = InlineKeyboardButton(reqResult['coubs'][5]['title'], callback_data = f"rcb{reqResult['coubs'][5]['permalink']}")
			inline_kb_random_coub_6 = InlineKeyboardButton(reqResult['coubs'][6]['title'], callback_data = f"rcb{reqResult['coubs'][6]['permalink']}")
			inline_kb_random_coub_7 = InlineKeyboardButton(reqResult['coubs'][7]['title'], callback_data = f"rcb{reqResult['coubs'][7]['permalink']}")
			inline_kb_random_coub_8 = InlineKeyboardButton(reqResult['coubs'][8]['title'], callback_data = f"rcb{reqResult['coubs'][8]['permalink']}")
			inline_kb_random_coub_9 = InlineKeyboardButton(reqResult['coubs'][9]['title'], callback_data = f"rcb{reqResult['coubs'][9]['permalink']}")
			inline_kb_random_coubs = InlineKeyboardMarkup(row_width=2)
			inline_kb_random_coubs.add(inline_kb_random_coub_0, inline_kb_random_coub_1, inline_kb_random_coub_2)
			inline_kb_random_coubs.row(inline_kb_random_coub_0, inline_kb_random_coub_1, inline_kb_random_coub_2)
			inline_kb_random_coubs.add(inline_kb_random_coub_3, inline_kb_random_coub_4, inline_kb_random_coub_5)
			inline_kb_random_coubs.row(inline_kb_random_coub_3, inline_kb_random_coub_4, inline_kb_random_coub_5)
			inline_kb_random_coubs.add(inline_kb_random_coub_6, inline_kb_random_coub_7, inline_kb_random_coub_8)
			inline_kb_random_coubs.row(inline_kb_random_coub_6, inline_kb_random_coub_7, inline_kb_random_coub_8)
			inline_kb_random_coubs.add(inline_kb_random_coub_9)

			await bot.send_message(message.chat.id, "10 Рандомных Коубов", reply_markup=inline_kb_random_coubs)

# Симуляция стадий
#@dp.message_handler(state='*', commands=['setstate'])
async def process_setstate_command(message: types.Message):
	argument = message.get_args()
	state = dp.current_state(user=message.from_user.id)
	if not argument:
		await state.reset_state()
		return await message.reply('Состояние успешно сброшено')

	if (not argument.isdigit()) or (not int(argument) < len(States.all())):
		return await message.reply('Состояние успешно сброшено'.format(key=argument))

	await state.set_state(States.all()[int(argument)])

#dp.message_handler(commands = ['getlog'])
async def process_getlog_command(message: types.Message):
	if message.chat.id == int(config['ADMINS']['admin_penidze']):
		with open('logger.log', 'rb') as filelog:
			await bot.send_document(message.chat.id, filelog, caption = 'Файл логов')
	else:
		await bot.send_message(message.chat.id, 'У вас нет доступа к команде')

#dp.message_handler(commands = ['resetlog])
async def process_resetlog_command(message: types.Message):
	if message.chat.id == int(config['ADMINS']['admin_penidze']):
		open('logger.log', 'w').close()
		await bot.send_message(message.chat.id, 'Файл очищен')
		await log_write('Файл Очищен', 'info', False)
	else:
		await bot.send_message(message.chat.id, 'У вас нет доступа к команде')

def register_handlers_general(dp: Dispatcher):
	dp.register_message_handler(process_start_command, commands=['start'])
	dp.register_message_handler(process_help_command, commands=['help'])
	dp.register_message_handler(process_getlog_command, commands = ['getlogs'])
	dp.register_message_handler(process_resetlog_command, commands = ['resetlog'])
	dp.register_message_handler(process_text_message, content_types=['text'])
	dp.register_message_handler(process_setstate_command, state='*', commands=['setstate'])