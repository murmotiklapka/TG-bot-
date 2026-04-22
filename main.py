import telebot
from dotenv import load_dotenv
import os
from cv_service import handle_image
import cv2

load_dotenv()
bot = telebot.TeleBot(os.getenv("TG_API_TOKEN"))

@bot.message_handler(commands=['start'])
def start(message):
    text = (
        f'Приветствую, {message.from_user.first_name}!\n\n'
        'Могу помочь с распознаванием объектов на картинке'
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(content_types=['photo'])
def handler_photo(message):
    os.makedirs('./images', exist_ok=True)

    temp_data = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(temp_data.file_path)

    image_path = f'./images/{message.message_id}.jpg'

    with open(image_path, 'wb') as image:
        image.write(downloaded_file)

    result = handle_image(image_path)
    return_text = ''

    if len(result) > 0:
        for obj in result:
            return_text += f"Класс: {obj['class']}, вероятность: {obj['confidence']}%\n"

        result_image_path = os.path.splitext(image_path)[0] + '_result.jpg'

        if os.path.exists(result_image_path):
            with open(result_image_path, 'rb') as img:
                bot.send_photo(message.chat.id, img, caption=return_text)
        else:
            bot.send_message(message.chat.id, return_text)
    else:
        response_text = 'На изображении не обнаружено объектов'
        bot.send_message(message.chat.id, response_text)

    if os.path.exists(image_path):
        os.remove(image_path)

bot.infinity_polling()