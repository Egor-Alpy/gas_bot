from core.database.database import DataBase

from core.logger_config import logger

from data.enums import KeyUsers


class DataBaseUsers(DataBase):
    table_name = "users"

    def execute_table(self):
        if self.database:
            logger.info(f"Database: table '{self.table_name}' has been connected!")

        self.database.execute(f"""CREATE TABLE IF NOT EXISTS users (
            {KeyUsers.user_id} TEXT PRIMARY KEY,
            {KeyUsers.username} TEXT,
            {KeyUsers.name} TEXT,
            {KeyUsers.surname} TEXT,
            {KeyUsers.interval} INT DEFAULT {30},
            {KeyUsers.subscribed} TEXT DEFAULT False,
            {KeyUsers.language} TEXT DEFAULT RUS
            )""")
        self.database.commit()

    def add_user(self, user_id: int, username: str, name: str, surname: str):
        self.cursor.execute(
            f"INSERT INTO users({KeyUsers.user_id}, {KeyUsers.username}, {KeyUsers.name}, {KeyUsers.surname}) VALUES({user_id}, '{username}', '{name}', '{surname}')")
        self.database.commit()

    def get_user_id_by_time(self, time):
        self.cursor.execute(f"SELECT {KeyUsers.user_id} FROM users WHERE {time} % interval < 30")
        rows_tuples = self.cursor.fetchall()
        rows = []
        for i in range(len(rows_tuples)):
            rows.append(rows_tuples[i][0])
        print(rows)
        return rows

    def get_all_user_id(self):
        self.cursor.execute(f"SELECT {KeyUsers.user_id} FROM users")
        rows_tuples = self.cursor.fetchall()
        rows = []
        for i in range(len(rows_tuples)):
            rows.append(rows_tuples[i][0])
        return rows

    def get_user_interval(self, user_id):
        self.cursor.execute(f"SELECT {KeyUsers.interval} FROM users WHERE user_id = {user_id}")
        row = self.cursor.fetchall()
        return row[0][0]

    def set_new_interval(self, user_id, interval):
        self.cursor.execute(
            f"UPDATE users SET {KeyUsers.interval} = '{interval}' WHERE {KeyUsers.user_id} = '{user_id}'")
        self.database.commit()

    def set_subscription_status(self, subscription_status, user_id):
        self.cursor.execute(
            f"UPDATE users SET {KeyUsers.subscribed} = '{subscription_status}' WHERE {KeyUsers.user_id} = '{user_id}'")
        self.database.commit()

    def get_subscription_status(self, user_id):
        self.cursor.execute(f"SELECT {KeyUsers.subscribed} FROM users WHERE {KeyUsers.user_id} = {user_id}")
        row = self.cursor.fetchall()
        if row:
            return row[0][0]
        return

    def get_user_language(self, user_id: str):
        self.cursor.execute(f"SELECT {KeyUsers.language} FROM users WHERE {KeyUsers.user_id} = '{user_id}'")
        row = self.cursor.fetchall()
        if row:
            print(row[0][0])
            return row[0][0]

    def set_new_language(self, user_id, language):
        self.cursor.execute(
            f"UPDATE users SET {KeyUsers.language} = '{language}' WHERE {KeyUsers.user_id} = '{user_id}'")
        self.database.commit()