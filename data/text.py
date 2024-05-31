from web3 import Web3
from core.logger_config import logger, PROJECT_NAME
import requests

from core.database.database_main import table_channels

CMD_START = 'start'
CMD_MENU = 'menu'
CMD_HELP = 'help'
CMD_ADD_CHANNEL = 'addchannel'
CMD_DEL_CHANNEL = 'delchannel'
CMD_SEND_MSG = 'sendmsg'

CMD_CLIENT = [CMD_MENU, CMD_START, CMD_HELP]
CMD_ADMIN = [CMD_DEL_CHANNEL, CMD_ADD_CHANNEL, CMD_SEND_MSG]

INTERVALS = {}

RUS = 'RUS'

MSG = {
    RUS: {
        'CLIENT': {
            'HELP': '*При возникновении неполадок с Ботом обращайтесь в '
                    'техническую поддержку: @wndrflp*'
        },
        'ADMIN': {
            'SEND_MSG': {
                'INPUT': 'Пришлите *пост*, который вы хотите разослать всем пользователям:',
                'CHECK': '*Проверьте пост на корректность!*\n'
                         '\n'
                         'Вы уверены, что хотите отправить этот пост всем пользователям бота?\n'
            },
            'CHANNEL': {
                'ADD': '*Пришлите id или @тег канала, который хотите добавить.*\n(предварительно выдайте Боту права '
                       'администратора в этом канале)',
                'DEL': '*Выберите канал из списка, который хотите удалить*'
            },
            'HELP': f'*Инструкция (админ):*\n'
                    f'\n'
                    f'Добавить новый обязательный для подписки канал:\n'
                    f'/{CMD_ADD_CHANNEL}\n'
                    f'\n'
                    f'Удалить обязательный для подписки канал:\n'
                    f'/{CMD_DEL_CHANNEL}\n'
                    f'\n'
                    f'Отправить сообщение всем пользователям:\n'
                    f'/{CMD_SEND_MSG}\n'
                    f'\n'
        },
        'SETTINGS': {
            'MENU': f'*Привет, это меню {PROJECT_NAME}!*\n'
                    f'\n'
                    f'Здесь Вы можете регулировать работу бота.',
            'INTERVAL': '*Выберите интервал, с которым Вы будете получать информацию о цене газа в сети:*',
            'STOP': 'Бот остановлен!',
            'START': 'Бот снова работает!'
        },
        'SUB': {
            'CLOSED': f'*Доступ к боту был закрыт.*',
            'OPENED': '*Доступ к Боту был открыт!\n\nБот присылает текущую стоимость газа в сети '
                      'ETH. Можете регулировать интервал рассылки или остановить работу Бота в '
                      '/menu.*',
        },

        'NO_ROOTS': 'У вас нет прав на использование этой команды',
        'OTHER': 'Такой команды не существует, чтобы настроить бота вызовите /menu.'

    }
}

BUTTONS = {
    'INTERVAL': 'Интервалы',
    'TURN': {
        'ON': 'Включить',
        'OFF': 'Выключить'
    }
}


def get_msg_channels_to_subscribe():
    channels = ''
    i = 1
    for tag in table_channels.get_channel_tags():
        channels += f'{i}. ' + 'https://t.me/' + tag + '\n'
    msg = f'*Для использования бота необходимо быть подписанным на следующие каналы: \n\n{channels}*'
    return msg


def get_msg_gas_price():
    prices = get_price()

    con_web3 = Web3(provider=Web3.HTTPProvider(endpoint_uri='https://rpc.ankr.com/eth'))
    gas = round(con_web3.eth.gas_price / 10 ** 9, 2)
    if gas < 20:
        indicator = '🟩'
    elif 20 <= gas < 40:
        indicator = '🟧'
    else:
        indicator = '🟥'

    msg = (
        f'*{indicator} ETH: {gas} GWEI\n\nBTC:* ${prices["BTCUSDT"]}\n*ETH:* ${prices["ETHUSDT"]}\n*BNB:* ${prices["BNBUSDT"]}\n*SOL:* ${prices["SOLUSDT"]}\n*TON'
        f':* ${prices["TONUSDT"]}')
    return msg


def get_price():
    tickers_prices = {"BTCUSDT": '', "ETHUSDT": '', 'BNBUSDT': '', 'SOLUSDT': '', "TONUSDT": ''}
    for symbol in tickers_prices:
        url = f"https://api.bybit.com/v2/public/tickers?symbol={symbol}"
        try:
            response = requests.get(url)
            data = response.json()

            if 'result' in data and len(data['result']) > 0:
                tickers_prices[f"{symbol}"] = round(float(data['result'][0]['last_price']), 1)
            else:
                return None
        except Exception as e:
            logger.info(f"{e} - Error in getting cryptocurrency [{symbol}] prices!")

    return tickers_prices
