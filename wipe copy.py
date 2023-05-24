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

    subprocess.run(['rm', file_path])


async def create_file(file_path):
    data = {
        "messages": [
            # Оставляем пустую строку здесь
        ]
    }
    with open(file_path, 'w') as file:
        file.write("{\n    \"messages\": [\n    ]\n}")
    
    try:
        command = "sudo systemctl restart echo"
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


async def wipe(callback_query: types.CallbackQuery, state: FSMContext, message: types.Message):
    await callback_query.answer()

    if callback_query.data == 'confirm':
        try:
            delete_file("data/replies.json")
            await create_file("data/replies.json")
            await callback_query.message.answer("Файл успешно удален и создан.")
        except FileNotFoundError:
            await callback_query.message.answer("Файл не найден.")
            print("File not found.")
    elif callback_query.data == 'cancel':
        try:
            await message.delete()
        except:
            pass

    await state.finish()
