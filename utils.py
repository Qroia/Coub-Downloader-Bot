from aiogram.utils.helper import Helper, HelperMode, ListItem


class States(Helper):
	mode = HelperMode.snake_case

	STATE_COUBDOWNLOAD  = ListItem()
	STATE_IDENTIFYMUSIC = ListItem()
	STATE_LEADERCOUBS   = ListItem()
	STATE_RANDOMCOUB    = ListItem()

if __name__ == '__main__':
	print(States.all())