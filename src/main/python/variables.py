import telebot
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
token_id = config['Telegram']['token_id']
link = config['Telegram']['link']
login_link = config['Telegram']['login_link']
register_link = 'https://authb.agoraus1.egc.duckdns.org/register.php'
public_key = ''
recuento_api = 'https://recuento.agoraus1.egc.duckdns.org/api'
censos_api = 'https://beta.censos.agoraus1.egc.duckdns.org/census/'
jar_sha = ''

bot = telebot.TeleBot(token_id)

sesion = {}