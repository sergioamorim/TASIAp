#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import re
import subprocess
import bot_daemon_config as config

logger = logging.getLogger('bot_daemon')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler('bot_daemon.log')
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)

def is_user_authorized(user_id):
    return True if user_id in config.authorized_users else False

def is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def is_double_int(s):
    try: 
        s_split_space = s.split(' ')
        int(s_split_space[0])
        int(s_split_space[1])
        return True
    except ValueError:
        return False

def get_onu_info_string(onu_repr):
    phy_address = re.findall(".*phy_id\\=\\'([0-9A-Z]{4}[0-9A-Fa-f]{8}).*", onu_repr)[0]
    board = re.findall(".*board_id\\=\\'([0-9]{2}).*", onu_repr)[0]
    pon = re.findall(".*pon_id\\=\\'([0-9]).*", onu_repr)[0]
    onu_number = re.findall(".*number\\=\\'([0-9]*)'.*", onu_repr)[0]
    cvlan = re.findall(".*cvlan\\=\\'([0-9]*)'.*", onu_repr)[0]
    return '{0}{1}{2}{3} {4} {5}'.format('1' if board == '12' else '2', pon, '0' if int(onu_number) < 10 else '', onu_number, cvlan, phy_address)

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    logger.debug('start handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
    update.message.reply_text('Bem-vindo(a)!\
        \nEsse BOT envia mensagens de alarme do Zabbix para o grupo da Elite Fibra e também pode autorizar ONUs.\
        \nSe precisar de ajuda para autorizar ONUs, envie /help')


def help(bot, update):
    """Send a message when the command /help is issued."""
    logger.debug('help handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
    update.message.reply_text('Para autorizar uma ONU envie autorizar e siga as instruções.')

def sinal(bot, update):
    logger.debug('sinal handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
    if is_user_authorized(update.message.from_user.id):
        message_list = update.message.text.lower().split(' ')
        if is_int(message_list[1]) and int(message_list[1]) > 1100 and int(message_list[1]) < 3900 and int(message_list[1][2:]) > 0 and int(message_list[1][1:2]) > 0 and int(message_list[1][1:2]) < 9:
            command_list = ['python3.7', 'onu_signal_power.py', '-i', '{0}'.format(message_list[1])]
            logger.debug('sinal handler: valid id: command_list: {0}'.format(command_list))
            answer_string = subprocess.run(command_list, capture_output=True).stdout.decode('utf-8').replace('\n', '')
            logger.debug('sinal handler: valid id: answer_string: {0}'.format(answer_string))
            if answer_string == 'not found':
                update.message.reply_text('{0} sinal: não existe ONU autorizada com esse ID'.format(message_list[1]))
            elif answer_string == 'off':
                update.message.reply_text('{0}: sem sinal'.format(message_list[1]))
            elif answer_string == 'error':
                update.message.reply_text('{0}: erro não especificado'.format(message_list[1]))
            else:
                update.message.reply_text('{0} sinal: {1}'.format(message_list[1], answer_string))
        else:
            update.message.reply_text('ID da ONU inválido. O priméiro dígito do ID deve ser de 1 a 3 (número da placa), o segundo dígito deve ser de 1 a 8 (número da PON) e os dois últimos dígitos devem ser entre 01 e 99 (número da ONU).')
    else:
        update.message.reply_text('Você não tem permissão para acessar o menu /sinal.')

def reiniciar(bot, update):
    logger.debug('reiniciar handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
    if is_user_authorized(update.message.from_user.id):
        message_list = update.message.text.lower().split(' ')
        if is_int(message_list[1]) and int(message_list[1]) > 1100 and int(message_list[1]) < 3900 and int(message_list[1][2:]) > 0 and int(message_list[1][1:2]) > 0 and int(message_list[1][1:2]) < 9:
            command_list = ['python3.7', 'onu_restart.py', '-i', '{0}'.format(message_list[1])]
            logger.debug('reiniciar handler: valid id: command_list: {0}'.format(command_list))
            answer_string = subprocess.run(command_list, capture_output=True).stdout.decode('utf-8').replace('\n', '')
            logger.debug('reiniciar handler: valid id: answer_string: {0}'.format(answer_string))
            if answer_string == 'not found':
                update.message.reply_text('{0} reiniciar: sem sinal ou não existe ONU autorizada com esse ID'.format(message_list[1]))
            elif answer_string == 'error':
                update.message.reply_text('{0}: erro não especificado'.format(message_list[1]))
            elif answer_string == 'done':
                update.message.reply_text('{0}: comando enviado com sucesso. A ONU será reiniciada em até 2 minutos.'.format(message_list[1]))
            else:
                update.message.reply_text('{0} reiniciar: resposta desconhecida: {1}'.format(message_list[1], answer_string))
        else:
            update.message.reply_text('ID da ONU inválido. O priméiro dígito do ID deve ser de 1 a 3 (número da placa), o segundo dígito deve ser de 1 a 8 (número da PON) e os dois últimos dígitos devem ser entre 01 e 99 (número da ONU).')
    else:
        update.message.reply_text('Você não tem permissão para acessar o menu /reiniciar.')

def onu_auth(bot, update):
    logger.debug('onu_auth handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))
    if 'aut' in update.message.text.lower():
        answer_list = subprocess.run(['python3.7', 'authorize_onu.py'], capture_output=True).stdout.decode('utf-8').split(' ')
        logger.debug('onu_auth: aut: answer_list: {0}'.format(answer_list))
        if '\n' in answer_list:
            answer_list.remove('\n')
        if len(answer_list) is 1:
            if 'None' in answer_list[0]:
                update.message.reply_text('Nenhuma ONU foi encontrada. Envie "autorizar" para verificar novamente se há novas ONUs.')
            else:
                update.message.reply_text('Uma ONU foi encontrada: '+answer_list[0]+'\nConfirma serial para autorizar?\nEnvie "sim" para autorizar ou "autorizar" para verificar novamente se há novas ONUs.')
        else:
            reply_list = []
            for i, answer in enumerate(answer_list):
                reply_list.append(str(i+1)+'. ')
                reply_list.append(answer+'\n')
            update.message.reply_text('ONUs encontradas:\n'+''.join(reply_list)+'Envie o número da ONU que deseja autorizar (ex.: "1") ou "autorizar" para verificar novamente se há novas ONUs.')
    elif is_int(update.message.text) or is_double_int(update.message.text):
        update_message_text_lower_split_space = update.message.text.lower().split(' ')
        if len(update_message_text_lower_split_space) == 2 and is_int(update_message_text_lower_split_space[1]) and int(update_message_text_lower_split_space[1]) > 0 and int(update_message_text_lower_split_space[1]) < 4096:
            answer_string = subprocess.run(['python3.7', 'authorize_onu.py', '-a {0}'.format(update_message_text_lower_split_space[0]), '-v {0}'.format(update_message_text_lower_split_space[1])], capture_output=True).stdout.decode('utf-8')
        else:
            answer_string = subprocess.run(['python3.7', 'authorize_onu.py', '-a {0}'.format(update_message_text_lower_split_space[0])], capture_output=True).stdout.decode('utf-8')
        logger.debug('onu_auth: int or double_int: answer_string: {0}'.format(answer_string))
        if 'OnuDevice' in answer_string:
            update.message.reply_text('ONU autorizada com sucesso!\n{0}'.format(get_onu_info_string(answer_string)))
        elif 'ERR' in answer_string:
            update.message.reply_text('A ONU informada não foi encontrada. Envie "autorizar" para ver a lista de ONUs disponíveis.')
        elif 'None' in answer_string:
            update.message.reply_text('Nenhuma ONU foi encontrada. Envie "autorizar" para verificar novamente se há novas ONUs.')
    elif 'sim' in update.message.text.lower():
        update_message_text_lower_split_space = update.message.text.lower().split(' ')
        if len(update_message_text_lower_split_space) == 2 and is_int(update_message_text_lower_split_space[1]) and int(update_message_text_lower_split_space[1]) > 0 and int(update_message_text_lower_split_space[1]) < 4096:
            answer_string = subprocess.run(['python3.7', 'authorize_onu.py', '-a 1', '-v {0}'.format(update_message_text_lower_split_space[1])], capture_output=True).stdout.decode('utf-8')
        else:
            answer_string = subprocess.run(['python3.7', 'authorize_onu.py', '-a 1'], capture_output=True).stdout.decode('utf-8')
        logger.debug('onu_auth: sim: answer_string: {0}'.format(answer_string))
        if 'OnuDevice' in answer_string:
            update.message.reply_text('ONU autorizada com sucesso!\n{0}'.format(get_onu_info_string(answer_string)))
        elif 'ERR' in answer_string:
            update.message.reply_text('A ONU não foi encontrada. Envie "autorizar" para ver a lista de ONUs disponíveis.')
        elif 'None' in answer_string:
            update.message.reply_text('Nenhuma ONU foi encontrada. Envie "autorizar" para verificar novamente.')
    else:
        update.message.reply_text('Para autorizar uma ONU envie "autorizar".')

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)
    logger.debug('onu_auth handler: message from {0}{1}{2}({3}) received: {4}'.format(update.message.from_user.first_name, ' {0}'.format(update.message.from_user.last_name) if update.message.from_user.last_name else '', ' - @{0} '.format(update.message.from_user.username) if update.message.from_user.username else '', update.message.from_user.id, update.message.text))

def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(config.bot_token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("sinal", sinal))
    dp.add_handler(CommandHandler("reiniciar", reiniciar))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message
    dp.add_handler(MessageHandler(Filters.text, onu_auth))

    # log all errors
    dp.add_error_handler(error)

    logger.info('Starting...')
    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()