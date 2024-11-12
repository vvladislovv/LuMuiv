import time

from aiogram import Bot, Router, F, types
from aiogram.types import Message, File, FSInputFile
from aiogram.fsm.context import FSMContext

import config, math, random, os
from fnmatch import fnmatch
from datetime import datetime
from handlers.FSM import FSM
from handlers.DataBase import update_data, GetDataUser, UsingBot, UpdateIDSQL, FindUserData
from handlers.Keyboard import createKeyboard, createKeyNextLevel
from handlers.Methods import *
Callback_router = Router(name=__name__)

@Callback_router.callback_query(F.data == "Main")
async def MainGlobule(call:  types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    keyword = createKeyNextLevel([
        ("😊 Новый стикер", "Sticker"),
        ("💭 Новые сообщение", "Msg"),
        ("📕 UDiary - Бот по расписанию", "UDiaryBot"),
        # ("⚙️ Профиль", "Profile")
    ], 2, 1)

    await call.message.answer(" Привет! Выберите интересующее действие:)", reply_markup=keyword.as_markup())

@Callback_router.callback_query(F.data == 'NoPhoto')
async def callback_query(call: types.CallbackQuery, state: FSMContext) -> None:
    try:
        await UpdateIDSQL({
            "IDType": "IDimage"
        })

        keyword = createKeyboard([
            ("Вернуться в меню", "Main"),
        ], 1)

        await call.message.answer("📸 Фото было отправлено на модерацию. Мы вас оповестим.",reply_markup=keyword.as_markup())
       # await call.message.answer("⚙️ Вернуться в главное меню, напишите команду /start")
        await state.clear()
        #await call.message.edit_reply_markup(reply_markup=None)
    except Exception as Err:
        print(f"Error {Err}")


@Callback_router.callback_query(F.data.in_({'Sticker', 'Sticker2', 'Msg', 'NoMsg', 'YesPhotoOne', 'EditPhoto','YesMsg', 'NoMsgOne', 'UpdateMSG'}),)
async def Callback_Query_Main(call: types.CallbackQuery, state: FSMContext) -> None:
    if call.data == "Sticker":
        DataUser: tuple = await FindUserData(call)
        GetUser: tuple = await GetDataUser(DataUser)

        if GetUser[6] == None:
            keyword = createKeyboard([
                ("Вернуться в меню", "Main"),
            ], 1)
            await call.message.answer("🖼️Прешлите одно новые фото:",reply_markup=keyword.as_markup())
            #await call.message.edit_reply_markup(reply_markup=None)
            await state.update_data(name=F.data.text)
            await state.set_state(FSM.photo)
        elif GetUser[6] != None:
            await call.message.answer(
                f"😌Вы уже отправили стикер. Когда администратор проверит предыдущие, вы сможете отправить следующий стикер!")
    elif call.data == "Sticker2":
        await call.message.answer("🖼️Прешлите новые фото:")
        # await call.message.edit_reply_markup(reply_markup=None)
        await state.update_data(name=F.data.text)
        await state.set_state(FSM.changeImg)
    elif call.data == "Msg":
        try:
            DataUser : tuple = await FindUserData(call)
            GetUser : tuple = await GetDataUser(DataUser)

            if GetUser[5] == None:
                keyword = createKeyboard([
                    ("Вернуться в меню", "Main"),
                ], 1)
                await state.update_data(name=F.data.text)
                await state.set_state(FSM.msg)
                await call.message.answer("💭Напишите одно сообщение:",reply_markup=keyword.as_markup())
                #await call.message.edit_reply_markup(reply_markup=None)
            elif GetUser[5] != None:
                await call.message.answer(
                    f"😌Вы уже отправили сообщение. Когда администратор проверит предыдущие, вы сможете отправить следующее сообщение!")

        except Exception as Err:
            print(f"Error {Err}")
    elif call.data == "NoMsg":
        await UpdateIDSQL({
            'IDType': 'IDmsg'
        })

        keyword = createKeyboard([
            ("Вернуться в меню", "Main"),
        ], 1)

        await call.message.answer("📄 Текст было отправлен на модерацию. Мы вас оповестим.",reply_markup=keyword.as_markup())
        # await call.message.answer("⚙️ Вернуться в главное меню, напишите команду /start")
        await state.clear()
        await call.message.edit_reply_markup(reply_markup=None)
    elif call.data == "YesPhotoOne":
        keyword = createKeyboard([
            ("Нет", "StickerAdmin"),
            ("Да", "NoPhotoUser"),
        ], 2)

        await call.message.answer("❓Вы уверены в своем решение?", reply_markup=keyword.as_markup())
    elif call.data == 'EditPhoto':
        await call.message.answer("✏️Измените ваше изображения:")
        await state.update_data(name=F.data.text)
        await state.set_state(FSM.changeImg)
    elif call.data == "YesMsg":
        await call.message.answer("📝 Пришлите новый текст")
        await call.message.edit_reply_markup(reply_markup=None)
    elif call.data == "NoMsgOne":
        await call.message.edit_reply_markup(reply_markup=None)

        keyword = createKeyboard([
            ("Нет", "MsgAdmin"),
            ("Да", "DestroyMsg"),
        ], 2)

        await call.message.answer("Вы уверены в своем решение?", reply_markup=keyword.as_markup())
    elif call.data == "UpdateMSG":
        await state.update_data(name=F.data.text)
        await state.set_state(FSM.changeMsg)
        await call.message.answer("Измените ваше сообщение:")

@Callback_router.callback_query(F.data == "StickerAdmin")
async def sticker_admin(call: types.CallbackQuery, state: FSMContext) -> None:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM DataUsers")
            records = cursor.fetchall()
                # Можно добавить оповещение на будущее
            if records:
                await UpdateIDSQL({
                    "IDType": "IDimage"
                })
                # await call.message.delete()
                #await call.message.edit_reply_markup(reply_markup=None)

                keyword = createKeyNextLevel([
                    ("Нет", "YesPhotoOne"),
                    ("Да", "NoPhotoOne"),
                    ("Отправить в канал", "PhotoPublic"),
                ], 2,1)

                for row in records:
                    if row[9] == "1" and row[6] != None:
                        previous_image_pattern = f"{row[0]}_*.jpg"
                        for old_file in os.listdir('PhotoDB'):
                            if fnmatch(old_file, previous_image_pattern):
                                photo_file = FSInputFile(path=os.path.join('PhotoDB', old_file))
                                await call.message.answer_photo(photo=photo_file, caption=f"Пользователя: {int(row[0])} или {'@' + row[1]}\n"
                                  f"Стадия: {row[7]}\n"
                                    f"Вы хотите изменить сообщение?\n", reply_markup=keyword.as_markup())
                    '''elif row[9] == "-1" and row[6] == None and row[7] == None:
                        await call.message.answer(f"В таблице сообщений запросов. Проверьте запросы через некоторое время:)")'''


    except Exception as e:

        print(f"Error: {str(e)}")

@Callback_router.callback_query(F.data == "NoPhotoUser")
async def callback_query(call: types.CallbackQuery, state: FSMContext) -> None:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM DataUsers")
            records = cursor.fetchall()
            if records:
                for row in records:
                    if row[9] == "1":
                        await call.bot.send_message(chat_id=row[0],
                                                    text="😔Ваш стикер не приняли, напишите команду /start, чтобы перейти в главное меню.")

                        await update_data({
                            'UserID': row[0],
                            'Type': "Image",
                            'value': None,
                        })

                        await update_data({
                            'UserID': row[0],
                            'Type': "TypeAction",
                            'value': None,
                        })

                        await update_data({
                            'UserID': row[0],
                            'Type': "Stage",
                            'value': None,
                        })

                        await update_data({
                            'UserID': row[0],
                            'Type': "IDimage",
                            'value': "-1", # Возможно ошибка
                        })

                        previous_image_pattern = f"{row[0]}_*.jpg"

                        for old_file in os.listdir('PhotoDB'):
                            if fnmatch(old_file, previous_image_pattern):
                                os.remove(os.path.join('PhotoDB', old_file))

                        conn.commit()
    except Exception as e:
        print(f"Error: {e}")


@Callback_router.callback_query(F.data == "NoPhotoOne")
async def AnswerYesPhoto(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM DataUsers")
            records = cursor.fetchall()
            if records:
                for row in records:
                    if row[9] == "1":

                        await call.message.answer(f"Сообщение пользователя: ({int(row[0])} или {'@'+row[1]})")
                        previous_image_pattern = f"{row[0]}_*.jpg"

                        for old_file in os.listdir('PhotoDB'):
                            if fnmatch(old_file, previous_image_pattern):
                                photo_file = FSInputFile(path=os.path.join('PhotoDB', old_file))
                                await call.message.answer_photo(photo=photo_file)

                        keyword = createKeyboard([
                            ("Редактировать Фото", "EditPhoto"),
                            ("Отправить в канал","PhotoPublic"),
                            ("Назад", "StickerAdmin")
                        ],3)

                        await call.message.answer("Что вы хотите сделать?", reply_markup=keyword.as_markup())
    except Exception as e:
        print(f"Error: {e}")

@Callback_router.callback_query(F.data == "PhotoPublic")
async def EditPhoto(call: types.CallbackQuery, state: FSMContext):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM DataUsers")
            records = cursor.fetchall()
            if records:
                for row in records:
                    if row[9] == "1":
                        previous_image_pattern = f"{row[0]}_*.jpg"
                        for old_file in os.listdir('PhotoDB'):
                            if fnmatch(old_file, previous_image_pattern):
                                photo_file = FSInputFile(path=os.path.join('PhotoDB', old_file))
                                await call.bot.send_photo(chat_id=config.Chanaleid,photo=photo_file)
                                await call.bot.send_message(chat_id=row[0],
                                                            text="🥳Вашу картинку приняли, вы можете добавить новую! перейти в главное меню /start")

                        await update_data({
                            'UserID': row[0],
                            'Type': "Image",
                            'value': None,
                        })

                        await update_data({
                            'UserID': row[0],
                            'Type': "TypeAction",
                            'value': None,
                        })

                        await update_data({
                            'UserID': row[0],
                            'Type': "Stage",
                            'value': None,
                        })
                        await update_data({
                            'UserID': row[0],
                            'Type': "IDimage",
                            'value': "-1",  # Возможно ошибка
                        })

                        previous_image_pattern = f"{row[0]}_*.jpg"

                        for old_file in os.listdir('PhotoDB'):
                            if fnmatch(old_file, previous_image_pattern):
                                os.remove(os.path.join('PhotoDB', old_file))

                        conn.commit()

    except Exception as e:
            print(f"Error: {e}")


#! MSG SCRIPT

@Callback_router.callback_query(F.data == "MsgAdmin")
async def msg_admin(call: types.CallbackQuery) -> None:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM DataUsers")
            records = cursor.fetchall()
                # Можно добавить оповещение на будущее
            if records:
                await UpdateIDSQL({
                    'IDType': 'IDmsg'
                })
                # await call.message.delete()
                #await call.message.edit_reply_markup(reply_markup=None)

                keyword = createKeyNextLevel([
                    ("Нет", "NoMsgOne"),
                    ("Да", "YesMsgOne"),
                    ("Отправить в канал","MsgPublic")
                ], 2,1)

                for row in records:
                    if row[8] == "1" and row[5] != None:
                        await call.message.answer(f"Пользователя: {int(row[0])} или {'@' + row[1]}\n"
                          f"Сообщение пользователя: {row[5]}\n"
                          f"Стадия: {row[7]}\n\n"  f"Вы хотите изменить сообщение?\n"
                                                  , reply_markup=keyword.as_markup())



    except Exception as e:

        print(f"Error: {str(e)}")

@Callback_router.callback_query(F.data == "UDiaryBot")
async def UDiaryBotAnswer(call: types.CallbackQuery) -> None:
    keyword = createKeyboard([
        ("Вернуться в меню", "Main"),
    ], 1)
    await call.message.answer(f"✏️Ты учишься в МУИВ, и ты не пользуешься ботом UDiary?\n\n"
                       f"Это бот для расписания, в нем ты можешь быстро посмотреть расписание на всю неделю! \n\n"
                       f"Хочу предупредить, бот не является официальным! Возможно, расписание не точное, по этому следите на сайте или канале разработчика :)\n\n"
                       f"🤖 UDiary - @udiarybot\n"
                       f"ℹ️ Новости UDiary - @udiary_news\n"
                       f"🔍 Канал разработчика - @andrianovse\n", reply_markup=keyword.as_markup())

@Callback_router.callback_query(F.data == "Profile") # Добавить
async def ProfileAnswer(call: types.CallbackQuery) -> None:
    keyword = createKeyboard([
        ("Вернуться в меню", "Main"),
    ], 1)
    await call.message.answer(f"Информация об профиле:\n\n"
                              f"Ваше кол-во сообщений всего - 0\n"
                              f"Принятых сообщений - 0\n"
                              f"Откзано в сообщений - 0\n\n"
                              f"Ваше кол-во стикеров всего - 0\n"
                              f"Принятых стикеров - 0\n"
                              f"Откзано в стикерах - 0\n\n"
                              f"", reply_markup=keyword.as_markup())


# DELETE BASE DATA
@Callback_router.callback_query(F.data == "DeleteBase")
async def delete_base(call: types.CallbackQuery, state: FSMContext) -> None:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM DataUsers")
        records = cursor.fetchall()
        for record in records:
            await call.message.answer(record[1])

    await call.message.answer("Напишите ник пользователя:")
    await state.set_state(FSM.delet_Data)


@Callback_router.callback_query(F.data == "DestroyMsg")
async def AnswerDestroyMsg(call: types.CallbackQuery, state: FSMContext):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM DataUsers")
            records = cursor.fetchall()
            if records:
                for row in records:
                    if row[8] == "1":
                        await call.bot.send_message(chat_id=row[0], text="😔 Сообщение не принято, напишите команду /start, чтобы перейти в главное меню.")

                        await update_data({
                            'UserID': row[0],
                            'Type': "Message",
                            'value': None,
                        })

                        await update_data({
                            'UserID': row[0],
                            'Type': "TypeAction",
                            'value': None,
                        })

                        await update_data({
                            'UserID': row[0],
                            'Type': "Stage",
                            'value': None,
                        })
                        await update_data({
                            'UserID': row[0],
                            'Type': "IDmsg",
                            'value': "-1",
                        })

                        conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        
        
@Callback_router.callback_query(F.data == "YesMsgOne")
async def AnswerYesMsg(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=None)
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM DataUsers")
            records = cursor.fetchall()
            if records:
                for row in records:
                    if row[8] == "1":
                        await call.message.answer(f"Сообщение пользователя: ({int(row[0])} или {'@'+row[1]})")
                        await call.message.answer(row[5])

                        keyword = createKeyboard([
                            ("Редактировать", "UpdateMSG"),
                            ("Отправить в канал","MsgPublic"),
                            ("Назад", "MsgAdmin")
                        ],3)
                        await call.message.answer("Что вы хотите сделать?", reply_markup=keyword.as_markup())
    except Exception as e:
        print(f"Error: {e}")

@Callback_router.callback_query(F.data == "MsgPublic")
async def MsgChannel(call: types.CallbackQuery, state: FSMContext):
    try:
        await state.clear()  # Очищаем состояние после обработки
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM DataUsers")
            records = cursor.fetchall()
            for row in records:
                if row[8] == "1":
                    await call.bot.send_message(chat_id=config.Chanaleid, text=row[5])
                    await call.bot.send_message(chat_id=row[0], text="🥳 Сообщение принято! Поздравляю, вы можете написать новое сообщение :) /start")
                    # SAVE IN HISTORY REQUESTS

                    await update_data({
                        'UserID': row[0],
                        'Type': "Message",
                        'value': None,
                    })

                    await update_data({
                        'UserID': row[0],
                        'Type': "Stage",
                        'value': None,
                    })

                    await update_data({
                        'UserID': row[0],
                        'Type': "TypeAction",
                        'value': None,
                    })

                    await update_data({
                        'UserID': row[0],
                        'Type': "IDmsg",
                        'value': "-1",
                    })

                    conn.commit()

    except Exception as Er:
        print(f"Error: {Er}")