import os, shutil
from datetime import datetime
from fnmatch import fnmatch
from handlers.DataBase import get_db_connection

async def GetPhoto(Specifications: dict) -> dict:

    file_id = Specifications.get('file_id')
    file_info = await Specifications['msg'].bot.get_file(file_id)  # Получаем информацию о файле
    file_path = file_info.file_path
    photo_url = f'https://api.telegram.org/file/bot{os.getenv("TOKEN")}/{file_path}'

    save_directory = 'PhotoDB'
    os.makedirs(save_directory, exist_ok=True)

    unique_filename = f"{Specifications['msg'].from_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    image_file_path = os.path.join(save_directory, unique_filename)

    previous_image_pattern = f"{Specifications['msg'].from_user.id}_*.jpg"

    await download_file(photo_url, image_file_path)

    for old_file in os.listdir(save_directory):
        if fnmatch(old_file, previous_image_pattern):
            os.remove(os.path.join(save_directory, old_file))

    return {
        'unique_filename': unique_filename,
        'image_file_path': image_file_path,
        'previous_image_pattern': previous_image_pattern,
        'photo_url': photo_url
    }


async def download_file(photo_url: str, save_path: str):
    import aiohttp
    with get_db_connection() as conn:
        async with aiohttp.ClientSession() as session:
            async with session.get(photo_url) as response:
                if response.status == 200:
                    with open(save_path, 'wb') as f:
                        f.write(await response.read())