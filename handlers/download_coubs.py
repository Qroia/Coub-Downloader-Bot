import asyncio
import wget
import os
import time
import json

from utils import States
from create_bot import dp, bot, config, db, collection, collection_opts, collection_theard
from modules_download import download

from mutagen.mp3 import MP3
from emoji import emojize
from aiogram import types, Dispatcher
from aiogram.types import ReplyKeyboardRemove, \
	ReplyKeyboardMarkup, KeyboardButton, \
	InlineKeyboardMarkup, InlineKeyboardButton
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

#@dp.message_handler(state=States.STATE_COUBDOWNLOAD)
async def state_domain_case(message: types.Message):
	class msg:
		id           = message.chat.id
		fromUserID   = message.from_user.id
		messageIdOld = message.message_id + 1
		messageText  = message["text"]

	if 'https://coub.com/view' in msg.messageText:

		if await collection_theard.count_documents({"status": "closed"}) == 0:
			try:
				await collection_theard.insert_one({
					"_id": msg.id,
					"status": "closed"
				})

				await download.downloadCoub(msg)

				ffmpegPath = config["PATH"]["ffmpeg_path"]

				# Чистка данных после запросов
				data_opts = await collection_opts.find_one({"_id": msg.id})
				await bot.delete_message(chat_id = msg.id, message_id = data_opts["message_bot"])

				await bot.send_message(msg.id, 'Начинаем обработку видео 10% /')

				# https://coub.com/view/2y9z7 -> view-source:https://coub.com/coubs/2y9z7c/remix
				originalLink = msg.messageText.replace(" ", "")
				codeFromLink = originalLink[22:]
				GoodLink     = f"view-source:https://coub.com/coubs/{codeFromLink}/remix"

				# Настройка и запуска браузера
				options = webdriver.ChromeOptions()
				options.add_argument(f"user-data-dir={config['PATH']['profile_directory']}")
				options.add_argument("profile-directory=Profile 2")
				# options.headless = True

				# executable_path = config['PATH']['chromedriver_path']
				# service = Service(config['PATH']['chromedriver_path'])
				driver = webdriver.Chrome(service = Service(config['PATH']['chromedriver_path']), options = options)
				driver.get(f"https://coub.com/coubs/{codeFromLink}/remix")
				await asyncio.sleep(15)
				driver.get(GoodLink)

				await bot.edit_message_text(chat_id = msg.id,
									  text = "Обработка видео 20% \\",
									  message_id = msg.messageIdOld)

				# Получение кода страницы
				fullPageText = driver.find_element_by_tag_name("body").text
				pageSource = driver.page_source
				fileToWrite = open("page_source.html", "w", encoding="utf-8")
				fileToWrite.write(pageSource)
				fileToWrite.close()
				fileToRead = open("page_source.html", "r", encoding="utf-8")
				fullPageText = fileToRead.read()
				fileToRead.close()

				await bot.edit_message_text(chat_id = msg.id,
									  text = "Обработка видео 20% /",
									  message_id = msg.messageIdOld)

				# Обрез строки оставляя только ссылку
				start = fullPageText.find('window.source_coub')

				# Проверяем на наличие тегов
				if fullPageText.find('"}]}') == -1:
					end    = fullPageText.find('"tags":[]}')
					addEnd = 10
				else:
					end    = fullPageText.find('"}]}')
					addEnd = 4

				# Обрезка строки до JSON файла
				editOneLink = fullPageText[start+21:end+addEnd]

				# Загрузка editLinkOne в JSON тип и последующее нахождение количество сегментов в объекте
				jsonSource = json.loads(editOneLink) # Загрузка JSON файла
				countSegments = len(jsonSource['finalization_data']['segments']) # Количество сегментов в Coub

				await bot.edit_message_text(chat_id = msg.id,
									  text = "Обработка видео 40% \\ \nСтадия 2",
									  message_id = msg.messageIdOld)

				if countSegments > 1:
					# Скачиваем все видео и сохраняем
					outputInputAddAddress = '' # Адресса направляющие точки входа в один выход(Линейно)
					outputInputAddAddDot  = f'concat=n={countSegments}:v=1:a=1' # Точное определение количество точек входа и перенаправления
					videoNameFiles        = ''
					durationVideo         = 0

					await bot.edit_message_text(chat_id = msg.id,
										  text = "Скачиваем необходимые файлы 50% / \nСтадия 2",
										  message_id = msg.messageIdOld)

					for IntSegment in range(countSegments):	
						try:
							wget.download(jsonSource['finalization_data']['segments'][IntSegment]['cutter_ios'], f'./coubs/{msg.id}_{IntSegment}.mp4')
							outputInputAddAddress = outputInputAddAddress + f'[{IntSegment}:v:0][{IntSegment}:a:0]'
							videoNameFiles        = videoNameFiles + f' -i ./coubs/{msg.id}_{IntSegment}.mp4'
							durationVideo         = durationVideo + jsonSource['finalization_data']['segments'][IntSegment]['cutter_mp4_dashed']['duration']
						except:
							print('Ошибка в Скачивание сегментов')

					# Сшиваем видео в одно
					os.system(f'c:\\ffmpeg\\bin\\ffmpeg.exe{videoNameFiles} -filter_complex "{outputInputAddAddress} {outputInputAddAddDot} [outv] [outa]" -map "[outv]" -map "[outa]" ./coubs/{message.chat.id}_final.mp4')

					# Удаляем использованные сегменты
					for deleteSegmentVideo in range(countSegments):	
						os.remove(f"./coubs/{msg.id}_{deleteSegmentVideo}.mp4")

					# Открывает стандартную страницу коуба
					driver.get(originalLink)

					# Получаем исходный код стандартной страницы
					fullPageText_1 = driver.find_element_by_tag_name("body").text
					pageSource_1 = driver.page_source
					fileToWrite_1 = open("page_source.html", "w", encoding="utf-8")
					fileToWrite_1.write(pageSource_1)
					fileToWrite_1.close()
					fileToRead_1 = open("page_source.html", "r", encoding="utf-8")
					fullPageText_1 = fileToRead_1.read()
					fileToRead_1.close()
					driver.quit()

					await bot.edit_message_text(chat_id = msg.id,
									  text = "Добавляем музыку 70% \\ \nСтадия 2",
									  message_id = msg.messageIdOld)

					# Обрез строки оставляя только ссылку
					start_music       = fullPageText_1.find('"audio":{"high":{"url":"')
					end_music         = fullPageText_1.find('-high.mp3","size":')
					editOneLink_music = fullPageText_1[start_music+24:end_music+9]
					print(editOneLink_music)
					wget.download(editOneLink_music, f'./coubs/{msg.id}_originalmusic.mp3')

					# Получаем начало и конец трека использованного в коубе
					checkDuration = jsonSource['finalization_data']['cutted_audio_data']
					if 'beginning' in checkDuration or 'ending' in checkDuration:
						startMusic, endMusic = jsonSource['finalization_data']['cutted_audio_data']['beginning'], jsonSource['finalization_data']['cutted_audio_data']['ending']
					else:
						startMusic, endMusic = 0, 0

					# Получаем громкость звука, и если он равен 1, то оставляем его таким же
					volumeMusic = jsonSource['finalization_data']['audio_volume']
					if volumeMusic < 1 or volumeMusic > 1:
						os.system(f'{ffmpegPath} -i ./coubs/{msg.id}_originalmusic.mp3 -filter: "volume = {volumeMusic}" -c copy ./coubs/{msg.id}_originalmusic.mp3')

					# Преобразуем startMusic в формат 0:00:00
					finalStartMusic = time.gmtime(startMusic)
					resTimeMusic = time.strftime("%H:%M:%S", finalStartMusic)

					# Так же преобразуем endMusic
					finalEndMusic = time.gmtime(endMusic)
					resEndTimeMusic = time.strftime("%H:%M:%S", finalEndMusic)

					# Получаем количество секунд самого трека
					audio    = MP3(f'./coubs/{msg.id}_originalmusic.mp3')
					audioLen = audio.info.length

					# Получаем realDurationMusic в 0:00:00
					finalRealDurationMusic = time.gmtime(audioLen)
					realDurationMusic = time.strftime("%H:%M:%S", finalRealDurationMusic)

					# Сшиваем музыку с итоговым видео
					# С начала(как в кубах) до конца
					if data_opts["full_loop"] == 1 and data_opts["loop_on_coub"] == 1:

						# Высчитываем формулу по типу: 256/7 = 36.571 -> 37x7(259) -> 259 - 256 = 3
						loopCount, cutClip = int(audioLen / durationVideo + 1), round(int(audioLen / durationVideo + 1) * durationVideo - audioLen, 2)
						
						# Преобразуем в формат 0:00:00
						timeCutCache = time.gmtime(audioLen - cutClip)
						timeCut      = time.strftime("%H:%M:%S", timeCutCache)
						
						# Выполняем ffmpeg команды. 1 - Повторяем лупинг, 2 - добавляем музыку, 3 - обрезаем видео
						os.system(f'{ffmpegPath} -stream_loop {loopCount} -t {audioLen} -i ./coubs/{msg.id}_final.mp4 -c copy ./coubs/{msg.id}_final2.mp4')
						os.system(f'{ffmpegPath} -ss {resTimeMusic} - i ./coubs/{msg.id}_final2.mp4 -t {endMusic - startMusic} -c copy ./coubs/{msg.id}_final2.mp4')
						os.system(f'{ffmpegPath} -ss {resTimeMusic} - i ./coubs/{msg.id}_originalmusic.mp3 -to {resEndTimeMusic} -c copy ./coubs/{msg.id}_originalmusic.mp3')
						os.system(f'{ffmpegPath} -i ./coubs/{msg.id}_final2.mp4 -i "./coubs/{msg.id}_originalmusic.mp3" -map 0:v:0 -map 1:a:0 -y -c copy ./coubs/{msg.id}_by_tgbot_@coubsave_finalrelease.mp4')
	
					# От начала(0) до конца(endMusic)
					if data_opts["full_loop"] == 1 and data_opts["loop_on_coub"] == 2:

						# Высчитываем формулу по типу: 57секунд / 6.45 + 1
						loopCount = int(audioLen / durationVideo + 1)

						# Выполняем ffmpeg команды. 1 - Повторяем лупинг, 2 - добавляем музыку, 3 - обрезаем видео
						os.system(f'{ffmpegPath} -stream_loop {loopCount} -t {audioLen} -i ./coubs/{msg.id}_final.mp4 ./coubs/{msg.id}_final2.mp4')
						os.system(f'{ffmpegPath} -i "./coubs/{msg.id}_final2.mp4" -t {realDurationMusic} -i "./coubs/{msg.id}_originalmusic.mp3" -map 0:v:0 -map 1:a:0 -y ./coubs/{msg.id}_by_tgbot_@coubsave_finalrelease.mp4')

					# От начала(как в кубе), до конца(как в кубе)
					if data_opts["full_loop"] == 2 and data_opts["loop_on_coub"] == 1:

						# Высчитываем формулу по типу: 57секунд / 6.45 + 1
						loopCount = int(audioLen / durationVideo + 1)
						
						# Выполняем ffmpeg команды. 1 - Повторяем лупинг, 2 - добавляем музыку, 3 - обрезаем видео
						os.system(f'{ffmpegPath} -stream_loop {loopCount} -t {audioLen} -i ./coubs/{msg.id}_final.mp4 -c copy ./coubs/{msg.id}_final2.mp4')
						os.system(f'{ffmpegPath} -i "./coubs/{msg.id}_final2.mp4" -ss {resTimeMusic} -t {realDurationMusic} -i "./coubs/{msg.id}_originalmusic.mp3" -map 0:v:0 -map 1:a:0 -y ./coubs/{msg.id}_by_tgbot_@coubsave_finalrelease.mp4')
					
					# стандартное поведение
					if data_opts["full_loop"] == 2 and data_opts["loop_on_coub"] == 2:
						os.system(f'{ffmpegPath} -i "./coubs/{msg.id}_final.mp4" -ss {resTimeMusic} -t {durationVideo} -i "./coubs/{msg.id}_originalmusic.mp3" -map 0:v:0 -map 1:a:0 -y ./coubs/{msg.id}_by_tgbot_@coubsave_finalrelease.mp4')

					# Удаляем ненужные файлы
					os.remove(f"./coubs/{msg.id}_final.mp4")
					os.remove(f"./coubs/{msg.id}_final2.mp4")

					await bot.edit_message_text(chat_id = msg.id,
									  text = "Ещё чуть-чуть 90% / \nСтадия 2",
									  message_id = msg.messageIdOld)

				else:

					await bot.edit_message_text(chat_id = msg.id,
										  text = "Скачиваем необходимые файлы 50% / \nСтадия 2",
										  message_id = msg.messageIdOld)

					# Скачиваем coub
					wget.download(jsonSource['finalization_data']['segments'][0]['cutter_ios'], f'./coubs/{msg.id}_notfinal.mp4')

					# Открывает стандартную страницу коуба
					driver.get(originalLink)

					# Получаем исходный код стандартной страницы
					fullPageText_1 = driver.find_element_by_tag_name("body").text
					pageSource_1 = driver.page_source
					fileToWrite_1 = open("page_source.html", "w", encoding="utf-8")
					fileToWrite_1.write(pageSource_1)
					fileToWrite_1.close()
					fileToRead_1 = open("page_source.html", "r", encoding="utf-8")
					fullPageText_1 = fileToRead_1.read()
					fileToRead_1.close()
					driver.quit()

					# Обрез строки оставляя только ссылку
					start_music       = fullPageText_1.find('"audio":{"high":{"url":"')
					end_music         = fullPageText_1.find('-high.mp3","size":')
					editOneLink_music = fullPageText_1[start_music+24:end_music+9]
					wget.download(editOneLink_music, f'./coubs/{msg.id}_originalmusic.mp3')

					await bot.edit_message_text(chat_id = msg.id,
										  text = "Добавляем музыку 70% \\ \nСтадия 2",
										  message_id = msg.messageIdOld)

					durationVideo = jsonSource['finalization_data']['segments'][0]['cutter_mp4_dashed']['duration']

					# Получаем начало и конец трека использованного в коубе
					try:
						startMusic, endMusic = int(jsonSource['finalization_data']['cutted_audio_data']['beginning']), int(jsonSource['finalization_data']['cutted_audio_data']['ending'])
					except:
						startMusic = 0

					# Преобразуем startMusic в формат 0:00:00
					finalStartMusic = time.gmtime(startMusic)
					resTimeMusic = time.strftime("%H:%M:%S", finalStartMusic)

					checkDuration = jsonSource['finalization_data']['cutted_audio_data']
					if 'beginning' in checkDuration and 'ending' in checkDuration:
						startMusic, endMusic = jsonSource['finalization_data']['cutted_audio_data']['beginning'], jsonSource['finalization_data']['cutted_audio_data']['ending']
					else:
						startMusic = 0


					# Получаем громкость звука, и если он равен 1, то оставляем его таким же
					volumeMusic = jsonSource['finalization_data']['audio_volume']
					if volumeMusic < 1 or volumeMusic > 1:
						os.system(f'{ffmpegPath} -i ./coubs/{msg.id}_originalmusic.mp3 -filter: “volume = {volumeMusic}” ./coubs/{msg.id}_originalmusic.mp3')

					# Преобразуем startMusic в формат 0:00:00
					finalStartMusic = time.gmtime(startMusic)
					resTimeMusic = time.strftime("%H:%M:%S", finalStartMusic)

					# Так же преобразуем endMusic
					finalEndMusic = time.gmtime(endMusic)
					resEndTimeMusic = time.strftime("%H:%M:%S", finalEndMusic)

					# Получаем количество секунд самого трека
					audio    = MP3(f'./coubs/{msg.id}_originalmusic.mp3')
					audioLen = audio.info.length

					# Сшиваем музыку с итоговым видео
					# С начала(как в кубах) до конца
					if data_opts["full_loop"] == 1 and data_opts["loop_on_coub"] == 1:

						# Высчитываем формулу по типу: 256/7 = 36.571 -> 37x7(259) -> 259 - 256 = 3
						loopCount, cutClip = int(audioLen / durationVideo + 1), round(int(audioLen / durationVideo + 1) * durationVideo - audioLen, 2)
						
						# Преобразуем в формат 0:00:00
						timeCutCache = time.gmtime(audioLen - cutClip)
						timeCut      = time.strftime("%H:%M:%S", timeCutCache)
						
						# Выполняем ffmpeg команды. 1 - Повторяем лупинг, 2 - добавляем музыку, 3 - обрезаем видео
						os.system(f'{ffmpegPath} -stream_loop {loopCount} -i ./coubs/{msg.id}_notfinal.mp4 -c copy ./coubs/{msg.id}_final2.mp4')
						asyncio.sleep(2)
						os.system(f'{ffmpegPath} -i "./coubs/{msg.id}_notfinal.mp4" -ss {resTimeMusic} -t {timeCut} -i "./coubs/{msg.id}_originalmusic.mp3" -map 0:v:0 -map 1:a:0 -y ./coubs/{msg.id}_final2.mp4')
						asyncio.sleep(2)
						os.system(f'{ffmpegPath} -ss {resTimeMusic} -i ./coubs/{msg.id}_final2.mp4 -to {timeCut} -c copy ./coubs/{msg.id}_by_tgbot_@coubsave_finalrelease.mp4')
	
					# От начала(0) до конца(endMusic)
					if data_opts["full_loop"] == 1 and data_opts["loop_on_coub"] == 2:

						# Высчитываем формулу по типу: 57секунд / 6.45 + 1
						loopCount = int(endMusic / durationVideo + 1)

						# Выполняем ffmpeg команды. 1 - Повторяем лупинг, 2 - добавляем музыку, 3 - обрезаем видео
						os.system(f'{ffmpegPath} -stream_loop {loopCount} -i ./coubs/{msg.id}_notfinal.mp4 -c copy ./coubs/{msg.id}_final2.mp4')
						os.system(f'{ffmpegPath} -i "./coubs/{msg.id}_notfinal.mp4" -t {resEndTimeMusic} -i "./coubs/{msg.id}_originalmusic.mp3" -map 0:v:0 -map 1:a:0 -y ./coubs/{msg.id}_final2.mp4')
						os.system(f'{ffmpegPath} -i ./coubs/{msg.id}_final2.mp4 -to {resEndTimeMusic} -c copy ./coubs/{msg.id}_by_tgbot_@coubsave_finalrelease.mp4')

					# От начала(как в кубе), до конца(как в кубе)
					if data_opts["full_loop"] == 2 and data_opts["loop_on_coub"] == 1:

						# Высчитываем формулу по типу: 57секунд / 6.45 + 1
						loopCount = int(endMusic / durationVideo + 1)
						
						# Выполняем ffmpeg команды. 1 - Повторяем лупинг, 2 - добавляем музыку, 3 - обрезаем видео
						os.system(f'{ffmpegPath} -stream_loop {loopCount} -i ./coubs/{msg.id}_notfinal.mp4 -c copy ./coubs/{msg.id}_final2.mp4')
						asyncio.sleep(2)
						os.system(f'{ffmpegPath} -i "./coubs/{msg.id}_notfinal.mp4" -ss {resTimeMusic} -t {resEndTimeMusic} -i "./coubs/{msg.id}_originalmusic.mp3" -map 0:v:0 -map 1:a:0 -y ./coubs/{msg.id}_final2.mp4')
						asyncio.sleep(2)
						os.system(f'{ffmpegPath} -ss {resTimeMusic} -i ./coubs/{msg.id}_final2.mp4 -to {resEndTimeMusic} -c copy ./coubs/{msg.id}_by_tgbot_@coubsave_finalrelease.mp4')
					
					# стандартное поведение
					if data_opts["full_loop"] == 2 and data_opts["loop_on_coub"] == 2:
						# Сшиваем музыку с итоговым видео
						os.system(f'{ffmpegPath} -i "./coubs/{msg.id}_notfinal.mp4" -ss {resTimeMusic} -t {durationVideo} -i "./coubs/{msg.id}_originalmusic.mp3" -map 0:v:0 -map 1:a:0 -y ./coubs/{msg.id}_by_tgbot_@coubsave_finalrelease.mp4')


					await bot.edit_message_text(chat_id = msg.id,
									  text = "Ещё чуть-чуть 90% / \nСтадия 2",
									  message_id = msg.messageIdOld)
		
					# Удаляем ненужные файлы
					os.remove(f'./coubs/{msg.id}_notfinal.mp4')
					os.remove(f"./coubs/{msg.id}_final2.mp4")


				await bot.edit_message_text(chat_id = msg.id,
									  text = "Отправка музыки и видео... 100% \\ \nСтадия 3",
									  message_id = msg.messageIdOld)

				# Отправка видео + создание caption

				sizeFileVideo, sizeFileMusic = os.path.getsize(f"./coubs/{msg.id}_by_tgbot_@coubsave_finalrelease.mp4"), os.path.getsize(f"./coubs/{msg.id}_originalmusic.mp3")

				if sizeFileVideo >= 52428800 or sizeFileMusic >= 52428800:
					await bot.send_message(msg.id, "ОШИБКА! \nФайл кубов или музыки превышает лимит Телеграма(Читать здесь) в 50МБ, выберите другие параметры в начале скачивания или подождите немного, в будущем мы добавим возможность отправки больших файлов")
				else:
					caption       = "@dwhat_team | @coubsave_bot (CoubSave)"
					caption_music = "Для определения нвазвания музыки вы можете выбрать кнопку 'Инфо Музыка'\n\n@dwhat_team | @coubsave_bot (CoubSave)"
					with open(f'./coubs/{msg.id}_by_tgbot_@coubsave_finalrelease.mp4', 'rb') as video:
						await bot.send_video(message.from_user.id, video,
											 caption=emojize(caption),
											 reply_to_message_id=message.message_id)

				await collection_theard.delete_one({
					"_id": msg.id
				})

				# Отправка музыки
				with open(f"./coubs/{msg.id}_originalmusic.mp3", "rb") as music:
					await bot.send_audio(msg.fromUserID, music,
										caption = caption_music,
										performer = "Наш сайт dwhat.su",
										title = "@coubsave_bot")

				# Удаление остаточных файлов
				os.remove(f"./coubs/{msg.id}_originalmusic.mp3")
				os.remove(f"./coubs/{msg.id}_by_tgbot_@coubsave_finalrelease.mp4")

				# Выходим из стадии
				state = dp.current_state(user = msg.fromUserID)
				await state.reset_state()

				# Чистка первоначальных настроек
				await collection_opts.delete_one({"_id": msg.id})
		
			except:
				try:
					if await collection_theard.count_documents({"_id": msg.id}) >= 1:
						await collection_theard.delete_one({
							"_id": msg.id
						})
					driver.quit()
					# Выходим из стадии
					state = dp.current_state(user = msg.fromUserID)
					await state.reset_state()
				except:
					# Выходим из стадии
					state = dp.current_state(user = msg.fromUserID)
					await state.reset_state()
	
		else:
			await bot.send_message(msg.id, "Извините, сейчас все потоки заняты, попробуйте через 5-20 секунд.")
			# Выходим из стадии
			state = dp.current_state(user = msg.fromUserID)
			await state.reset_state()
	
	else:
		await bot.send_message(msg.id, 'Ссылка неверна')

		state = dp.current_state(user = msg.fromUserID)
		await state.reset_state()

