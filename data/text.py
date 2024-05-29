from web3 import Web3

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
                'INPUT': '*⚠️Введите сообщение, которое хотите отправить всем пользователям бота:*',

            },
            'CHANNEL': {
                'ADD': '*Пришлите id или @тег канала, который хотите добавить.*\n(предварительно выдайте Боту права '
                       'администратора в этом канале)',
                'DEL': '*Выберите канал из списка, который хотите удалить*'
            },
            'HELP': f'*Команды:\n\n/{CMD_ADD_CHANNEL} - добавить канал\n/{CMD_DEL_CHANNEL} - удалить канал\n'
                    f'/{CMD_SEND_MSG} - разослать сообщение всем пользователям*'
        },
        'SETTINGS': {
            'MENU': '*Настройте параметры бота*',
            'INTERVAL': '*Выберите интервал, с которым Вы будете получать информацию о цене газа в сети:*',
            'STOP': 'Бот остановлен!\n\nЧтобы возобновить работу, откройте настройки (/menu), нажмите на '
                    'кнопку «Включить» или установите новый интервал.',
            'START': 'Бот снова работает!\n\nВы можете выбрать интервал рассылки сообщений, открыв настройки '
                     '(/menu). Чтобы остановить работу, нажмите на кнопку «Выключить» в меню.'
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
    con_web3 = Web3(provider=Web3.HTTPProvider(endpoint_uri='https://rpc.ankr.com/eth'))
    gas = round(con_web3.eth.gas_price / 10 ** 9, 2)
    msg = f'*gas price: {gas} ETH gwei*'
    return msg
