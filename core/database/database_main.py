import sqlite3 as sq

from core.database.tables.table_users import DataBaseUsers


FILENAME_DATABASE = "data/database/database.db"

connection = sq.connect(FILENAME_DATABASE)
cursor = connection.cursor()

table_users = DataBaseUsers(connection, cursor)

for table in [table_users]:
    table.execute_table()
