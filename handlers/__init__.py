from aiogram import Dispatcher
from .start import register_start_handlers
from .form import register_form_handlers


def register_handlers(dp: Dispatcher):
    register_start_handlers(dp)
    register_form_handlers(dp)

