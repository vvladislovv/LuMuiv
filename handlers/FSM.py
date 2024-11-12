from fnmatch import fnmatch

from aiogram import Bot, Router, F, types
from aiogram.types import Message, File, FSInputFile
from aiogram.utils import keyboard
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from handlers.Keyboard import reply_markup, createKeyboard
import config, os, sqlite3, aiohttp
# Import modules
#from main import
from datetime import datetime
from handlers.DataBase import update_data, get_db_connection, GetDataUser,DeleatUserData, SelectData
from handlers.Methods import GetPhoto

class FSM(StatesGroup):
    msg = State()
    photo = State()
    waitCode = State()
    delet_Data = State()
    changeImg = State()
    changeMsg = State()



FSMBot = Router(name=__name__)

@FSMBot.message(FSM.msg)
async def send_msg(message: Message) -> None:
    if FSM.msg.state:
        if message.text:

            await update_data({
                'UserID': message.from_user.id,
                'Type': "Message",
                'value': message.text,
            })

            await update_data({
                'UserID': message.from_user.id,
                'Type': "TypeAction",
                'value': "Message",
            })

            await update_data({
                'UserID': message.from_user.id,
                'Type': "Stage",
                'value': "Expectation",
            })

            keyword = createKeyboard([
                ("Да", "YesMsg"),
                ("Нет", "NoMsg"),
            ], 2)

            await message.answer('❓ Вы хотите изменить текст?', reply_markup=keyword.as_markup())
        else:
            await message.answer('📝 Некоректный текс, отправте текст повторно')

@FSMBot.message(FSM.waitCode)
async def process_code(message: types.Message, state: FSMContext) -> None:
    try:
        user_code = int(message.text.strip())
        for _, admin_info in config.Admins.items():
            if admin_info['Key'] == user_code and admin_info['ID'] == message.from_user.id:
                keyword = createKeyboard([
                    ("Все новые стикеры", "StickerAdmin"),
                    ("Все новые сообщения", "MsgAdmin"),
                    ("Удалить данные человека", "DeleteBase"),
                ], 3)

                await message.answer("Выберите, что вы хотите сделать:", reply_markup=keyword.as_markup())
                await state.clear()
            '''            elif admin_info['Key'] != user_code and message.from_user.id != admin_info['ID']:
                await message.answer("Доступ запрещен! Неверный код.")
                await state.clear()'''
    except ValueError:
        await message.answer("Пожалуйста, введите действительный код.")
    except Exception as e:
        print(f"An error occurred while processing the code: {str(e)}")

@FSMBot.message(FSM.delet_Data)
async def process_delete_user(message: types.Message, state: FSMContext) -> None:
    try:
        username = message.text.strip()

        with get_db_connection() as conn:
            user_info = SelectData(username)

            if user_info:
                DeleatUserData(username)
                await message.answer("Пользователь был удален✅")
                await state.clear()
            else:
                await message.answer("❌Повторите запрос, пользователя нет.")
    except Exception as e:
        print(f"An error occurred while deleting user: {str(e)}")

@FSMBot.message(F.photo)
async def image_handler(message: Message, state: FSMContext) -> None:
    try:
        current_state = await state.get_state()
        if current_state == FSM.photo.state:
            if message.photo:
                FileSpeci = await GetPhoto({
                    'file_id': message.photo[-1].file_id,
                    'msg': message
                })

                async with aiohttp.ClientSession() as session:
                    async with session.get(FileSpeci['photo_url']) as response:
                        if response.status == 200:
                            image_data = await response.read()

                            with open(FileSpeci['image_file_path'], 'wb') as file:
                                file.write(image_data)

                            await update_data({
                                'UserID': message.from_user.id,
                                'Type': "Image",
                                'value': FileSpeci['unique_filename'],
                            })

                    await update_data({
                        'UserID': message.from_user.id,
                        'Type': "TypeAction",
                        'value': "Message",
                    })

                    await update_data({
                        'UserID': message.from_user.id,
                        'Type': "Stage",
                        'value': "Expectation",
                    })

                keyword = createKeyboard([
                    ("Да", "Sticker"),
                    ("Нет", "NoPhoto"),
                ], 2)
                await message.answer('❓ Вы хотите изменить фото?', reply_markup=keyword.as_markup())
                await state.clear()  # Этого не было
            else:
                await message.answer('📸 Отправте фото повторно')
        elif current_state == FSM.changeImg.state:
                with get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM DataUsers")
                    records = cursor.fetchall()

                    UsersSQL = await GetDataUser(records)

                    if UsersSQL[8] == "1":
                        if message.photo:
                            FileSpeci = await GetPhoto({
                                'file_id': message.photo[-1].file_id,
                                'msg': message
                            })

                            async with aiohttp.ClientSession() as session:
                                async with session.get(FileSpeci['photo_url']) as response:
                                    if response.status == 200:
                                        image_data = await response.read()

                                        with open(FileSpeci['image_file_path'], 'wb') as file:
                                            file.write(image_data)


                                        await update_data({
                                            'UserID': message.from_user.id,
                                            'Type': "Image",
                                            'value': FileSpeci['unique_filename'],
                                        })

                                        for old_file in os.listdir('PhotoDB'):
                                            if fnmatch(old_file, FileSpeci['previous_image_pattern']):
                                                photo_file = FSInputFile(path=os.path.join('PhotoDB', old_file))
                                                await message.answer_photo(photo=photo_file,
                                                                           caption=f"Ваше новое изображение")

                                                keyword = createKeyboard([
                                                    ("Да", "Sticker2"),
                                                    ("Нет", "PhotoYesRedact"),
                                                ], 2)
                                                await message.answer('❓ Вы хотите изменить фото?',
                                                                     reply_markup=keyword.as_markup())
                                                await state.clear()

    except Exception as Er:
        print(f"Error: {Er}")

@FSMBot.message(FSM.changeMsg)
async def Change(message: Message, state: FSMContext):
    try:
        user_text = message.text
        await state.update_data(user_message=user_text)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM DataUsers")
            records = cursor.fetchall()
            for row in records:
                if row[9] == "1":
                    await update_data({
                        'UserID': row[0],
                        'Type': "Message",
                        'value': message.text,
                    })

        await message.answer(f"Ваше новое сообщение: {user_text}")
        await state.clear()  # Очищаем состояние после обработки

        keyword = createKeyboard([
            ("Да", "UpdateMSG"),
            ("Нет", "MsgPublic")
        ], 2)

        await message.answer("Что вы хотите изменить сообщение?", reply_markup=keyword.as_markup())
    except Exception as Er:
        print(f"Error: {Er}")
