# coding: utf8
import time
import json
import os
import random
import configparser

import wget

from selenium import webdriver

# Читаем парсерингом настройки
# Использование config["PATH"][""]
config = configparser.ConfigParser()
config.read("settings.ini") 

originalLink = input("Введите ссылку")
GoodLink = f"view-source:https://coub.com/coubs/{originalLink[22:]}/remix"

# Настройка и запуска браузера
options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=C:\\Users\\andro\\AppData\\Local\\Google\\Chrome\\User Data")
options.add_argument("profile-directory=Profile 2")
driver = webdriver.Chrome(executable_path = r'D:\Projects\Python\Telegram\SaveCoubs\chromedriver.exe', options = options)
driver.get(f"https://coub.com/coubs/{originalLink[22:]}/remix")
time.sleep(6)
driver.get(GoodLink)

# Получение кода страницы
fullPageText = driver.find_element_by_tag_name("body").text
pageSource = driver.page_source
fileToWrite = open("page_source.html", "w", encoding="utf-8")
fileToWrite.write(pageSource)
fileToWrite.close()
fileToRead = open("page_source.html", "r", encoding="utf-8")
fullPageText = fileToRead.read()
fileToRead.close()

# Обрез строки оставляя только ссылку
start = fullPageText.find('window.source_coub')
end = fullPageText.find('"}]}')
editOneLink = fullPageText[start+21:end+4]

# Загрузка editLinkOne в JSON тип и последующее нахождение количество сегментов в объекте
jsonSource = json.loads(editOneLink) # Загрузка JSON файла
countSegments = len(jsonSource['finalization_data']['segments']) # Количество сегментов в Coub
print(countSegments)

id_user = random.randint(1412341, 425254534) # Тестовое рандомное ID

if countSegments > 1:
	# Скачиваем все видео и сохраняем
	outputInputAddAddress = '' # Адресса направляющие точки входа в один выход(Линейно)
	outputInputAddAddDot  = f'concat=n={countSegments}:v=1:a=1' # Точное определение количество точек входа и перенаправления
	videoNameFiles        = ''
	durationVideo         = 0

	for IntSegment in range(countSegments):
		try:
			print(f"{IntSegment}ый сегмент скачался")
			wget.download(jsonSource['finalization_data']['segments'][IntSegment]['cutter_ios'], f'./coubs/{id_user}_{IntSegment}.mp4')
			outputInputAddAddress = outputInputAddAddress + f'[{IntSegment}:v:0][{IntSegment}:a:0]'
			videoNameFiles        = videoNameFiles + f' -i ./coubs/{id_user}_{IntSegment}.mp4'
			durationVideo         = durationVideo + jsonSource['finalization_data']['segments'][IntSegment]['cutter_mp4_dashed']['duration']
		except:
			print('Ошибка в Скачивание сегментов')

	# Сшиваем видео в одно
	os.system(f'c:\\ffmpeg\\bin\\ffmpeg.exe{videoNameFiles} -filter_complex "{outputInputAddAddress} {outputInputAddAddDot} [outv] [outa]" -map "[outv]" -map "[outa]" ./coubs/{id_user}_final.mp4')

	# Удаляем использованные сегменты
	for deleteSegmentVideo in range(countSegments):
		os.remove(f"./coubs/{id_user}_{deleteSegmentVideo}.mp4")

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
	print(editOneLink_music)
	wget.download(editOneLink_music, f'./coubs/{id_user}_originalmusic.mp3')

	# Получаем начало и конец трека использованного в коубе
	try:
		startMusic, endMusic = int(jsonSource['finalization_data']['cutted_audio_data']['beginning']), int(jsonSource['finalization_data']['cutted_audio_data']['ending'])
	except:
		startMusic = 0

	# Преобразуем startMusic в формат 0:00:00
	finalStartMusic = time.gmtime(startMusic)
	resTimeMusic = time.strftime("%H:%M:%S", finalStartMusic)

	# Сшиваем музыку с итоговым видео
	os.system(f'c:\\ffmpeg\\bin\\ffmpeg.exe -i "./coubs/{id_user}_final.mp4" -ss {resTimeMusic} -t {durationVideo} -i "./coubs/{id_user}_originalmusic.mp3" -map 0:v:0 -map 1:a:0 -y ./coubs/{id_user}_by_tgbot_@coubsave_finalrelease.mp4')



else:
	# Скачиваем музыку
	wget.download(jsonSource['finalization_data']['segments'][0]['cutter_ios'], f'./coubs/{id_user}_notfinal.mp4')

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
	print(editOneLink_music)
	wget.download(editOneLink_music, f'./coubs/{id_user}_originalmusic.mp3')

	# Получаем начало и конец трека использованного в коубе
	try:
		startMusic, endMusic = int(jsonSource['finalization_data']['cutted_audio_data']['beginning']), int(jsonSource['finalization_data']['cutted_audio_data']['ending'])
	except:
		startMusic = 0

	# Преобразуем startMusic в формат 0:00:00
	finalStartMusic = time.gmtime(startMusic)
	resTimeMusic = time.strftime("%H:%M:%S", finalStartMusic)

	durationVideo = jsonSource['finalization_data']['segments'][0]['cutter_mp4_dashed']['duration']

	# Сшиваем музыку с итоговым видео
	os.system(f'c:\\ffmpeg\\bin\\ffmpeg.exe -i "./coubs/{id_user}_notfinal.mp4" -ss {resTimeMusic} -t {durationVideo} -i "./coubs/{id_user}_originalmusic.mp3" -map 0:v:0 -map 1:a:0 -y ./coubs/{id_user}_by_tgbot_@coubsave_finalrelease.mp4')
