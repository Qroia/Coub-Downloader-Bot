import configparser
import motor.motor_asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# Читаем парсерингом настройки
# Использование config["PATH"][""]
config = configparser.ConfigParser()
config.read("settings.ini") 

# Инцилизация Бота
bot = Bot(token=config["TOKEN"]["token_bot"])
dp = Dispatcher(bot, storage=MemoryStorage())

# Подключение Базы данных (Общая ссылка)
#db                = MongoClient(config["DATABASE_PARAMETRS"]["uri"])[config["DATABASE_PARAMETRS"]["cluster_name"]] - Синхронное подключение
client            = motor.motor_asyncio.AsyncIOMotorClient(config["DATABASE_PARAMETRS"]["uri"])
db                = client[config["DATABASE_PARAMETRS"]["cluster_name"]]
collection        = db["users"]
collection_theard = db["theard"]
collection_opts   = db["opts"]

# Логгирование
logging.basicConfig(
	filename ='logger.log',
	level    = logging.INFO,
	format   = "%(asctime)s - %(levelname)s - %(message)s",
	datefmt  ='%H:%M:%S',
)

async def log_write(message, type, module):
	if module != False:
		logging.basicConfig(
			format = '%(asctime)s - %(levelname)s' + f'- {module} -' + '%(message)s'
		)
	if type == 'debug':
		logging.debug(message)
	elif type == 'info':
		logging.info(message)
	elif type == 'warning':
		logging.warning(message)
	elif type == 'error':
		logging.error(message)
	elif type == 'critical':
		logging.critical(message)