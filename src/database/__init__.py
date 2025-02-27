import mysql.connector
from database.db_tables import *
from tools.logging import logger, dedent

class Manager:
    def __init__(self, connection=None):
        self.connection = connection

    def get_table_column_names(self, table_name):
        data = []
        try:
            logger.info(f"Формирование запроса к '{table_name}' для получения таблиц.")
            cursor = self.connection.cursor()
            value = [table_name]
            query = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = %s"
            logger.info(f"Отправка запроса к '{table_name}':\n{dedent(query)}")
            cursor.execute(query, value)
            data = [column[0] for column in cursor.fetchall()]
            logger.info(f"Ответ от '{table_name}':\n{data}")
        except mysql.connector.Error as err:
            logger.error(f"Запрос к таблице '{table_name}' проваленен:{err}.")
            raise err
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            return data

    def get_table_rows(self, main_table_name, joined_tables={}):
        data = []
        try:
            logger.info(f"Формирование запроса к '{main_table_name}'.")
            column_names = [f"{main_table_name}.{column_name}" for column_name in self.get_table_column_names(main_table_name)]
            for join_table in joined_tables:
                joined_table_name = join_table["join_table_name"]
                column_names.extend([f"{joined_table_name}.{column_name}" for column_name in self.get_table_column_names(joined_table_name)])
            cursor = self.connection.cursor()
            query=f"""
            SELECT {", ".join(column_names)}
            FROM {main_table_name}
            """
            for join_table in joined_tables:
                query += f"""
                JOIN {join_table["join_table_name"]}
                ON {join_table["join_table_column"]} = {join_table["main_table_column"]}
                """
            logger.info(f"Отправка запроса к '{main_table_name}':\n{dedent(query)}")
            cursor.execute(query)
            data = [dict(zip(column_names, row)) for row in cursor.fetchall()]
            logger.info(f"Ответ от '{main_table_name}':\n{data}")
        except mysql.connector.Error as err:
            logger.error(f"Запрос к таблице '{main_table_name}' проваленен:{err}.")
            raise err
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            return data

    def get_referenced_row_rows(self, referenced_table_name, row):
        data = []
        try:
            logger.info("Формирование запроса к базе данных за зависимыми записями.")
            cursor = self.connection.cursor(dictionary=True)
            value = [referenced_table_name]
            query = """
            SELECT
                REFERENCED_TABLE_NAME AS referenced_table_name,
                REFERENCED_COLUMN_NAME AS referenced_column_name,
                TABLE_NAME AS table_name,
                COLUMN_NAME AS column_name
            FROM 
                INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE 
                REFERENCED_TABLE_NAME = %s
                AND TABLE_NAME IS NOT NULL;
            """
            logger.info(f"Отправка основного запроса к '{referenced_table_name}':\n{dedent(query)}\n{value}")
            cursor.execute(query, value)
            for temp in cursor.fetchall():
                data.append({
                        "referenced_table_name": referenced_table_name,
                        "referenced_column_name": f"{temp['referenced_table_name']}.{temp['referenced_column_name']}",
                        "main_table_name": temp['table_name'],
                        "main_table_rows": [column for column in self.get_table_rows(temp['table_name']) if column[temp['column_name']] == row[f"{temp['referenced_table_name']}.{temp['referenced_column_name']}"]],
                        "main_column_name": f"{temp['table_name']}.{temp['column_name']}",
                    }
                )
            logger.info(f"Ответ основного запроса от '{referenced_table_name}':\n{data}")
        except mysql.connector.Error as err:
            logger.error(f"Запрос к таблице '{referenced_table_name}' проваленен:{err}.")
            raise err
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            logger.info(f"Ответ от '{referenced_table_name}':\n{data}")
            return data

    def get_table_row_dependens(self, table_name):
        data = []
        try:
            logger.info("Формирование запроса к базе данных за зависимыми записями.")
            cursor = self.connection.cursor(dictionary=True)
            value = [table_name]
            query = """
            SELECT
                REFERENCED_TABLE_NAME AS referenced_table_name,
                REFERENCED_COLUMN_NAME AS referenced_column_name,
                TABLE_NAME AS table_name,
                COLUMN_NAME AS column_name
            FROM 
                INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE 
                TABLE_NAME = %s
                AND REFERENCED_TABLE_NAME IS NOT NULL;
            """
            logger.info(f"Отправка основного запроса к '{table_name}':\n{dedent(query)}\n{value}")
            cursor.execute(query, value)
            temp = cursor.fetchall()
            for row in temp:
                data.append({
                        "referenced_table_name": row['referenced_table_name'],
                        "referenced_table_rows": self.get_table_rows(row['referenced_table_name']),
                        "referenced_column_name": f"{row['referenced_table_name']}.{row['referenced_column_name']}",
                        "main_column_name": f"{table_name}.{row['column_name']}",
                    }
                )
            logger.info(f"Ответ основного запроса от '{referenced_table_name}':\n{data}")
        except mysql.connector.Error as err:
            logger.error(f"Запрос к таблице '{table_name}' проваленен:{err}.")
            raise err
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            logger.info(f"Ответ от '{table_name}':\n{data}")
            return data

    def add_table_row(self, table_name, row):
        try:
            logger.info(f"Формирование запроса к '{table_name}'.")
            cursor = self.connection.cursor()
            columns = ", ".join(row.keys())
            placeholders = ", ".join(["%s"] * len(row))
            values = list(map(lambda x: None if x == "" else x, row.values()))
            query = f"""
            INSERT INTO {table_name} ({columns})
            VALUES ({placeholders})
            """
            logger.info(f"Отправка запроса к '{table_name}':\n{dedent(query)}\n{values}")
            cursor.execute(query, values)
            self.connection.commit()
            logger.info(f"Операция успешна")
        except mysql.connector.Error as err:
            logger.error(f"Запрос к таблице '{table_name}' проваленен:{err}.")
            raise err
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def update_table_row(self, table_name, row, primary_columns=[]):
        try:
            logger.info(f"Формирование запроса к '{table_name}'.")
            cursor = self.connection.cursor()
            set_row = ", ".join([f"{key} = %s" for key in row.keys() if key not in primary_columns])
            where_clause = " AND ".join([f"{key} = %s" for key in primary_columns])
            values = [row[key] for key in row.keys() if key not in primary_columns] + [row[key] for key in primary_columns]
            values = list(map(lambda x: None if x == "" else x, values))
            query = f"""
            UPDATE {table_name}
            SET {set_row}
            WHERE {where_clause}
            """
            logger.info(f"Отправка запроса к '{table_name}':\n{dedent(query)}\n{values}")
            cursor.execute(query, values)
            self.connection.commit()
            logger.info(f"Операция успешна")
        except mysql.connector.Error as err:
            logger.error(f"Запрос к таблице '{table_name}' проваленен:{err}.")
            raise err
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def delete_table_rows(self, table_name, primary_columns={}):
        try:
            logger.info(f"Формирование запроса к '{table_name}'.")
            cursor = self.connection.cursor()
            where_clause = " AND ".join([f"{key} = %s" for key in primary_columns.keys()])
            values = list(primary_columns.values())
            query = f"""
            DELETE FROM {table_name}
            WHERE {where_clause}
            """
            logger.info(f"Отправка запроса к '{table_name}':\n{dedent(query)}\n{values}")
            cursor.execute(query, values)
            self.connection.commit()
            logger.info(f"Операция успешна")
        except mysql.connector.Error as err:
            logger.error(f"Запрос к таблице '{table_name}' проваленен:{err}.")
            raise err
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def get_user(self, login):
        data = []
        try:
            logger.info(f"Формирование запроса к таблице пользователей.")
            cursor = self.connection.cursor()
            query = """
            SELECT role_name, password_hash FROM users
                JOIN roles ON users.user_id = roles.role_id
                WHERE login = %s;
            """
            value = [login]
            logger.info(f"Отправка запроса к таблице пользователей':\n{dedent(query)}\n{value}")
            cursor.execute(query, value)
            data = cursor.fetchone()
            logger.info(f"Ответ от таблицы пользователей:\n{data}")
        except mysql.connector.Error as err:
            logger.error(f"Запрос к таблице пользователей проваленен:{err}.")
            raise err
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            return data

class Database:
    def __init__(self, setting_db):
        self.is_connected = False
        self.setting_db = setting_db
        self.manager = Manager()
        self.connect()

    def connect(self, setting_db=None):
        try:
            if not setting_db:
                setting_db = self.setting_db
            self.manager.connection = mysql.connector.connect(**setting_db)
            self.is_connected = True
            self.setting_db = setting_db
            logger.info(f"Подключение к базе данных '{setting_db["database"]}' успешно.")
        except mysql.connector.Error as err:
            self.manager.connection = None
            self.is_connected = False
            logger.error(f"Подключение к базе данных '{setting_db["database"]}' проваленно.")

