import telebot
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
token_id = config['Telegram']['token_id']
link = config['Telegram']['link']
login_link = config['Telegram']['login_link']

bot = telebot.TeleBot(token_id)

sesion = {}