#@dp.callback_query_handler(func=lambda c: c.data and c.data.startswith('opts'))
async def process_callback_setopts(callback_query: types.CallbackQuery):
	opts = callback_query.data[4:]

	class call_data:
		userId = callback_query.from_user.id

	if opts == 'full_loop':
		if await collection_opts.count_documents({"_id": call_data.userId}) >= 1:
			data = await collection_opts.find_one({"_id": call_data.userId})

			if data["loop_on_coub"] == 1:
				inline_kb_download_opts_loop_on_coub = InlineKeyboardButton('Цикл как в Coub ✅', callback_data = 'optsloop_on_coub')
			elif data["loop_on_coub"] == 2:
				inline_kb_download_opts_loop_on_coub = InlineKeyboardButton('Цикл как в Coub', callback_data = 'optsloop_on_coub')

			if data["full_loop"] == 2:
				inline_kb_download_opts_full_loop = InlineKeyboardButton('Полный Цикл ✅', callback_data = 'optsfull_loop')
				await collection_opts.update_one({"_id": call_data.userId}, {"$set": {"full_loop": 1}})
				await callback_query.answer("Включен")
			elif data["full_loop"] == 1:
				inline_kb_download_opts_full_loop = InlineKeyboardButton('Полный Цикл', callback_data = 'optsfull_loop')
				await collection_opts.update_one({"_id": call_data.userId}, {"$set": {"full_loop": 2}})
				await callback_query.answer("Выключен")

			data = await collection_opts.find_one({"_id": call_data.userId})

			if data["full_loop"] == 2 and data["loop_on_coub"] == 2:
				inline_kb_download_opts_pass = InlineKeyboardButton('Пропустить', callback_data = 'optsgo')
			else:
				inline_kb_download_opts_pass = InlineKeyboardButton('Продолжить', callback_data = 'optsgo')
			inline_kb_download_opts_back = InlineKeyboardButton('Отмена', callback_data = 'optsback')

			inline_kb_opts = InlineKeyboardMarkup(row_width = 2)
			inline_kb_opts.add(inline_kb_download_opts_full_loop)
			inline_kb_opts.add(inline_kb_download_opts_loop_on_coub)
			inline_kb_opts.add(inline_kb_download_opts_pass)
			inline_kb_opts.add(inline_kb_download_opts_back)
		
			await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text = 'Выберите параметры, нажмите Пропустить/Продолжить, после чего вы сможете скачать Coub', reply_markup = inline_kb_opts)
		else:
			await callback_query.answer('Недоступно')

	elif opts == 'loop_on_coub':

		if await collection_opts.count_documents({"_id": call_data.userId}) >= 1:
			data = await collection_opts.find_one({"_id": call_data.userId})

			if data["full_loop"] == 1:
				inline_kb_download_opts_full_loop = InlineKeyboardButton('Полный Цикл ✅', callback_data = 'optsfull_loop')
			elif data["full_loop"] == 2:
				inline_kb_download_opts_full_loop = InlineKeyboardButton('Полный Цикл', callback_data = 'optsfull_loop')

			if data["loop_on_coub"] == 2:
				inline_kb_download_opts_loop_on_coub = InlineKeyboardButton('Цикл как в Coub ✅', callback_data = 'optsloop_on_coub')
				await collection_opts.update_one({"_id": call_data.userId}, {"$set": {"loop_on_coub": 1}})
				await callback_query.answer("Включен")
			elif data["loop_on_coub"] == 1:
				inline_kb_download_opts_loop_on_coub = InlineKeyboardButton('Цикл как в Coub', callback_data = 'optsloop_on_coub')
				await collection_opts.update_one({"_id": call_data.userId}, {"$set": {"loop_on_coub": 2}})
				await callback_query.answer("Выключен")

			data = await collection_opts.find_one({"_id": call_data.userId})

			if data["full_loop"] == 2 and data["loop_on_coub"] == 2:
				inline_kb_download_opts_pass = InlineKeyboardButton('Пропустить', callback_data = 'optsgo')
			else:
				inline_kb_download_opts_pass = InlineKeyboardButton('Продолжить', callback_data = 'optsgo')
			inline_kb_download_opts_back = InlineKeyboardButton('Отмена', callback_data = 'optsback')

			inline_kb_opts = InlineKeyboardMarkup(row_width = 2)
			inline_kb_opts.add(inline_kb_download_opts_full_loop)
			inline_kb_opts.add(inline_kb_download_opts_loop_on_coub)
			inline_kb_opts.add(inline_kb_download_opts_pass)
			inline_kb_opts.add(inline_kb_download_opts_back)
		
			await bot.edit_message_text(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id, text = 'Выберите параметры, нажмите Пропустить/Продолжить, после чего вы сможете скачать Coub', reply_markup = inline_kb_opts)
		else:
			await callback_query.answer('Недоступно')

	elif opts == 'back':
		await callback_query.answer("Отменено")
		await collection_opts.delete_one({"_id": call_data.userId})
		await callback_query.message.delete()

	elif opts == 'go':
		if await collection_theard.count_documents({"status": "closed"}) == 0:
			await collection_opts.update_one({"_id": call_data.userId}, {"$set": {"message_bot": callback_query.message.message_id}})
			await bot.send_message(call_data.userId, 'Отправьте ссылку в виде \nhttps://coub.com/view/2y9z7')
			state = dp.current_state(user=call_data.userId)
			await state.set_state(States.all()[0])
		else:
			await bot.send_message(call_data.userId, "Извините, сейчас все потоки заняты, попробуйте через 5-20 секунд.")
			# Выходим из стадии
			state = dp.current_state(user = call_data.userId)
			await state.reset_state()

def register_handlers_download_coubs(dp: Dispatcher):
	dp.register_message_handler(state_domain_case, state = States.STATE_COUBDOWNLOAD)
	dp.register_callback_query_handler(process_callback_setopts, lambda c: c.data and c.data.startswith('opts'))