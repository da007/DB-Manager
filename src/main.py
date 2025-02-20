import flet as ft
import mysql.connector
import Levenshtein
import json
import re
import bcrypt
from cryptography.fernet import Fernet

class RepairShopApp:

    theme_modes = {
        "Светлая стандартная": ft.ThemeMode.LIGHT,
        "Темная стандартная": ft.ThemeMode.DARK
    }
    themes = {
        "Индиго": ft.Theme(
            color_scheme_seed=ft.Colors.INDIGO,
            use_material3=True,
        ),
        "Фиолетовая ночь": ft.Theme(
            color_scheme_seed=ft.Colors.DEEP_PURPLE,
            use_material3=True,
        ),
        "Лесная зелень": ft.Theme(
            color_scheme_seed=ft.Colors.GREEN,
            use_material3=True,
        ),
        "Песчаный берег": ft.Theme(
            color_scheme_seed=ft.Colors.AMBER,
            use_material3=True,
        ),
        "Лазурный бриз": ft.Theme(
            color_scheme_seed=ft.Colors.BLUE_400,
            use_material3=True,
        ),
        "Тестовый": ft.Theme(
            color_scheme_seed=ft.Colors.random(),
            use_material3=True
        ),
    }

    logos_modes = {
        "Светлая стандартная": r"source\img\logo\light_default.png",
        "Темная стандартная": r"source\img\logo\dark_default.png"
    }

    setting_default = {
        "app": {
            "theme_mode": "Темная стандартная",
            "theme": "Индиго"
        },
        "db": {
            "host": "localhost",
            "user": "User", 
            "password": "1pq0", 
            "database": "repair_shop"
        }
    }

    column_names = {
        'spare_part_id': 'ID запчасти',
        'part_name': 'Название запчасти',
        'description': 'Описание',
        'manufacturer': 'Производитель',
        'part_number': 'Номер запчасти',
        'quantity_in_stock': 'Кол-во на складе',
        'purchase_price': 'Цена закупки',
        'selling_price': 'Цена продажи',
        'compatible_devices': 'Совместимые устр.',
        'client_id': 'ID клиента',
        'first_name': 'Имя',
        'last_name': 'Фамилия',
        'phone_number': 'Номер телефона',
        'email': 'Эл. почта',
        'address': 'Адрес',
        'notes': 'Заметки',
        'order_id': 'ID заказа',
        'device_id': 'ID устройства',
        'employee_id': 'ID сотрудника',
        'assigned_employee_id': 'Назнач. сотрудник',
        'status_id': 'ID статуса',
        'date_created': 'Дата создания',
        'date_completed': 'Дата завершения',
        'problem_description': 'Описание проблемы',
        'diagnosis': 'Диагноз',
        'total_price': 'Общая цена',
        'quantity_used': 'Использ. кол-во',
        'price_per_unit': 'Цена за единицу',
        'device_type_id': 'ID типа устр.',
        'brand': 'Бренд',
        'model': 'Модель',
        'serial_number': 'Серийный номер',
        'position': 'Должность',
        'hire_date': 'Дата найма',
        'is_active': 'Активен',
        'service_id': 'ID услуги',
        'service_name': 'Название услуги',
        'price': 'Цена',
        'is_hardware': 'Аппаратное',
        'type_name': 'Тип устройства',
        'status_name': 'Название статуса',
        'role_id': 'ID роли',
        'role_name': 'Название роли',
        'user_id': 'ID юзера',
        'login': 'логин',
        'password_hash': 'хеш пароля',
    }

    regex_patterns = {
        "int": r"^\d+$",
        "positive_int": r"^[1-9]\d*$",
        "float": r"^\d+(\.\d{1,2})?$",
        "text": r"^[\w\s.,!?\-()]+$",
        "name": r"^[a-zA-Zа-яА-Я\s\-]+$",
        "phone": r"^\+?\d[\d\s()\-]+$",
        "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "date": r"^\d{4}-\d{2}-\d{2}$",
        "datetime": r"^\d{4}-\d{2}-\d{2}$",
        "part_number": r"^[\w\s.\-/]+$",
        "serial_number": r"^[\w\s.\-/]+$",
        "boolean": r"^(0|1)$",
        "any": r"^.*$",
    }

    column_mapping = {
        'spare_part_id': "int",
        'part_name': "text",
        'description': "text",
        'manufacturer': "text",
        'part_number': "part_number",
        'quantity_in_stock': "positive_int",
        'purchase_price': "float",
        'selling_price': "float",
        'compatible_devices': "text",
        'client_id': "int",
        'first_name': "name",
        'last_name': "name",
        'phone_number': "phone",
        'email': "email",
        'address': "text",
        'notes': "text",
        'order_id': "int",
        'device_id': "int",
        'employee_id': "int",
        'assigned_employee_id': "int",
        'status_id': "int",
        'date_created': "datetime",
        'date_completed': "datetime",
        'problem_description': "text",
        'diagnosis': "text",
        'total_price': "float",
        'quantity_used': "positive_int",
        'price_per_unit': "float",
        'device_type_id': "int",
        'brand': "text",
        'model': "text",
        'serial_number': "serial_number",
        'position': "text",
        'hire_date': "date",
        'is_active': "boolean",
        'service_id': "int",
        'service_name': "text",
        'price': "float",
        'is_hardware': "boolean",
        'type_name': "text",
        'status_name': "text",
        'role_id': "int",
        'role_name': "text",
        'user_id': "int",
        'login': "login",
        'password_hash': "any",
    }

    tables = {
        "clients": {
            "name": "Клиенты", 
            "label_on_choose": ['first_name', 'last_name'],
            "view_columns": "clients.client_id, clients.first_name, clients.last_name, clients.phone_number, clients.email, clients.address, clients.notes",
            "nessesary_columns": ['first_name', 'last_name'],
            "passed_columns": ['client_id'],
            "join_tables": [],
        },
        "devices": {
            "name": "Устройства", 
            "label_on_choose": ['device_type_id', "serial_number"],
            "view_columns": "devices.device_id, devices.brand, devices.model, devices.serial_number, devices.description, device_types.type_name",
            "nessesary_columns": ['device_type_id', 'brand', 'model'],
            "passed_columns": ['device_id'],
            "join_tables": [{
                    "referenced_table_name": "device_types",
                    "referenced_column_name": "device_type_id",
                    "column_name": "device_type_id"
                }
            ],
        },
        "device_types": {
            "name": "Типы устройств", 
            "label_on_choose": ['type_name'],
            "view_columns": "device_types.device_type_id, device_types.type_name",
            "nessesary_columns": ['type_name'],
            "passed_columns": ['device_type_id'],
            "join_tables": [],
        },
        "employees": {
            "name": "Сотрудники", 
            "label_on_choose": ['first_name', 'last_name'],
            "view_columns": "employees.employee_id, employees.first_name, employees.last_name, employees.position, employees.phone_number, employees.email, employees.hire_date, employees.is_active",
            "nessesary_columns": ['first_name', 'last_name', 'position', 'hire_date'],
            "passed_columns": ['employee_id'],
            "join_tables": [],
        },
        "order_spare_parts": {
            "name": "Заказы запчастей", 
            "label_on_choose": ['order_id', 'spare_part_id', 'quantity_used', 'price_per_unit'],
            "view_columns": "order_spare_parts.order_id, order_spare_parts.spare_part_id, order_spare_parts.quantity_used, order_spare_parts.price_per_unit, spare_parts.part_name",
            "nessesary_columns": ['order_id', 'spare_part_id', 'quantity_used', 'price_per_unit'],
            "passed_columns": [],
            "join_tables": [{
                    "referenced_table_name": "spare_parts",
                    "referenced_column_name": "spare_part_id",
                    "column_name": "spare_part_id"
                }
            ],
        },
        "order_services": {
            "name": "Заказы услуг", 
            "label_on_choose": ['order_id', 'service_id', 'price'],
            "view_columns": "order_services.order_id, order_services.service_id, order_services.price, services.service_name",
            "nessesary_columns": ['order_id', 'service_id', 'price'],
            "passed_columns": [],
            "join_tables": [{
                    "referenced_table_name": "services",
                    "referenced_column_name": "service_id",
                    "column_name": "service_id"
                }
            ],
        },
        "statuses": {
            "name": "Статусы", 
            "label_on_choose": ["status_name"],
            "view_columns": "statuses.status_id, statuses.status_name",
            "nessesary_columns": ['status_name'],
            "passed_columns": ['status_id'],
            "join_tables": [],
        },
        "spare_parts": {
            "name": "Запчасти", 
            "label_on_choose": ["spare_part_id, part_name"],
            "view_columns": "spare_parts.spare_part_id, spare_parts.part_name, spare_parts.description, spare_parts.manufacturer, spare_parts.part_number, spare_parts.quantity_in_stock, spare_parts.purchase_price, spare_parts.selling_price, spare_parts.compatible_devices",
            "nessesary_columns": ['part_name', 'quantity_in_stock', 'purchase_price', 'selling_price'],
            "passed_columns": ['spare_part_id'],
            "join_tables": [],
        },
        "services": {
            "name": "Услуги", 
            "label_on_choose": ["service_name"],
            "view_columns": "services.service_id, services.service_name, services.description, services.price, services.is_hardware",
            "nessesary_columns": ['service_name', 'price'],
            "passed_columns": ['service_id'],
            "join_tables": [],
        },
        "orders": {
            "name": "Заказы", 
            "label_on_choose": ["order_id, problem_description"],
            "view_columns": "orders.order_id, orders.problem_description, orders.diagnosis, orders.total_price, orders.notes, clients.first_name, clients.last_name, devices.brand, devices.model, employees.first_name, employees.last_name, statuses.status_name, orders.date_created",
            "nessesary_columns": ['client_id', 'device_id', 'employee_id', 'status_id', 'date_created', 'total_price'],
            "passed_columns": ['order_id', 'date_created'],
            "join_tables": [{
                    "referenced_table_name": "clients",
                    "referenced_column_name": "client_id",
                    "column_name": "client_id"
                },{
                    "referenced_table_name": "devices",
                    "referenced_column_name": "device_id",
                    "column_name": "device_id"
                },{
                    "referenced_table_name": "employees",
                    "referenced_column_name": "employee_id",
                    "column_name": "employee_id"
                },{
                    "referenced_table_name": "statuses",
                    "referenced_column_name": "status_id",
                    "column_name": "status_id"
                }
            ],
        },
    }

    user_role_tables = {
        "Administrator":[
            "clients",
            "devices",
            "device_types",
            "employees",
            "order_spare_parts",
            "order_services",
            "statuses",
            "spare_parts",
            "services",
            "orders",
        ],
        "Operator":[
            "clients",
            "order_spare_parts",
            "order_services",
            "statuses",
            "orders",
        ],
        "Master":[
            "devices",
            "statuses",
            "spare_parts",
            "services",
            "orders",
        ],
        "Storage":[
            "order_spare_parts",
            "spare_parts",
        ],
        "Guest":[],
    }

    key = "-KlO432jG5Vm5G24X3gb-2oRX2jsVODPMjW1fu8idzw="
    config_file = "config"

    def __init__(self, page: ft.Page):
        self.page = page
        self.alert_dialogs_stack = []
        self.platform = "None"
        self.user_role = "Guest"
        self.user = "guest"
        self.is_connected = False
        self.page.on_resized = self.detect_platform
        self.page.on_route_change = self.route_change
        self.page.on_close = self.on_close
        self.page.title = "DB manager"

        self.setting = self.load_config()
        self.set_color_theme()
        self.connect_db(alert=False)
        self.detect_platform()
        self.page.go("/")


    def encrypt(self, data):
        cipher = Fernet(self.key)
        return cipher.encrypt(json.dumps(data).encode())

    def hash_password(self, password):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed_password.decode('utf-8')

    def verify_password(self, stored_password, provided_password):
        try:
            return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))
        except ValueError: 
            return False

    def decrypt(self, encrypted_data):
        cipher = Fernet(self.key)
        return json.loads(cipher.decrypt(encrypted_data).decode())


    def load_config(self):
        try:
            with open(self.config_file, "rb") as file:
                encrypted_data = file.read()
                return self.decrypt(encrypted_data)
        except (FileNotFoundError, ValueError):
            return self.setting_default

    def save_config(self):
        encrypted_data = self.encrypt(self.setting)
        with open(self.config_file, "wb") as file:
            file.write(encrypted_data)

    def alert_dialogs_stack_pop(self, e=None):
        if self.alert_dialogs_stack:
            self.alert_dialogs_stack.pop()
            if len(self.alert_dialogs_stack) > 0:
                self.page.open(self.alert_dialogs_stack[-1])
            self.page.update()

    def show_alert_dialog(self, title="Уведомление", content=ft.Column(), actions=[], modal=False):
        alert_dialog = ft.AlertDialog()
        alert_dialog.title = ft.Text(title)
        alert_dialog.content = content
        alert_dialog.actions = actions
        alert_dialog.modal = modal
        alert_dialog.on_dismiss = self.alert_dialogs_stack_pop

        self.alert_dialogs_stack.append(alert_dialog)
        self.page.open(self.alert_dialogs_stack[-1])
        self.page.update()

    def connect_db(self, alert=True):
        try:
            self.connection = mysql.connector.connect(**self.setting["db"])
            self.is_connected = True
            if alert:
                self.show_alert_dialog(content=ft.Text("Подключение успешно!"))
        except mysql.connector.Error as err:
            self.is_connected = False
            self.show_alert_dialog(content=ft.Text(f"Ошибка подключения: {err}"))
        finally:
            self.page.update()

    def set_color_theme(self):
        self.page.theme_mode = self.theme_modes[self.setting["app"]["theme_mode"]]
        self.page.theme = self.themes[self.setting["app"]["theme"]]
        self.border_color = ft.Colors.BLACK if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.WHITE
        self.page.update()

    def route_change(self, e):
        rest = ["", "setting", "loggin"]
        self.page.views.clear()
        if self.page.route[1:] in self.user_role_tables[self.user_role] + rest:
            template_view = self.routing_map.get(self.page.route)
        else:
            template_view = self.routing_map.get("/")

        if self.page.theme_mode != self.theme_modes[self.setting["app"]["theme_mode"]] or self.page.theme != self.themes[self.setting["app"]["theme"]]:
            self.set_color_theme()

        if template_view:
            view = template_view["view"]
            view.controls = [template_view["function"](self)]
            self.page.views.append(view)
            self.page.update()
        else:
            self.page.go("/")


    def detect_platform(self, e=None): 
        window_width = self.page.window.width or 0
        window_height = self.page.window.height or 0
        user_agent = self.page.client_user_agent or ""

        platform = "phone"
        if ("Windows" in user_agent or "Linux" in user_agent or "Mac" in user_agent) or self.page.platform in ("windows", "macos", "linux") or (window_width and window_width >= window_height):
            platform = "desktop"

        if self.platform != platform:
            self.platform = platform
            self.update_views()

    def update_views(self):
        if self.page.views:
          self.route_change(None)

    def get_table_rows(self, table_name, columns_str="*", join_tables=[]):
        data = []
        try:
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
            cursor.execute(query)
            data = cursor.fetchall()
        except mysql.connector.Error as err:
            self.show_alert_dialog(content=ft.Text(f"Ошибка при выполнении запроса: {err}"))
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            return data

    def get_unique_columns(self, table_name):
        data = []
        errors = []
        try:
            cursor = self.connection.cursor()
            query = """
            SELECT
            COLUMN_NAME as column_name
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = %s
              AND COLUMN_KEY IN ('UNI');
            """
            cursor.execute(query, (table_name,))
            data = list(cursor.fetchall()[0])
        except mysql.connector.Error as err:
            self.show_alert_dialog(content=ft.Text(f"Ошибка при выполнении запроса: {err}"))
            errors.append("Error")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            return errors, data

    def get_primary_columns(self, table_name):
        data = []
        errors = []
        try:
            cursor = self.connection.cursor()
            query = """
            SELECT
            COLUMN_NAME as column_name
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = %s
              AND COLUMN_KEY IN ('PRI');
            """
            cursor.execute(query, (table_name,))
            data = list(cursor.fetchall()[0])
        except mysql.connector.Error as err:
            self.show_alert_dialog(content=ft.Text(f"Ошибка при выполнении запроса: {err}"))
            errors.append("Error")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            return errors, data

    def get_referenced_row_rows(self, table_name, row):
        data = []
        errors, table_row_dependens = self.get_table_row_dependens(table_name)
        if not errors:
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
        return errors, data

    def get_table_row_dependens(self, table_name):
        data = []
        errors = []
        try:
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
            cursor.execute(query, (table_name,))
            temp = cursor.fetchall()
            for row in temp:
                temp_query = """
                SELECT
                    *
                FROM
                    %s
                """
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
            self.show_alert_dialog(content=ft.Text(f"Ошибка при выполнении запроса: {err}"))
            errors.append("Error")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            return errors, data

    def add_table_row(self, table_name, row):
        errors = []
        try:
            cursor = self.connection.cursor()
            columns = ", ".join(row.keys())
            placeholders = ", ".join(["%s"] * len(row))
            values = list(row.values())
            query = f"""
            INSERT INTO {table_name} ({columns})
            VALUES ({placeholders})
            """
            cursor.execute(query, values)
            self.connection.commit()
        except mysql.connector.Error as err:
            self.show_alert_dialog(content=ft.Text(f"Ошибка при выполнении запроса: {err}"))
            errors.append("Error")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            return errors

    def update_table_row(self, table_name, row):
        errors = []
        try:
            error, primary_columns = self.get_primary_columns(table_name)
            cursor = self.connection.cursor()
            if not error:
                set_row = ", ".join([f"{key} = %s" for key in row.keys() if key not in primary_columns])
                where_clause = " AND ".join([f"{key} = %s" for key in primary_columns])
                query = f"""
                UPDATE {table_name}
                SET {set_row}
                WHERE {where_clause}
                """
                values = [row[key] for key in row.keys() if key not in primary_columns] + [row[key] for key in primary_columns]
                cursor.execute(query, values)
                self.connection.commit()
        except mysql.connector.Error as err:
            self.show_alert_dialog(content=ft.Text(f"Ошибка при выполнении запроса: {err}"))
            errors.extend(error)
            errors.append("Error")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            return errors

    def delete_table_rows(self, table_name, row):
        errors = []
        try:
            error, primary_columns = self.get_primary_columns(table_name)
            cursor = self.connection.cursor()
            if not error:
                where_clause = " AND ".join([f"{key} = %s" for key in primary_columns])
                query = f"""
                DELETE FROM {table_name}
                WHERE {where_clause}
                """
                values = [row[key] for key in primary_columns]
                cursor.execute(query, values)
                self.connection.commit()
        except mysql.connector.Error as err:
            self.show_alert_dialog(content=ft.Text(f"Ошибка при выполнении запроса: {err}"))
            errors.extend(error)
            errors.append("Error")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            return errors

    def home_view(self):
        def on_menu_click(e):
            self.page.go(f"/{e.control.data}")

        all_items = {
            "clients": ft.PopupMenuItem(data="clients", text="Клиенты", on_click=on_menu_click),
            "devices": ft.PopupMenuItem(data="devices", text="Устройства", on_click=on_menu_click),
            "device_types": ft.PopupMenuItem(data="device_types", text="Типы устройств", on_click=on_menu_click),
            "employees": ft.PopupMenuItem(data="employees", text="Сотрудники", on_click=on_menu_click),
            "order_spare_parts": ft.PopupMenuItem(data="order_spare_parts", text="Заказы запчастей", on_click=on_menu_click),
            "order_services": ft.PopupMenuItem(data="order_services", text="Заказы услуг", on_click=on_menu_click),
            "statuses": ft.PopupMenuItem(data="statuses", text="Статусы", on_click=on_menu_click),
            "spare_parts": ft.PopupMenuItem(data="spare_parts", text="Запчасти", on_click=on_menu_click),
            "services": ft.PopupMenuItem(data="services", text="Услуги", on_click=on_menu_click),
            "orders": ft.PopupMenuItem(data="orders", text="Заказы", on_click=on_menu_click),
        }
        items = [all_items[table_name] for table_name in self.user_role_tables[self.user_role]]
        status_text = "Подключенно" if self.is_connected else "Не подключенно"

        if self.platform == "phone":
            main_window = ft.Column([
                    ft.Column([
                            ft.Container(
                                content=ft.Row([ 
                                        ft.PopupMenuButton(
                                            items=[
                                                ft.PopupMenuItem(text="Войти", on_click=lambda _: self.page.go("/loggin")),
                                                ft.PopupMenuItem(text="Настройки", on_click=lambda _: self.page.go("/setting")),
                                            ]
                                        ),
                                        ft.PopupMenuButton(
                                            content=ft.Text("Таблицы"),
                                            items=items
                                        ),
                                    ],
                                ),
                                border=ft.border.only(bottom=ft.BorderSide(1, self.border_color))
                            ),
                            ft.Text(f"Статус: {status_text}"),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Container(
                        content=ft.Image(
                            src=self.logos_modes[self.setting["app"]["theme_mode"]],
                            width=400,
                            fit=ft.ImageFit.CONTAIN,
                        ),
                        padding=20
                    ),
                    ft.Row([
                            ft.Text("2.0.1-beta"),
                            ft.Text("@danhack007")
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                horizontal_alignment = ft.CrossAxisAlignment.CENTER,
            )
        elif self.platform == "desktop":
            main_window = ft.Column([
                    ft.Column([
                            ft.Container(
                                content=ft.Row([ 
                                        ft.TextButton("Войти", on_click=lambda _: self.page.go("/loggin")),
                                        ft.TextButton("Настройки", on_click=lambda _: self.page.go("/setting")),
                                        ft.PopupMenuButton(
                                            content=ft.Text("Таблицы", color=ft.Colors.PRIMARY),
                                            items=items
                                        )
                                    ],
                                alignment=ft.MainAxisAlignment.START,
                                ),
                                border=ft.border.only(bottom=ft.BorderSide(1, self.border_color))
                            ),
                            ft.Text(f"Статус: {status_text}"),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Container(
                        content=ft.Image(
                            src=self.logos_modes[self.setting["app"]["theme_mode"]],
                            width=550,
                            fit=ft.ImageFit.CONTAIN,
                        ),
                        padding=150
                    ),
                    ft.Row(
                        [
                            ft.Text("2.0.1-beta"),
                            ft.Text("@danhack")
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                ],
                expand=True,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                horizontal_alignment = ft.CrossAxisAlignment.CENTER,
            )
        else:
            self.detect_platform()
            self.home_view()

        return main_window

    def loggin_view(self):
        def submit(e):
            pattern_loggin = r"^[a-zA-Z][a-zA-Z0-9_]{3,19}$"
            pattern_password = r"[a-zA-Z0-9@#$%^&+=!]{8,30}$"
            if bool(re.fullmatch(pattern_loggin, field_loggin.value)) and bool(re.fullmatch(pattern_password, field_password.value)):
                try:
                    cursor = self.connection.cursor()
                    query = """
                    SELECT role_name, password_hash FROM users
                        JOIN roles ON users.user_id = roles.role_id
                        WHERE login = %s;
                    """
                    value = (field_loggin.value,)
                    cursor.execute(query, value)
                    results = cursor.fetchone()
                    if results and self.verify_password(results[1], field_password.value):
                        self.user_role = results[0]
                        self.user = field_loggin.value
                        self.page.go("/")
                        self.show_alert_dialog(content=ft.Text(f"Здравствуйте, {field_loggin.value}"))
                    else:
                        self.show_alert_dialog(content=ft.Text("Неправильные пароль или логин"))
                except mysql.connector.Error as err:
                    self.show_alert_dialog(content=ft.Text(f"Ошибка при выполнении запроса: {err}"))
                finally:
                    if 'cursor' in locals() and cursor:
                        cursor.close()
            else:
                self.show_alert_dialog(content=ft.Text("Некоректно введен пароль или логин"))
            self.page.update()

        def on_change_field(e):
            if field_loggin.value and field_password.value:
                button_loggin.disabled=False
            else:
                button_loggin.disabled=True
            self.page.update()

        field_loggin = ft.TextField(label = "Логин", on_change=on_change_field)
        field_password = ft.TextField(label = "Пароль", on_change=on_change_field, password=True, can_reveal_password=True)
        button_loggin = ft.ElevatedButton(text="Войти", on_click=submit, disabled=True)
        
        if self.platform == "phone":
            main_window = ft.Column([
                ft.IconButton( icon=ft.Icons.ARROW_BACK, on_click=lambda _: self.page.go("/")),
                    ft.Row([
                            ft.Column([
                                    ft.Text("Авторизация"),
                                    field_loggin,
                                    field_password,
                                    ft.Row([                            
                                        ft.ElevatedButton(text="Войти", on_click=submit),
                                        ],
                                        alignment = ft.MainAxisAlignment.CENTER,
                                    ),
                                ],
                                expand = True,
                                alignment = ft.MainAxisAlignment.CENTER,
                                horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                            ),
                        ],
                        expand = True,
                        alignment = ft.MainAxisAlignment.CENTER,
                        vertical_alignment = ft.CrossAxisAlignment.CENTER,
                    ),
                ft.Row()
                ],
                expand = True,
                alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                horizontal_alignment = ft.CrossAxisAlignment.START,
            )
        elif self.platform == "desktop":
            main_window = ft.Column([
                    ft.Row([
                            ft.Column([
                                    ft.Text("Авторизация"),
                                    field_loggin,
                                    field_password,
                                    ft.Row([
                                        ft.ElevatedButton(text="Назад", on_click=lambda _: self.page.go("/")),
                                        ft.ElevatedButton(text="Войти", on_click=submit),
                                        ],
                                        alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                ],
                                width = 300,
                                alignment = ft.MainAxisAlignment.CENTER,
                                horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                            ),
                        ],
                        expand = True,
                        alignment = ft.MainAxisAlignment.CENTER,
                        vertical_alignment = ft.CrossAxisAlignment.CENTER,
                    ),
                ],
                expand = True,
                alignment = ft.MainAxisAlignment.CENTER,
                horizontal_alignment = ft.CrossAxisAlignment.CENTER,
            )
        else:
            self.detect_platform()
            self.home_view()

        return main_window

    def setting_view(self):
        def on_change_field(e=None):
            if host_field.value and user_field.value and db_field.value:
                button_connect.disabled=False
            else:
                button_connect.disabled=True
            self.page.update()

        def on_change_dropdown(e=None):            
            self.page.theme_mode = self.theme_modes[th_m_drop.value]
            self.page.theme = self.themes[th_c_drop.value]
            self.page.update()

        def on_click_connect(e=None):
            setting = {
                "host": host_field.value,
                "user": user_field.value,
                "password": pw_field.value,
                "database": db_field.value
            }
            try:
                self.connection = mysql.connector.connect(**setting)
                self.is_connected = True
                self.show_alert_dialog(content=ft.Text("Подключение успешно!"))
            except mysql.connector.Error as err:
                self.is_connected = False
                self.show_alert_dialog(content=ft.Text(f"Ошибка подключения: {err}"))
            finally:
                self.page.update()
        
        def on_click_save(e=None):            
            self.setting["app"]["theme_mode"] = th_m_drop.value
            self.setting["app"]["theme"] = th_c_drop.value
            self.set_color_theme()
            self.setting["db"]["host"] = host_field.value
            self.setting["user"] = user_field.value
            self.setting["password"] = pw_field.value
            self.setting["database"] = db_field.value
            self.connect_db(alert=False)
            self.save_config()
            self.page.go("/")
        
        host_field = ft.TextField(label = "Host", on_change=on_change_field)
        user_field = ft.TextField(label = "User", on_change=on_change_field)
        pw_field = ft.TextField(label = "Password", on_change=on_change_field, password=True, can_reveal_password=True)
        db_field = ft.TextField(label = "Database", on_change=on_change_field)
        
        host_field.value=self.setting["db"]["host"]
        user_field.value=self.setting["db"]["user"]
        db_field.value=self.setting["db"]["database"]
        
        th_m_drop = ft.Dropdown(
            label="Тема",
            options=[ft.dropdown.Option(key) for key in self.theme_modes.keys()],
            on_change=on_change_dropdown,
            value=self.setting["app"]["theme_mode"],
        )
        th_c_drop = ft.Dropdown(
            label="Цвет",
            options=[ft.dropdown.Option(key) for key in self.themes.keys()],
            on_change=on_change_dropdown,
            value=self.setting["app"]["theme"],
        )
        
        button_connect = ft.ElevatedButton(text="Подключиться", on_click=on_click_connect)        
        button_save = ft.ElevatedButton(text="Сохранить", on_click=on_click_save)
        on_change_field()
        if self.platform == "phone":
            main_window = ft.Column([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: self.page.go("/")),
                    ft.Row([
                            ft.Column([
                                    ft.Container(
                                        content=ft.Column([
                                                ft.Text("Подключение к БД"),
                                                host_field,
                                                user_field,
                                                pw_field,
                                                db_field,
                                                button_connect,
                                            ],
                                            horizontal_alignment = ft.CrossAxisAlignment.START,
                                        )
                                    ),
                                    ft.Container(
                                        content=ft.Column([
                                                ft.Text("Кастомизация"),
                                                th_m_drop,
                                                th_c_drop,
                                            ],
                                            horizontal_alignment = ft.CrossAxisAlignment.START,
                                        )
                                    ),
                                    button_save,
                                ],
                                alignment = ft.MainAxisAlignment.CENTER,
                                horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                            ),
                        ],
                        expand = True,
                        alignment = ft.MainAxisAlignment.CENTER,
                        vertical_alignment = ft.CrossAxisAlignment.CENTER,
                    ),
                    ft.Row(),
                ],
                expand = True,
                alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                horizontal_alignment = ft.CrossAxisAlignment.START,
            )
        elif self.platform == "desktop":
            main_window = ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Подключение к БД"),
                                host_field,
                                user_field,
                                pw_field,
                                db_field,
                                button_connect,
                                ],
                                horizontal_alignment = ft.CrossAxisAlignment.START,
                            )
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Кастомизация"),
                                th_m_drop,
                                th_c_drop,
                                ],
                                horizontal_alignment = ft.CrossAxisAlignment.START,
                            )
                        ),
                        ft.Row([
                            ft.ElevatedButton(text="Назад" , on_click=lambda _: self.page.go("/")),
                            button_save,
                            ],
                            alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                        )
                        ],
                        width = 300,
                        alignment = ft.MainAxisAlignment.CENTER,
                        horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                    ),
                    ],
                    expand = True,
                    alignment = ft.MainAxisAlignment.CENTER,
                    vertical_alignment = ft.CrossAxisAlignment.CENTER,
                ),
                ],
                expand = True,
                alignment = ft.MainAxisAlignment.CENTER,
                horizontal_alignment = ft.CrossAxisAlignment.CENTER,
            )
        else:
            self.detect_platform()
            self.home_view()

        return main_window

    def table_view(self, table_name):
        def create_table(table_name, table_rows):
            table_container_in = ft.Row()
            if table_rows:
                def sync_scroll(e: ft.OnScrollEvent):
                    main_table_container_in.scroll_to(offset=e.pixels, delta=e.scroll_delta, duration=0)

                main_columns = [
                    ft.DataColumn(ft.Text(self.column_names[key])) for key in table_rows[0].keys()
                ]
                last_column = [
                    ft.DataColumn(ft.Text("Действия"))
                ]
                main_rows=[]
                last_rows=[]
                for row in table_rows:
                    main_rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(cell)) for cell in row.values()
                            ],
                        )
                    )
                    last_rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(
                                    ft.Row([
                                            ft.IconButton(icon=ft.Icons.DELETE, on_click=lambda e, t=table_name, r=row: delete_row(e, t, r)),
                                            ft.IconButton(icon=ft.Icons.EDIT, on_click=lambda e, t=table_name, r=row: change_row(e, t, r)),
                                        ],
                                    )
                                )
                            ]
                        )
                    )
                main_rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.IconButton(icon=ft.Icons.ADD, on_click=add_note))
                        ]+[
                            ft.DataCell(ft.Text()) for _ in range(len(table_rows[0])-1)
                        ]
                    )
                )
                last_rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text())
                        ]
                    )
                )
                main_table = ft.DataTable(
                    columns=main_columns,
                    rows=main_rows,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                )
                main_table_container_in = ft.Column(
                    controls=[main_table],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    scroll=ft.ScrollMode.AUTO,
                )
                main_table_container_out = ft.Row(
                    controls=[main_table_container_in],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                )
                last_table = ft.DataTable(
                    columns=last_column,
                    rows=last_rows,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                )
                last_table_container = ft.Column(
                    controls=[last_table],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    scroll=ft.ScrollMode.AUTO,
                )
                last_table_container.on_scroll = sync_scroll
                table_container_in = ft.Row(
                    controls=[
                        main_table_container_out,
                        last_table_container,
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    expand=True,
                    spacing=0,
                )
            return table_container_in
        def search_data(e=None):
            table_container_in = table_container_out.controls[0]
            main_table_container_out = table_container_in.controls[0]
            main_table_container_in = main_table_container_out.controls[0]
            main_table = main_table_container_in.controls[0]
            main_rows = main_table.rows[:-1]
            last_table_container = table_container_in.controls[1]
            last_table = last_table_container.controls[0]
            last_rows = last_table.rows[:-1]

            query = e.control.value.lower()
            for main_row, last_row in zip(main_rows, last_rows):
                main_row.visible = True
                last_row.visible = True
                if query:
                    for cell in main_row.cells:
                        match = False
                        value = str(cell.content.value).lower()
                        if (Levenshtein.ratio(query, value) >= 0.7) or (query in value):
                            match = True
                            break
                    if not match:
                        main_row.visible = False
                        last_row.visible = False
            self.page.update()

        def add_note(e=None):
            def create_row(content):
                controls = content.controls
                adding_row = {control.data:control.value for control in controls}
                return adding_row
            def check_row_values(content):
                controls = content.controls
                nessesary_columns_list = list(self.tables[table_name]["nessesary_columns"])
                have_wrong = False
                for control in controls:
                    if control.data in nessesary_columns_list:
                        if control.value:
                            nessesary_columns_list.remove(control.data)
                    if control.error_text:
                        return False
                return not bool(nessesary_columns_list)
            def check_value(e=None):
                value = e.control.value
                column_name = e.control.data
                pattern = self.regex_patterns[self.column_mapping[column_name]]
                if value:
                    if re.match(pattern, value, re.IGNORECASE):
                        e.control.error_text = None
                    else:
                        e.control.error_text = "Поле заполнено не правильно"
                else:
                    e.control.error_text = "Данное поле нужно заполнить"
                self.page.update()
            def set_nesserary_empty():
                controls = content.controls
                nessesary_columns_list = list(self.tables[table_name]["nessesary_columns"])
                for control in controls:
                    if control.data in nessesary_columns_list:
                        if not control.value:
                            control.error_text = "Данное поле нужно заполнить"
                self.page.update()
            def action_button_click(e=None):
                dialog = e.control.parent
                text = e.control.text
                if text == "Отмена":
                    self.page.close(dialog)
                else:
                    is_checked = check_row_values(content)
                    if is_checked:
                        adding_row = create_row(content)
                        error = self.add_table_row(table_name, adding_row)
                        self.page.close(dialog)
                        if not error:
                            self.show_alert_dialog(content=ft.Text("Успех!"))
                    else:
                        set_nesserary_empty()
                self.page.update()

            content = ft.Column(
                scroll=ft.ScrollMode.AUTO,
                expand = True,
            )
            actions = [
                ft.TextButton("Отмена", on_click=action_button_click),
                ft.TextButton("Применить", on_click=action_button_click),
            ]
            
            table_column_names = [column_name for column_name in self.get_table_rows(table_name)[0].keys() if not column_name in self.tables[table_name]["passed_columns"]]
            errors, table_row_dependens = self.get_table_row_dependens(table_name)
            if not errors:
                for table_column_name in table_column_names:
                    control = None
                    for table_row_dependen in table_row_dependens:
                        if table_column_name in table_row_dependen["column_name"]:
                            options = []
                            for referenced_table_row in table_row_dependen["referenced_table_rows"]:
                                options.append(ft.dropdown.Option(
                                        key=str(referenced_table_row[table_row_dependen["referenced_column_name"]]),
                                        text=" ".join([str(referenced_table_row[column_name]) for column_name in self.tables[table_row_dependen['referenced_table_name']]["label_on_choose"]])
                                    )
                                )
                            control = ft.Dropdown(
                                data=table_column_name,
                                label=self.column_names[table_column_name],
                                options=options,
                                on_change=check_value,
                            )
                    if not control:
                        control=ft.TextField(
                            data=table_column_name,
                            label=self.column_names[table_column_name],
                            on_change=check_value,
                        )
                    if control:
                        if control.data in self.tables[table_name]["nessesary_columns"]:
                            control.label = control.label+'*'
                        content.controls.append(control)

                self.show_alert_dialog(title="Добавить", content=content, actions=actions, modal=True)
            update()
        def delete_row(e=None,table_name=None, row=None):
            errors, referenced_row_rows = self.get_referenced_row_rows(table_name, row)
            if referenced_row_rows:
                if self.user_role == "Administrator":
                    def action_button_click(e=None):
                        dialog = e.control.parent
                        self.page.close(dialog)
                    content = ft.Column(
                        scroll=ft.ScrollMode.AUTO,
                        expand = True,
                    )
                    actions = [
                        ft.TextButton("Отмена", on_click=action_button_click),
                    ]
                    for referenced_row_row in referenced_row_rows:
                        referenced_table_name = referenced_row_row["referenced_table_name"]
                        referenced_table_rows = referenced_row_row["referenced_table_rows"]
                        content.controls.append(create_table(referenced_table_name, referenced_table_rows))
                    self.show_alert_dialog(title="Удаление", content=content, actions=actions, modal=True)
                else:
                    def action_button_click(e=None):
                        dialog = e.control.parent
                        self.page.close(dialog)
                    actions = [
                        ft.TextButton("Отмена", on_click=action_button_click),
                    ]
                    self.show_alert_dialog(title="Удаление", content=ft.Text("Есть зависимые записи. Удаление не возможно!"), actions=actions, modal=True)
            else:
                errors = self.delete_table_rows(table_name, row)
                if not errors:
                    self.show_alert_dialog(content=ft.Text("Успех!"))
            update()
        def change_row(e=None,table_name=None, row=None):
            def create_row(content):
                controls = content.controls
                updating_row = row.copy()
                for control in controls:
                    updating_row[control.data] = control.value
                return updating_row
            def check_row_values(content):
                controls = content.controls
                nessesary_columns_list = list(self.tables[table_name]["nessesary_columns"])
                have_wrong = False
                for control in controls:
                    if control.data in nessesary_columns_list:
                        if control.value:
                            nessesary_columns_list.remove(control.data)
                    if control.error_text:
                        return False
                return not bool(nessesary_columns_list)
            def check_value(e=None):
                value = e.control.value
                column_name = e.control.data
                pattern = self.regex_patterns[self.column_mapping[column_name]]
                if value:
                    if re.match(pattern, value, re.IGNORECASE):
                        e.control.error_text = None
                    else:
                        e.control.error_text = "Поле заполнено не правильно"
                else:
                    e.control.error_text = "Данное поле нужно заполнить"
                self.page.update()
            def set_empty_error_text():
                controls = content.controls[1].controls
                nessesary_columns_list = list(self.tables[table_name]["nessesary_columns"])
                for control in controls:
                    if control.data in nessesary_columns_list:
                        if not control.value:
                            control.error_text = "Данное поле нужно заполнить"
                self.page.update()
            def action_button_click(e=None):
                dialog = e.control.parent
                text = e.control.text
                if text == "Отмена":
                    self.page.close(dialog)
                else:
                    is_checked = check_row_values(content)
                    if is_checked:
                        updating_row = create_row(content)
                        error = self.update_table_row(table_name, updating_row)
                        self.page.close(dialog)
                        if not error:
                            self.show_alert_dialog(content=ft.Text("Успех!"))
                    else:
                        set_empty_error_text()
                self.page.update()

            content = ft.Column(
                scroll=ft.ScrollMode.AUTO,
                expand = True,
            )
            actions = [
                ft.TextButton("Отмена", on_click=action_button_click),
                ft.TextButton("Применить", on_click=action_button_click),
            ]
            
            table_column_names = [column_name for column_name in self.get_table_rows(table_name)[0].keys() if not column_name in self.tables[table_name]["passed_columns"]]
            errors1, primary_columns = self.get_primary_columns(table_name)
            errors2, unique_columns = self.get_unique_columns(table_name)
            errors = errors1 + errors2
            all_unique_columns = primary_columns + unique_columns 
            errors, table_row_dependens = self.get_table_row_dependens(table_name)
            if not errors:
                for table_column_name in table_column_names:
                    control = None
                    is_disabled = table_column_name in all_unique_columns
                    for table_row_dependen in table_row_dependens:
                        if table_column_name in table_row_dependen["column_name"]:
                            options = []
                            for referenced_table_row in table_row_dependen["referenced_table_rows"]:
                                options.append(ft.dropdown.Option(
                                        key=str(referenced_table_row[table_row_dependen["referenced_column_name"]]),
                                        text=" ".join([str(referenced_table_row[column_name]) for column_name in self.tables[table_row_dependen['referenced_table_name']]["label_on_choose"]])
                                    )
                                )
                            control = ft.Dropdown(
                                data=table_column_name,
                                label=self.column_names[table_column_name],
                                options=options,
                                on_change=check_value,
                                value=row[table_column_name],
                                disabled = is_disabled,
                            )
                    if not control:
                        control=ft.TextField(
                            data=table_column_name,
                            label=self.column_names[table_column_name],
                            on_change=check_value,
                            value=row[table_column_name],
                            disabled = is_disabled,
                        )
                    if control:
                        if control.data in self.tables[table_name]["nessesary_columns"]:
                            control.label = control.label+'*'
                        content.controls.append(control)

                self.show_alert_dialog(title="Обновить", content=content, actions=actions, modal=True)
            update()
        def update(e=None):
            table_rows = self.get_table_rows(
                table_name, self.tables[table_name]["view_columns"],
                self.tables[table_name]["join_tables"]
            )
            table_container_out.controls=[create_table(table_name, table_rows)]
            self.page.update()
            
        table_rows = self.get_table_rows(
            table_name, self.tables[table_name]["view_columns"],
            self.tables[table_name]["join_tables"]
        )
        table_container_out=ft.Column(
            controls=[create_table(table_name, table_rows)],
            alignment = ft.MainAxisAlignment.START,
            expand=True,
            horizontal_alignment = ft.CrossAxisAlignment.START,
        )
        search_field = ft.TextField(label = "Поиск", on_change = search_data)
        if self.platform == "phone":
            search_field.expand = True
            main_window = ft.Column([
                ft.Container(
                    content = ft.Row([
                            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: self.page.go("/")),
                            ft.Text(self.tables[table_name]["name"])
                        ],
                        alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    border=ft.border.only(bottom=ft.BorderSide(1, self.border_color)),
                ),
                table_container_out,
                ft.Row([
                        search_field,
                        ft.IconButton(icon=ft.Icons.REFRESH, on_click=update)
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                )
                ],
                expand = True,
                alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                horizontal_alignment = ft.CrossAxisAlignment.START,
            )
        elif self.platform == "desktop":
            main_window = ft.Column([
                ft.Column([
                        ft.Container(
                            content = ft.Row([
                                    ft.TextButton(text="Назад", on_click=lambda _: self.page.go("/")),
                                    ft.Text(self.tables[table_name]["name"])
                                ],
                                alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            border=ft.border.only(bottom=ft.BorderSide(1, self.border_color)),
                        ),
                        ft.Row([
                                search_field,
                                ft.IconButton(icon=ft.Icons.REFRESH, on_click=update),
                            ],
                        ),
                    ],
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                table_container_out,
                ft.Row(),
                ],
                expand = True,
                alignment = ft.MainAxisAlignment.START,
                horizontal_alignment = ft.CrossAxisAlignment.START,
            )
        else:
            self.detect_platform()
            self.home_view()

        return main_window

    def clients_view(self):
        return self.table_view("clients")

    def devices_view(self):
        return self.table_view("devices")

    def device_types_view(self):
        return self.table_view("device_types")

    def employees_view(self):
        return self.table_view("employees")

    def order_spare_parts_view(self):
       return self.table_view("order_spare_parts")

    def order_services_view(self):
        return self.table_view("order_services")

    def statuses_view(self):
        return self.table_view("statuses")

    def spare_parts_view(self):
        return self.table_view("spare_parts")

    def services_view(self):
        return self.table_view("services")

    def orders_view(self):
        return self.table_view("orders")


    def on_close(self,e):
        self.save_config()
        self.page.window_close()

    routing_map = {
        "/": {
            "function": home_view,
            "view": ft.View(
                route="/",
            ),
        },
        "/loggin": {
            "function": loggin_view,
            "view": ft.View(
                route="/setting",
            ),
        },
        "/setting": {
            "function": setting_view,
            "view": ft.View(
                route="/setting",
            ),
        },
        "/clients": {
            "function": clients_view,
            "view": ft.View(
                route="/clients",
            ),
        },
        "/devices": {
            "function": devices_view,
            "view": ft.View(
                route="/devices",
            ),
        },
        "/device_types": {
            "function": device_types_view,
            "view": ft.View(
                route="/device_types",
            ),
        },
        "/employees": {
            "function": employees_view,
            "view": ft.View(
                route="/employees",
            ),
        },
        "/order_spare_parts": {
            "function": order_spare_parts_view,
            "view": ft.View(
                route="/order_spare_parts",
            ),
        },
        "/order_services": {
            "function": order_services_view,
            "view": ft.View(
                route="/order_services",
            ),
        },
        "/statuses": {
            "function": statuses_view,
            "view": ft.View(
                route="/statuses",
            ),
        },
        "/spare_parts": {
            "function": spare_parts_view,
            "view": ft.View(
                route="/spare_parts",
            ),
        },
        "/services": {
            "function": services_view,
            "view": ft.View(
                route="/services",
            ),
        },
        "/orders": {
            "function": orders_view,
            "view": ft.View(
                route="/orders",
            ),
        }
    }

ft.app(target=RepairShopApp)
