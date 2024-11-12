from aiogram.utils import keyboard

def createKeyboard(Buttons, index):
    keyword = keyboard.InlineKeyboardBuilder()

    for button_text, callback_data in Buttons:
        if callback_data.startswith("https"):
            keyword.button(text=button_text, url=callback_data)
            keyword.adjust(index)
        else:
            keyword.button(text=button_text, callback_data=callback_data)
            keyword.adjust(index)

    return keyword

def createKeyNextLevel(Buttons, index,indexMax):
    keyword = keyboard.InlineKeyboardBuilder()

    for button_text, callback_data in Buttons:
        if callback_data.startswith("https"):
            keyword.button(text=button_text, url=callback_data)
            keyword.adjust(index,indexMax)
        else:
            keyword.button(text=button_text, callback_data=callback_data)
            keyword.adjust(index,indexMax)

    return keyword



