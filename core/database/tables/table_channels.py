from core.database.database import DataBase

from core.logger_config import logger

from data.enums import KeyChannels


class DataBaseChannels(DataBase):
    table_name = "channels"

    def execute_table(self):
        if self.database:
            logger.info(f"Database: table '{self.table_name}' has been connected!")

        self.database.execute(f"""CREATE TABLE IF NOT EXISTS channels (
            {KeyChannels.channel_id} TEXT PRIMARY KEY,
            {KeyChannels.channel_tag} TEXT,
            {KeyChannels.channel_name} TEXT
            )""")
        self.database.commit()

    def get_channel_tags(self):
        self.cursor.execute(f"SELECT {KeyChannels.channel_tag} FROM channels")
        rows_tuples = self.cursor.fetchall()
        rows = []
        for i in range(len(rows_tuples)):
            rows.append(rows_tuples[i][0])
        return rows

    def get_all_channels_info(self):
        self.cursor.execute(
            f"SELECT {KeyChannels.channel_id}, {KeyChannels.channel_tag}, {KeyChannels.channel_name} FROM channels")
        rows = self.cursor.fetchall()
        return rows

    def add_channel_to_db(self, channel_id: str, channel_tag: str, channel_name: str):
        self.cursor.execute(
            f"INSERT INTO channels({KeyChannels.channel_id}, {KeyChannels.channel_tag}, {KeyChannels.channel_name}) "
            f"VALUES('{channel_id}', '{channel_tag}', '{channel_name}')")
        self.database.commit()

    def del_channel(self, channel_id: str):
        self.cursor.execute(f"DELETE FROM channels WHERE {KeyChannels.channel_id} = '{channel_id}'")
        self.database.commit()



