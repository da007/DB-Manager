import mysql.connector
from database.db_tables import *
from tools.logging import logger, dedent

class Manager:
    def __init__(self, connection=None):
        self.connection = connection

    def get_table_rows(self, table_name, columns_str="*", join_tables=[]):
        data = []
        try:
            logger.info(f"Формирование запроса к '{table_name}'.")
            cursor = self.connection.cursor(dictionary=True)
            query = f"""
            SELECT {columns_str}
            FROM {table_name}
            """
            if join_tables:
                for join_table in join_tables:
                    query += f"""
                    JOIN {join_table['referenced_table_name']} 
                    ON {join_table['referenced_table_name']}.{join_table['referenced_column_name']} = 
                       {table_name}.{join_table['column_name']}
                    """
            logger.info(f"Отправка запроса к '{table_name}':\n{dedent(query)}")
            cursor.execute(query)
            data = cursor.fetchall()
            logger.info(f"Ответ от '{table_name}':\n{data}")
        except mysql.connector.Error as err:
            logger.error(f"Запрос к таблице '{table_name}' проваленен:{err}.")
            raise err
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            return data

    def get_primary_columns(self, table_name):
        data = []
        try:
            logger.info(f"Формирование запроса для получения PRIMARY KEY таблицы {table_name}.")
            cursor = self.connection.cursor()
            query = """
            SELECT
            COLUMN_NAME as column_name
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = %s
              AND COLUMN_KEY IN ('PRI');
            """
            logger.info(f"Отправка запроса для получения PRIMARY KEY:\n{dedent(query)}")
            cursor.execute(query, (table_name,))
            data = list(cursor.fetchall()[0])
            logger.info(f"Ответ от запроса для получения PRIMARY KEY:\n{data}")
        except mysql.connector.Error as err:
            logger.error(f"Запрос для получения PRIMARY KEY проваленен:{err}.")
            raise err
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            return data

    def get_referenced_row_rows(self, table_name, row):
        data = []
        table_row_dependens = self.get_table_row_dependens(table_name)
        for table_row_dependen in table_row_dependens:
            referenced_rows = table_row_dependen["referenced_table_rows"]
            referenced_column_name = table_row_dependen["referenced_column_name"]
            column_name = table_row_dependen["column_name"]
            referenced_table_rows = []
            for referenced_row in referenced_rows:
                if referenced_row[referenced_column_name] == row[column_name]:
                    referenced_table_rows.append(referenced_row)
            data.append({
                "referenced_table_name": table_row_dependen["referenced_table_name"],
                "referenced_table_rows": referenced_table_rows,
                "referenced_column_name": referenced_column_name,
                "table_name": table_row_dependen["table_name"],
                "column_name": column_name,
            })
        logger.info(f"Ответ от '{table_name}':\n{data}")
        return data

    def get_table_row_dependens(self, table_name):
        data = []
        try:
            logger.info(f"Формирование запроса к базе данных за зависимыми записями.")
            cursor = self.connection.cursor(dictionary=True)
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
            logger.info(f"Отправка основного запроса к '{table_name}':\n{dedent(query)}")
            cursor.execute(query, (table_name,))
            temp = cursor.fetchall()
            for row in temp:
                logger.info(f"Формирование запроса к '{row['referenced_table_name']}'.")
                temp_query = """
                SELECT *
                FROM %s
                """
                logger.info(f"Отправка запроса к '{table_name}':\n{dedent(query)}")
                cursor.execute(temp_query, (row['referenced_table_name'],))
                data.append({
                        "referenced_table_name": row['referenced_table_name'],
                        "referenced_table_rows": cursor.fetchall(),
                        "referenced_column_name": row['referenced_column_name'],
                        "table_name": row['table_name'],
                        "column_name": row['column_name'],
                    }
                )
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
            values = list(row.values())
            query = f"""
            INSERT INTO {table_name} ({columns})
            VALUES ({placeholders})
            """
            logger.info(f"Отправка запроса к '{table_name}':\n{dedent(query)}")
            cursor.execute(query, values)
            self.connection.commit()
            logger.info(f"Операция успешна")
        except mysql.connector.Error as err:
            logger.error(f"Запрос к таблице '{table_name}' проваленен:{err}.")
            raise err
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def update_table_row(self, table_name, row):
        try:
            logger.info(f"Формирование запроса к '{table_name}'.")
            primary_columns = self.get_primary_columns(table_name)
            cursor = self.connection.cursor()
            set_row = ", ".join([f"{key} = %s" for key in row.keys() if key not in primary_columns])
            where_clause = " AND ".join([f"{key} = %s" for key in primary_columns])
            values = [row[key] for key in row.keys() if key not in primary_columns] + [row[key] for key in primary_columns]
            query = f"""
            UPDATE {table_name}
            SET {set_row}
            WHERE {where_clause}
            """
            logger.info(f"Отправка запроса к '{table_name}':\n{dedent(query)}")
            cursor.execute(query, values)
            self.connection.commit()
            logger.info(f"Операция успешна")
        except mysql.connector.Error as err:
            logger.error(f"Запрос к таблице '{table_name}' проваленен:{err}.")
            raise err
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()

    def delete_table_rows(self, table_name, row):
        try:
            logger.info(f"Формирование запроса к '{table_name}'.")
            primary_columns = self.get_primary_columns(table_name)
            cursor = self.connection.cursor()
            where_clause = " AND ".join([f"{key} = %s" for key in primary_columns])
            values = [row[key] for key in primary_columns]
            query = f"""
            DELETE FROM {table_name}
            WHERE {where_clause}
            """
            logger.info(f"Отправка запроса к '{table_name}':\n{dedent(query)}")
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
            value = (login,)
            logger.info(f"Отправка запроса к таблице пользователей':\n{dedent(query)}")
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

