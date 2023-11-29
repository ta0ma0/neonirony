import os
import asyncio
from telethon import TelegramClient, events, sync
from telethon.errors.rpcerrorlist import MediaCaptionTooLongError
import time
import shutil
import configparser
import logging

# Настройка логирования
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Создание объекта ConfigParser
config = configparser.ConfigParser()

# Чтение файла конфигурации
config.read('config.ini')

# Извлечение настроек
api_id = config.get('bot_config', 'api_id')
api_hash = config.get('bot_config', 'api_hash')
bot_token = config.get('bot_config', 'bot_token')
channel_username = config.get('bot_config', 'channel_username')


# Создаем клиент Telethon
client = TelegramClient('session_name', api_id, api_hash).start(bot_token=bot_token)


def delete_post_directories():
    post_directories = [d for d in os.listdir('.') if d.startswith('post_') and os.path.isdir(d)]
    
    # Сортируем директории по времени модификации (от самой новой к самой старой)
    post_directories.sort(key=lambda x: os.path.getmtime(x), reverse=True)

    # Пропускаем первую (самую новую) директорию и удаляем все остальные
    for directory in post_directories[1:]:
        shutil.rmtree(directory)


def load_processed_directories():
    if os.path.exists("processed_directories.txt"):
        with open("processed_directories.txt", "r") as file:
            return set(file.read().splitlines())
    return set()

def save_processed_directory(directory):
    with open("processed_directories.txt", "a") as file:
        file.write(directory + "\n")

async def post_to_channel(directory):
    advice_file = os.path.join(directory, 'advice.txt')
    image_file = os.path.join(directory, 'image.png')

    if os.path.exists(advice_file) and os.path.exists(image_file):
        with open(advice_file, 'r') as file:
            text = file.read().split('Запрос к Dall-e:')[0].strip()

        try:
            await client.send_file(channel_username, image_file, caption=text[:1024])
            delete_post_directories()
            return True
        except MediaCaptionTooLongError:
            # Здесь можно добавить логику сокращения текста или его разделения
            logging.error("Caption too long for media. Consider shortening it.")
            # Продолжи отправлять с сокращённым текстом или раздели текст на несколько сообщений
            # Например:
            await client.send_file(channel_username, image_file, caption=text[:1024])
            if len(text) > 1024:
                await client.send_message(channel_username, text[1024:])
            return True
    else:
        logging.warning(f"Required files not found in directory: {directory}")
        return False

async def check_new_directories():
    logging.info(f"Checking new directories")
    posted_directories = load_processed_directories()

    while True:
        # Получаем список директорий с их временем изменения
        directories_with_time = [(d, os.path.getmtime(d)) for d in os.listdir('.') if d.startswith('post_') and os.path.isdir(d)]
        # Сортируем список по времени изменения (самые новые в начале)
        directories_with_time.sort(key=lambda x: x[1], reverse=True)

        for directory, _ in directories_with_time:
            if directory not in posted_directories:
                if await post_to_channel(directory):
                    save_processed_directory(directory)
                    posted_directories.add(directory)

        await asyncio.sleep(10)  # Проверяем каждые 10 секунд


logging.info('Bot started')
with client:
    client.loop.run_until_complete(check_new_directories())
