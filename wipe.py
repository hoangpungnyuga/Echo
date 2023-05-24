import os
import json
import subprocess
import asyncio
from loader import bot, dp
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class WipeConfirmation(StatesGroup):
    CONFIRMATION = State()


def delete_file(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File {file_path} does not exist.")

    subprocess.run(['rm', file_path]) # os.remove Почему-то не работало, вариант subprocess


async def create_file(file_path):
    data = {
        "messages": [
            # Это нужно чтобы бот не возращал data/replies.json
        ]
    }
    with open(file_path, 'w') as file:
        file.write("{\n    \"messages\": [\n    ]\n}")

    try:
        command = "sudo systemctl restart echo" # Перезапуск нужен дабы правильно применялась line 22
        process = await asyncio.create_subprocess_shell(command)
        await process.wait()
    except Exception as e:
        raise RuntimeError(f"Error while performing restart: {e}")


async def confirm_wipe(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    confirm_button = types.InlineKeyboardButton('Да', callback_data='confirm')
    cancel_button = types.InlineKeyboardButton('Нет', callback_data='cancel')
    keyboard.add(confirm_button, cancel_button)

    await WipeConfirmation.CONFIRMATION.set()
    await message.reply("Вы уверены, что хотите выполнить операцию wipe?\nБот также будет перезапущен", reply_markup=keyboard)


async def wipe(call: types.CallbackQuery, state: FSMContext, message: types.Message):
    if call.data == 'confirm':
        try:
            delete_file("data/replies.json")
            await create_file("data/replies.json")
            await wipe_success(call)
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except FileNotFoundError:
            await wipe_error(call)
            print("File not found.")
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    elif call.data == 'cancel':
        try:
            await wipe_cancel(call)
            await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except:
            pass

    await state.finish()


async def wipe_success(call: types.CallbackQuery):
    await call.answer("Успешно выполнен Wipe.", show_alert=False)

async def wipe_error(call: types.CallbackQuery):
    await call.answer("Файл не найден.", show_alert=False)

async def wipe_cancel(call: types.CallbackQuery):
    await call.answer("Окей, отменено.", show_alert=False)