from core.logger_config import PROJECT_NAME
from core.client_web3.client import Client
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
ENG = 'ENG'

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
                         'Вы уверены, что хотите отправить этот пост всем пользователям бота?\n',
                'SENT': '✅*Сообщение было отправлено всем пользователям!*',
                'EDIT': '✅*Выполнен переход к редактированию сообщения!*'
            },
            'CHANNEL': {
                'ADD': '*Пришлите id или @тег канала, который хотите добавить.*\n(предварительно выдайте Боту права '
                       'администратора в этом канале)',
                'ADDED': '',
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
            'LANGUAGE': '*Выберите язык:*',
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
    },
    ENG: {
            'CLIENT': {
                'HELP': '*If you encounter any problems with the Bot, please contact '
                        'technical support: @wndrflp*'
            },
            'ADMIN': {
                'SEND_MSG': {
                    'INPUT': 'Пришлите *пост*, который вы хотите разослать всем пользователям:',
                    'CHECK': '*Проверьте пост на корректность!*\n'
                             '\n'
                             'Вы уверены, что хотите отправить этот пост всем пользователям бота?\n',
                    'SENT': '✅*Сообщение было отправлено всем пользователям!*',
                    'EDIT': '✅*Выполнен переход к редактированию сообщения!*'
                },
                'CHANNEL': {
                    'ADD': '*Пришлите id или @тег канала, который хотите добавить.*\n(предварительно выдайте Боту права'
                           'администратора в этом канале)',
                    'ADDED': '',
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
                'MENU': f'*Hello, this is the {PROJECT_NAME} menu!*\n'
                        f'\n'
                        f'This is where you can customize the bot.',
                'INTERVAL': '*Select the interval at which you will receive information about the gas price in the '
                            'network:*',
                'LANGUAGE': '*Choose the language:*',
                'STOP': 'The bot has been stopped!',
                'START': 'The bot is working again!'
            },
            'SUB': {
                'CLOSED': f'*Access to the bot has been denied.*',
                'OPENED': '*Access to the bot has been opened!\n\nThe bot sends the current cost of GAS. '
                          'You can adjust the sending interval or stop the Bot in the /menu.*',
            },
            'NO_ROOTS': 'You do not have permission to use this command',
            'OTHER': 'There is no such a command, to customize the bot call /menu.'
        }
}

BUTTONS = {
    'RUS': {
        'INTERVAL': 'Интервалы',
        'LANGUAGE': 'Язык',
        'TURN': {
            'ON': 'Включить',
            'OFF': 'Выключить'
        },
        'PROMO': {
            'SEND': 'Отослать',
            'EDIT': 'Редактировать'
        },
        'BACK': '« Назад'
    },
    'ENG': {
        'INTERVAL': 'Intervals',
        'LANGUAGE': 'Language',
        'TURN': {
            'ON': 'Turn on',
            'OFF': 'Turn off'
        },
        'PROMO': {
            'SEND': 'Отослать',
            'EDIT': 'Редактировать'
        },
        'BACK': '« Back'
    }
}


def get_msg_channels_to_subscribe(LAN):
    channels = ''
    i = 1
    for tag in table_channels.get_channel_tags():
        channels += f'{i}. ' + 'https://t.me/' + tag + '\n'
    if LAN == 'RUS':
        msg = f'*Для использования бота необходимо быть подписанным на следующие каналы: \n\n{channels}*'
    elif LAN == 'ENG':
        msg = f'*To use the bot you have to be subscribed to the following channels: \n\n{channels}*'
    return msg


last_tickers_prices = {"BTCUSDT": '', "ETHUSDT": '', 'BNBUSDT': '', 'SOLUSDT': '', "TONUSDT": ''}


def get_msg_gas_price(LAN):
    global last_tickers_prices
    prices = Client.get_tickers_prices(last_tickers_prices)
    last_tickers_prices = prices
    # market_data = Client.get_coin_gecko_data()
    gas = Client.get_gas_price()
    market_data = {}
    market_data["market_cap_usd"] = '1'
    market_data["volume_24h_usd"] = '2'
    market_data["dominance_btc_percentage"] = '3'
    market_data["dominance_eth_percentage"] = '4'
    if gas < 20:
        indicator = '🟩'
    elif 20 <= gas < 40:
        indicator = '🟧'
    else:
        indicator = '🟥'

    if LAN == 'RUS':
        msg = (
            f'*{indicator} ETH: {gas} GWEI*'
            f'\n'
            f'\n*BTC:* ${prices["BTCUSDT"]}'
            f'\n*ETH:* ${prices["ETHUSDT"]}'
            f'\n*BNB:* ${prices["BNBUSDT"]}'
            f'\n*SOL:* ${prices["SOLUSDT"]}'
            f'\n*TON:* ${prices["TONUSDT"]}'
            f'\n'
            f'\n*Капитализация:* {market_data["market_cap_usd"]} трлн $'
            f'\n*Объем за 24 ч:* {market_data["volume_24h_usd"]} млрд $'
            f'\n*Доминирование:* BTC {market_data["dominance_btc_percentage"]}%'
            f' ETH {market_data["dominance_eth_percentage"]}%')
    elif LAN == 'ENG':
        msg = (
            f'*{indicator} ETH: {gas} GWEI*'
            f'\n'
            f'\n*BTC:* ${prices["BTCUSDT"]}'
            f'\n*ETH:* ${prices["ETHUSDT"]}'
            f'\n*BNB:* ${prices["BNBUSDT"]}'
            f'\n*SOL:* ${prices["SOLUSDT"]}'
            f'\n*TON:* ${prices["TONUSDT"]}'
            f'\n'
            f'\n*Market Cap:* {market_data["market_cap_usd"]} trln $'
            f'\n*Volume for 24 h:* {market_data["volume_24h_usd"]} mlrd $'
            f'\n*Dominance:* BTC {market_data["dominance_btc_percentage"]}%'
            f' ETH {market_data["dominance_eth_percentage"]}%')
    return msg


# ADMING MSG
def msg_soft_not_added(e):
    msg = (f'*Ошибка:\n{e}\n\nВы ввели некорректный адрес или не выдали права администратора '
           f'Боту в канале. Попробуйте ещё раз.*')
    return msg


def msg_soft_added(channel_id: int, channel_tag: str, channel_name: str):
    msg = f'*Канал был добавлен:\nID канала: {channel_id}\nТег канала: @{channel_tag}\nНазвание канала: {channel_name}*'
    return msg
