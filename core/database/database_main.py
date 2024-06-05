import sqlite3 as sq

from core.database.tables.table_users import DataBaseUsers
from core.database.tables.table_channels import DataBaseChannels


FILENAME_DATABASE = "data/database/database.db"

connection = sq.connect(database=FILENAME_DATABASE, check_same_thread=False)
cursor = connection.cursor()

table_users = DataBaseUsers(connection, cursor)
table_channels = DataBaseChannels(connection, cursor)

for table in [table_users, table_channels]:
    table.execute_table()
