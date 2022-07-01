from aiogram.types import ReplyKeyboardRemove, \
	ReplyKeyboardMarkup, KeyboardButton, \
	InlineKeyboardMarkup, InlineKeyboardButton

button_download_coub   = KeyboardButton('Скачать Coub')
button_music_indentify = KeyboardButton('Музыка с Coub')
button_leader_coub     = KeyboardButton('Лучшие Coub')
button_random_coub     = KeyboardButton('Рандомный Коуб')

markup3 = ReplyKeyboardMarkup(resize_keyboard = True).add(
	button_download_coub
	).add(
		button_music_indentify
		).add(
			button_leader_coub
		).add(
			button_random_coub
		)