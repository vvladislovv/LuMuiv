import asyncio, logging, os, sys, random, config
from dotenv import load_dotenv
# aiogram
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils import keyboard
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

#From import router
from handlers.Callback import Callback_router
from handlers.FSM import FSMBot, FSM
from handlers.DataBase import  UsingBot, add_user_database, update_data
from handlers.Keyboard import reply_markup, createKeyboard, createKeyNextLevel

async def MainDataBase(message) ->None:
    DataUser = {
        "UserID": message.from_user.id,
        "Name": message.from_user.username,
        "full_name": message.from_user.full_name,
        "TypeAction": None,
        "UsingBotN": 0
    }
    await add_user_database(DataUser)
load_dotenv()
Token = os.getenv('TOKEN')

dp = Dispatcher()

@dp.message(CommandStart())  # /start
async def command_start_handler(message: Message, state: FSMContext) -> None:
    # Проверка подписки на канала
    try:
        chat_member = await message.bot.get_chat_member(config.Chanaleid, message.from_user.id)
        if chat_member.status not in ["member", "administrator", "creator"]:
            keyword = createKeyboard([
                ("Подслушано МУИВ", "https://t.me/muivvvv"),
                ], 1)

            await message.answer(

                "😫Тебя нет в канале, подпишись на наш канал. После этого ты сможешь пользоваться этим ботом!",
                reply_markup=keyword.as_markup())
        else:
            # Create BaseData if haven't is it
            await MainDataBase(message)

            keyword = createKeyNextLevel([
                ("😊 Новый стикер", "Sticker"),
                ("💭 Новые сообщение", "Msg"),
                ("📕 UDiary - Бот по расписанию", "UDiaryBot"),
                #("⚙️ Профиль", "Profile")
            ], 2, 1)


            await message.answer("👋 Привет! Выберите интересующее действие:)", reply_markup=keyword.as_markup())

            CountUsing = UsingBot(message.from_user.username)
            await update_data({
                'UserID': message.from_user.id,
                'Type': "NBotUsage",
                'value': CountUsing+1,
            })

    except Exception as e:
        print(f"Error checking membership: {e}")
        return

@dp.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext) -> None:
    for _, admin_info in config.Admins.items():
        if admin_info['ID'] == message.from_user.id:
            Rand = random.randint(1, 9999)
            await message.answer(f"Ваш код: <tg-spoiler>{Rand}</tg-spoiler>", parse_mode='HTML')
            admin_info['Key'] = Rand
            await state.update_data(name=message.text)
            await state.set_state(FSM.waitCode)
            await message.answer("Напишите ваш код администраторов:")


async def main() -> None:
    bot = Bot(token=Token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.include_routers(Callback_router,FSMBot)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
