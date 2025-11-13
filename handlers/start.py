from aiogram import Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from keyboards import get_main_keyboard


async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        "👋 Добро пожаловать в систему заполнения анкеты!\n\n"
        "📊 Я помогу вам пройти процесс заполнения анкеты пошагово.\n"
        "🎯 Каждый заполненный раздел приближает вас к завершению.\n\n"
        "Нажмите кнопку ниже, чтобы начать заполнение.",
        reply_markup=get_main_keyboard()
    )


async def cmd_help(message: Message):
    """Обработчик команды /help"""
    await message.answer(
        "📋 Помощь по использованию бота:\n\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n"
        "/cancel - Отменить заполнение анкеты\n\n"
        "Анкета состоит из нескольких разделов. "
        "Вы можете заполнять их по порядку или переходить к нужному разделу."
    )


def register_start_handlers(dp: Dispatcher):
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_help, Command("help"))

