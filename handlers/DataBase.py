import sqlite3, os

def get_db_connection():
    db_relative_path = 'DataUsers.db'
    script_dir = "DataBase"
    db_path = os.path.join(script_dir, db_relative_path)
    return sqlite3.connect(db_path)

def create_table():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS DataUsers (
            UserID INTEGER PRIMARY KEY,
            Name TEXT,
            User_Name TEXT,
            TypeAction TEXT,
            NBotUsage TEXT,
            Message TEXT,
            Image TEXT,
            Stage TEXT,
            IDmsg TEXT,
            IDimage TEXT
        )
        ''')

def UsingBot(Username : str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT NBotUsage FROM DataUsers WHERE Name = ?', (Username,))
        result = cursor.fetchone()
        return int(result[0])

async def GetUsers(records: tuple):
    for row in records:
        yield row

async def GetDataUser(records: tuple):
    for row in records:
        return row


async def FindUserData(message) -> tuple:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM DataUsers WHERE UserID = ?", (message.from_user.id,))
            records = cursor.fetchall()
            return records
    except Exception as eerrr:
        print(f"Error {eerrr}")


async def UpdateIDSQL(IDtab : dict) -> None:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM DataUsers")
        recordss = cursor.fetchall()
        Quantity = 0
        async for user in GetUsers(recordss):
            DataSQL : tuple = user
            if IDtab['IDType'] == "IDimage": #DataSQL[7] == "Expectation"
                if  DataSQL[6] != None:
                    Quantity += 1
                    cursor.execute(
                        f"UPDATE DataUsers SET {"IDimage"} = ? WHERE UserID = ?",
                        (Quantity, DataSQL[0]))
                    conn.commit()
            elif IDtab['IDType']  == "IDmsg":
                if DataSQL[5] != None:
                    Quantity += 1
                    cursor.execute(
                        f"UPDATE DataUsers SET {"IDmsg"} = ? WHERE UserID = ?",
                        (Quantity, DataSQL[0]))
                    conn.commit()

def DeleatUserData(username : str) -> bool:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM DataUsers WHERE Name = ?', (username,))
        conn.commit()
        return True

def SelectData(username : str) -> tuple:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM DataUsers WHERE Name=?", (username,))
        return cursor.fetchone()

async def update_data(data) -> None:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("PRAGMA table_info(DataUsers);")
            columns = [column[1] for column in cursor.fetchall()]

            # update_data -- TYPE название для столбика

            if data['Type'] not in columns:
                cursor.execute(f"ALTER TABLE DataUsers ADD COLUMN {data['Type']} TEXT")

            cursor.execute(f"UPDATE DataUsers SET {data['Type']} = ? WHERE UserID = ?",
                           (data['value'],  data['UserID']))
            conn.commit()
    except Exception as e:
        print(f"An error occurred during update: {str(e)}")



async def add_user_database(data_user) -> None:
    try:
        create_table()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM DataUsers WHERE UserID = ?", (data_user["UserID"],))
            if cursor.fetchone() is None:
                cursor.execute(''' INSERT INTO DataUsers (UserID, Name, User_Name, TypeAction, NBotUsage,IDmsg,IDimage) VALUES (?, ?, ?, ?, ?,?,?) ''', (data_user["UserID"], data_user["Name"], data_user["full_name"], data_user["TypeAction"], data_user["UsingBotN"],data_user["UsingBotN"],data_user["UsingBotN"]))
                conn.commit()


                print("Пользователь добавлен в базу данных.")
    except Exception as e:
        print(f"Error {str(e)}")