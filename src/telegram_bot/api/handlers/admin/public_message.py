import logging
import random
from datetime import datetime

import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from omegaconf import OmegaConf
from telebot import types
from uuid import uuid4

from telegram_bot.api.handlers.common import create_cancel_button
from telegram_bot.db import crud

config = OmegaConf.load("./src/telegram_bot/conf/config.yaml")
strings = OmegaConf.load("./src/telegram_bot/conf/admin.yaml")

# Define timezone
timezone = pytz.timezone(config.timezone)

# Initialize scheduler
scheduler = BackgroundScheduler()

# Dictionary to store user data during message scheduling
die Benachrichtigung

Ich habe eine merkwürdige Benachrichtigung erhalten = {}

# Data structure to store scheduled messages
scheduled_messages = {}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_keyboard_markup(lang: str) -> types.InlineKeyboardMarkup:
    keyboard_markup = types.InlineKeyboardMarkup()
    for option in strings[lang].public_message.menu.options:
        keyboard_markup.add(types.InlineKeyboardButton(option.label, callback_data=option.value))
    return keyboard_markup


def send_scheduled_message(
    bot, user_id: int, media_type: str, message_id: str,\
    message_text: str = None, message_photo: str = None
    ):
    print(media_type, message_id, message_text, message_photo)
    try:
        if media_type == 'text':
            bot.send_message(chat_id=user_id, text=message_text)
        elif media_type == 'photo':
            bot.send_photo(chat_id=user_id, caption=message_text or "", photo=message_photo, disable_notification=False)
        
        # Remove message from scheduled_messages
        if message_id in scheduled_messages:
            del scheduled_messages[message_id]

    except Exception as e:
        logger.error(f"Error sending scheduled message to {user_id}: {e}")


def list_scheduled_messages(bot, user):
    if not scheduled_messages:
        bot.send_message(user.id, strings[user.lang].public_message.no_scheduled_messages)
        return

    response = strings[user.lang].public_message.list_public_messages + "\n"
    for message_id, message_data in scheduled_messages.items():
        scheduled_time = message_data['datetime'].strftime('%Y-%m-%d %H:%M')
        response += f"- {message_id}: {scheduled_time} ({config.timezone})\n"
    bot.send_message(user.id, response)


def cancel_scheduled_message(bot, user):
    if not scheduled_messages:
        bot.send_message(user.id, strings[user.lang].public_message.no_scheduled_messages)
        return

    # Create keyboard for cancel options
    keyboard = types.InlineKeyboardMarkup()
    for message_id in scheduled_messages:
        message_data = scheduled_messages[message_id]
        job_label = f"{message_id}: {message_data['datetime'].strftime('%Y-%m-%d %H:%M')}"
        keyboard.add(types.InlineKeyboardButton(job_label, callback_data=f"cancel_{message_id}"))
    
    bot.send_message(user.id, strings[user.lang].public_message.cancel_message_prompt, reply_markup=keyboard)


def get_message_content(message, bot, user):
    try:
        media_type = 'text' if message.text else 'photo'
        content = message.text or message.caption or ""
        photo = message.photo[-1].file_id if message.photo else None

        scheduled_datetime = user_data[user.id]['datetime']

        message_id = str(random.randint(100, 999))
        scheduled_messages[message_id] = {
            'id': message_id,
            'datetime': scheduled_datetime,
            'content': content,
            'media_type': media_type,
            'photo': photo,
            'jobs': []
        }
        target_users = crud.read_users()
        for target_user in target_users:
            job = scheduler.add_job(
                send_scheduled_message, 'date', run_date=scheduled_datetime,
                args=[bot, target_user.id, media_type, message_id, content, photo]
            )
            scheduled_messages[message_id]['jobs'].append(job.id)

        bot.send_message(user.id, strings[user.lang].public_message.message_scheduled_confirmation.format(
            message_id=message_id,
            n_users=len(target_users),
            send_datetime=scheduled_datetime.strftime('%Y-%m-%d %H:%M'),
            timezone=config.timezone
        ))
    finally:
        user_data.pop(user.id, None)


def register_handlers(bot):
    logger.info("Registering `public message` handlers")

    @bot.callback_query_handler(func=lambda call: call.data == "public_message")
    def query_handler(call: types.CallbackQuery, data: dict):
        user = data["user"]
        bot.send_message(
            user.id, strings[user.lang].public_message.menu.title,
            reply_markup=create_keyboard_markup(user.lang)
        )

    @bot.callback_query_handler(func=lambda call: call.data == "schedule_public_message")
    def create_public_message_handler(call: types.CallbackQuery, data: dict):
        user = data["user"]
        sent_message = bot.send_message(
            user.id, strings[user.lang].public_message.enter_datetime_prompt.format(timezone=config.timezone),
            reply_markup=create_cancel_button(user.lang)
        )
        bot.register_next_step_handler(sent_message, get_datetime_input, bot, user)

    @bot.callback_query_handler(func=lambda call: call.data == "list_scheduled_messages")
    def list_scheduled_messages_handler(call: types.CallbackQuery, data: dict):
        user = data["user"]
        list_scheduled_messages(bot, user)

    @bot.callback_query_handler(func=lambda call: call.data == "cancel_scheduled_message")
    def cancel_scheduled_message_handler(call: types.CallbackQuery, data: dict):
        user = data["user"]
        cancel_scheduled_message(bot, user)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("cancel_"))
    def handle_cancel_callback(call: types.CallbackQuery, data: dict):
        user = data["user"]
        callback_data = call.data

        if callback_data == "cancel_all":
            scheduler.remove_all_jobs()
            bot.send_message(user.id, strings[user.lang].public_message.all_scheduled_messages_cancelled)
        else:
            message_id = callback_data.replace("cancel_", "")
            for job in scheduled_messages[message_id]['jobs']:
                scheduler.remove_job(job)
            
            # remove message from scheduled_messages
            del scheduled_messages[message_id]

            bot.send_message(user.id, strings[user.lang].public_message.cancel_message_confirmation.format(message_id=message_id))

    def get_datetime_input(message, bot, user):
        try:
            user_datetime = datetime.strptime(message.text, '%Y-%m-%d %H:%M')
            user_datetime_localized = timezone.localize(user_datetime)
            if user_datetime_localized < datetime.now(timezone):
                raise ValueError("Past datetime")

            user_data[user.id] = {'datetime': user_datetime_localized}
            sent_message = bot.send_message(user.id, strings[user.lang].public_message.record_message_prompt)
            bot.register_next_step_handler(sent_message, get_message_content, bot, user)
        except Exception as e:
            logger.error(f"Error getting datetime input: {e}")
            sent_message = bot.send_message(
                user.id, strings[user.lang].public_message.invalid_datetime_format
            )
            bot.register_next_step_handler(sent_message, get_datetime_input, bot, user)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("cancel_"))
    def handle_cancel_callback(call: types.CallbackQuery, data: dict):
        user = data["user"]
        callback_data = call.data

        message_id = callback_data.replace("cancel_", "")
        if message_id in scheduled_messages:
            message_data = scheduled_messages[message_id]
            for job_id in message_data['jobs']:
                try:
                    scheduler.remove_job(job_id)
                except Exception as e:
                    logger.error(f"Error removing job {job_id}: {e}")
            del scheduled_messages[message_id]
            bot.send_message(call.message.chat.id, strings[user.lang].public_message.cancel_message_confirmation.format(message_id=message_id))
        else:
            bot.send_message(call.message.chat.id, strings[user.lang].public_message.message_not_found)

scheduler.start()
