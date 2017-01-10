import telebot
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
token_id = config['Telegram']['token_id']
link = config['Telegram']['link']
login_link = config['Telegram']['login_link']
register_link = 'https://authb.agoraus1.egc.duckdns.org/register.php'
public_key = ''
recuento_api = 'https://beta.recuento.agoraus1.egc.duckdns.org/api'

bot = telebot.TeleBot(token_id)

sesion = {}