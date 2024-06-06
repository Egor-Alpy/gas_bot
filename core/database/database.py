from sqlite3 import Connection, Cursor  # Используются только для аннотации


class DataBase:
    def __init__(self, connect: Connection, cur: Cursor) -> None:
        self.database = connect
        self.cursor = cur
