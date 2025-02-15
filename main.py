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
            color_scheme_seed="indigo",
            use_material3=True,
        ),
        "Фиолетовая ночь": ft.Theme(
            color_scheme_seed="deepPurple",
            use_material3=True,
        ),
        "Лесная зелень": ft.Theme(
            color_scheme_seed="green",
            use_material3=True,
        ),
        "Песчаный берег": ft.Theme(
            color_scheme_seed="amber",
            use_material3=True,
        ),
        "Лазурный бриз": ft.Theme(
            color_scheme_seed="lightBlue",
            use_material3=True,
        ),
        "Тестовый": ft.Theme(
            color_scheme_seed=ft.colors.ORANGE,
            use_material3=True
        ),
    }

    logos_modes = {
        "Светлая стандартная": r"source\img\logo\light_default.png",  # Убедись, что пути правильные
        "Темная стандартная": r"source\img\logo\dark_default.png"
    }

    setting_default = {
        "app": {
            "user_role": "Guest",
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

    key = "-KlO432jG5Vm5G24X3gb-2oRX2jsVODPMjW1fu8idzw="
    config_file = "config"

    def __init__(self, page: ft.Page):
        self.page = page
        self.alert_dialog = ft.AlertDialog()
        self.platform = "None"
        self.status_text = ft.Text("Не подключенно")
        self.is_connected = False  # Добавляем переменную для статуса подключения
        self.page.on_resize = self.detect_platform  # Вызываем detect_platform при изменении размера
        self.page.on_route_change = self.route_change # назначаем обработчик смены роута
        self.page.on_close = self.on_close
        self.page.title = "DB manager"

        self.setting = self.load_config()
        self.set_color_theme()
        self.connect_db(alert=False)
        self.detect_platform() # определяем платформу
        self.page.go("/") # переходим на главную


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

    def show_alert(self, message):
        self.alert_dialog.title = ft.Text("Уведомление")
        self.alert_dialog.content = ft.Text(message)
        self.alert_dialog.open = True
        self.page.dialog = self.alert_dialog
        self.page.update()

    def connect_db(self, alert=True):
        try:
            self.connection = mysql.connector.connect(**self.setting["db"])
            self.status_text = "Подключенно"
            self.is_connected = True
            if alert:
                self.show_alert("Подключение успешно!")
        except mysql.connector.Error as err:
            self.status_text = "Не подключенно"
            self.is_connected = False
            self.show_alert(f"Ошибка подключения: {err}")
        finally:
            self.page.update()

    def set_color_theme(self):
        self.page.theme_mode = self.theme_modes[self.setting["app"]["theme_mode"]]
        self.page.theme = self.themes[self.setting["app"]["theme"]]
        self.border_color = ft.colors.BLACK if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.colors.WHITE
        self.page.update()

    def route_change(self, e):
        self.page.views.clear()
        template_view = self.routing_map.get(self.page.route)  # Получаем View из словаря

        if self.page.theme_mode != self.theme_modes[self.setting["app"]["theme_mode"]] or self.page.theme != self.themes[self.setting["app"]["theme"]]:
            self.set_color_theme()

        if template_view:
            view = template_view["view"]
            view.controls = [template_view["function"](self)] # Вызываем функцию и добавляем результат в controls
            self.page.views.append(view)
        else:
            self.page.go("/")

        self.page.update()


    def detect_platform(self, e=None): 
        if self.page.platform in ["android", "ios"] or (self.page.window_width and self.page.window_height and self.page.window_width < self.page.window_height):
            if self.platform != "phone":
                self.platform = "phone"
        elif self.page.platform in ["windows", "macos", "linux"] or (self.page.window_width and self.page.window_height and self.page.window_width >= self.page.window_height):
            if self.platform != "desktop":
                self.platform = "desktop"
        else:
            if self.platform != "desktop":
                self.platform = "desktop"

        self.update_views()

    def update_views(self):
        if self.page.views:
          self.route_change(None)

    def get_table_rows(self, table, columns="*", join_tables=[]):
        data = []
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                SELECT 
                    {}
                FROM 
                    {}
            """.format(columns, table)
            if join_tables:
                for join_table in join_tables:
                    query += """ JOIN {refer_table} 
                        ON {refer_table}.{refer_column} = {table}.{column}
                    """.format(**join_table)
            cursor.execute(query)
            data = cursor.fetchall()
        except mysql.connector.Error as err:
            self.show_alert(f"Ошибка при выполнении запроса: {err}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            return data

    def get_table_row_dependens(self, table):
        data = []
        try:
            cursor = self.connection.cursor(dictionary=True)
            main_query = """
            SELECT     
                REFERENCED_TABLE_NAME AS referenced_table,
                REFERENCED_COLUMN_NAME AS referenced_column,
                TABLE_NAME AS table_name,
                COLUMN_NAME AS column_name
            FROM 
                INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE 
                TABLE_NAME = {} 
                AND REFERENCED_TABLE_NAME IS NOT NULL;
            """.format(table)
            cursor.execute(main_query)
            temp = cursor.fetchall()
            for row in temp:
                temp_query = """"""

        except mysql.connector.Error as err:
            self.show_alert(f"Ошибка при выполнении запроса: {err}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            return data

    def update_table_row(self, table, columns="*", join_tables=[]):
        pass

    def delete_table_rows(self, table, columns="*", join_tables=[]):
        pass

    def home_view(self):
        def on_menu_click(e):
            self.page.go(f"/{e.control.data}")

        all_items = {
            "clients": ft.PopupMenuItem(data="clients", text="Клиенты", on_click=on_menu_click),
            "devices": ft.PopupMenuItem(data="devices", text="Устройства", on_click=on_menu_click),
            "devicetypes": ft.PopupMenuItem(data="devicetypes", text="Типы устройств", on_click=on_menu_click),
            "employees": ft.PopupMenuItem(data="employees", text="Сотрудники", on_click=on_menu_click),
            "orderspareparts": ft.PopupMenuItem(data="orderspareparts", text="Заказы запчастей", on_click=on_menu_click),
            "orderservices": ft.PopupMenuItem(data="orderservices", text="Заказы услуг", on_click=on_menu_click),
            "statuses": ft.PopupMenuItem(data="statuses", text="Статусы", on_click=on_menu_click),
            "spareparts": ft.PopupMenuItem(data="spareparts", text="Запчасти", on_click=on_menu_click),
            "services": ft.PopupMenuItem(data="services", text="Услуги", on_click=on_menu_click),
            "orders": ft.PopupMenuItem(data="orders", text="Заказы", on_click=on_menu_click),
        }

        for item in all_items.values():
            item.enabled = self.is_connected


        if self.setting["app"]["user_role"] == "Administrator":
            items = list(all_items.values())
        elif self.setting["app"]["user_role"] == "Operator":
            items = [
                all_items["clients"],
                all_items["orderspareparts"],
                all_items["orderservices"],
                all_items["statuses"],
                all_items["orders"],
            ]
        elif self.setting["app"]["user_role"] == "Master":
            items = [
                all_items["devices"],
                all_items["statuses"],
                all_items["spareparts"],
                all_items["services"],
                all_items["orders"],
            ]
        elif self.setting["app"]["user_role"] == "Storage":
            items = [
                all_items["orderspareparts"],
                all_items["spareparts"],
            ]
        else:
            items = []



        if self.platform == "phone":
            main_window = ft.Column(
                [
                    ft.Column([
                        ft.Container(
                            content=ft.Row([ # вынес кнопки в отдельный Row
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
                        ft.Text(f"Статус: {self.status_text}"),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Image(
                        src=self.logos_modes[self.setting["app"]["theme_mode"]], # используем theme_mode, а не theme
                        width=200,
                        height=200,
                        fit=ft.ImageFit.CONTAIN,
                    ),
                    ft.Row(
                        [
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
            main_window = ft.Column(
                [
                    ft.Column([
                        ft.Container(
                            content=ft.Row([ # вынес кнопки в отдельный Row
                                ft.TextButton("Войти", on_click=lambda _: self.page.go("/loggin")),
                                ft.TextButton("Настройки", on_click=lambda _: self.page.go("/setting")),
                                ft.PopupMenuButton(
                                    content=ft.Text("Таблицы", color=ft.colors.PRIMARY),
                                    items=items
                                )
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            ),
                            border=ft.border.only(bottom=ft.BorderSide(1, self.border_color))
                        ),
                        ft.Text(f"Статус: {self.status_text}"),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Image(
                        src=self.logos_modes[self.setting["app"]["theme_mode"]], 
                        width=400,
                        height=400,
                        fit=ft.ImageFit.CONTAIN,
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
                        JOIN roles ON users.id = roles.id
                        WHERE login = %s;
                    """
                    value = (field_loggin.value,)
                    cursor.execute(query, value)
                    results = cursor.fetchone()
                    if self.verify_password(results[1], field_password.value):
                        self.setting["app"]["user_role"] = results[0]
                        self.page.go("/")
                        self.show_alert(f"Здравствуйте, {field_loggin.value}")
                    else:
                        self.show_alert("Неправильные пароль или логин")
                except mysql.connector.Error as err:
                    self.show_alert(f"Ошибка при выполнении запроса: {err}")
                finally:
                    if 'cursor' in locals() and cursor:
                        cursor.close()
            else:
                self.show_alert("Некоректно введен пароль или логин")
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
                ft.IconButton( icon=ft.icons.ARROW_BACK, on_click=lambda _: self.page.go("/")),
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
            self.loggin_view()

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
                self.status_text = "Подключенно"
                self.is_connected = True
                self.show_alert("Подключение успешно!")
            except mysql.connector.Error as err:
                self.status_text = "Не подключенно"
                self.is_connected = False
                self.show_alert(f"Ошибка подключения: {err}")
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
        pw_field.value=self.setting["db"]["password"]
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
                ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.page.go("/")),
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
            self.setting_view()

        return main_window

    def clients_view(self):
        table_container = ft.Column()
        def create_table(e=None):
            data = self.get_table_rows("clients")
            if data:
                def sync_scroll(e: ft.OnScrollEvent):
                    main_table_container_in.scroll_to(e.pixels, duration=0)

                main_columns = [
                    ft.DataColumn(ft.Text(key)) for key in data[0].keys()
                ]
                last_column = [
                    ft.DataColumn(ft.Text("Действия"))
                ]
                main_rows=[]
                last_rows=[]
                for row in data:
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
                                            ft.IconButton(icon=ft.icons.DELETE, on_click=lambda e, r=row: delete_row(e, r)),
                                            ft.IconButton(icon=ft.icons.EDIT, on_click=lambda e, r=row: change_row(e, r)),
                                        ],
                                    )
                                )
                            ]
                        )
                    )
                main_rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.IconButton(icon=ft.icons.ADD, on_click=add_note))
                        ]+[
                            ft.DataCell(ft.Text()) for _ in range(len(data[0])-1)
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
                    expand=True,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                )
                main_table_container_in = ft.Column(
                    controls=[main_table],
                    expand=True,
                    alignment=ft.MainAxisAlignment.START,
                    scroll=ft.ScrollMode.AUTO,
                )
                main_table_container_out = ft.Row(
                    controls=[main_table_container_in],
                    expand=True,
                    alignment=ft.MainAxisAlignment.START,
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
                    scroll=ft.ScrollMode.AUTO,
                )
                last_table_container.on_scroll = sync_scroll
                table_container = ft.Row(
                    controls=[main_table_container_out, last_table_container],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    expand=True,
                    spacing=0,
                )
            return table_container
        def search_data(e=None):
            table_container_local = table_container.controls[0]
            main_table_container_out = table_container_local.controls[0]
            main_table_container_in = main_table_container_out.controls[0]
            main_table = main_table_container_in.controls[0]
            main_rows = main_table.rows[:-1]
            last_table_container = table_container_local.controls[1]
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
            pass
        def delete_row(e=None, row=None):
            pass
        def change_row(e=None, row=None):
            pass
        def update(e=None):
            table_container.controls=[create_table()]
            self.page.update()

        table_container=ft.Column(
            controls=[create_table()],
            expand=True,
            alignment = ft.MainAxisAlignment.START,
            horizontal_alignment = ft.CrossAxisAlignment.START,
        )
        search_field = ft.TextField(label = "Поиск", on_change = search_data)
        if self.platform == "phone":
            search_field.expand = True
            main_window = ft.Column([
                ft.Container(
                    content = ft.Row([
                            ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.page.go("/")),
                            ft.Text("Клиенты")
                        ],
                        alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    border=ft.border.only(bottom=ft.BorderSide(1, self.border_color)),
                ),
                table_container,
                ft.Row([
                        search_field,
                        ft.IconButton(icon=ft.icons.REFRESH, on_click=update)
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
                                    ft.Text("Клиенты")
                                ],
                                alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            border=ft.border.only(bottom=ft.BorderSide(1, self.border_color)),
                        ),
                        ft.Row([
                                search_field,
                                ft.IconButton(icon=ft.icons.REFRESH, on_click=update),
                            ],
                        ),
                    ],
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                table_container,
                ft.Row(),
                ],
                expand = True,
                alignment = ft.MainAxisAlignment.START,
                horizontal_alignment = ft.CrossAxisAlignment.START,
            )
        else:
            self.detect_platform()
            self.clients_view()

        return main_window

    def devices_view(self):
        def create_table(e=None):
            return [ft.Row()]
        def search_data(e=None):
            pass
        def add_note(e=None):
            pass
        def delete_note(e=None):
            pass
        def update_note(e=None):
            pass
        def update(e=None):
            pass

        search_field = ft.TextField(label = "Поиск", on_change = search_data)
        if self.platform == "phone":
            search_field.expand = True
            main_window = ft.Column([
                ft.Container(
                    content = ft.Row([
                            ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.page.go("/")),
                            ft.Text("Устройства")
                        ],
                        alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    border=ft.border.only(bottom=ft.BorderSide(1, self.border_color)),
                ),
                ft.Column(
                    create_table() + [ft.IconButton(icon=ft.icons.ADD, on_click=add_note),ft.Row()],
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Row([
                        search_field,
                        ft.IconButton(icon=ft.icons.REFRESH, on_click=update)
                    ],
                    expand = True,
                    alignment = ft.MainAxisAlignment.START,
                    vertical_alignment = ft.CrossAxisAlignment.END,
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
                                    ft.Text("Устройства")
                                ],
                                alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            border=ft.border.only(bottom=ft.BorderSide(1, self.border_color)),
                        ),
                        ft.Row([
                                search_field,
                                ft.TextButton(text="Добавить", on_click=add_note),
                                ft.IconButton(icon=ft.icons.REFRESH, on_click=update),
                            ],
                        ),
                    ],
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Column(
                    create_table(),
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Row(),
                ],
                expand = True,
                alignment = ft.MainAxisAlignment.START,
                horizontal_alignment = ft.CrossAxisAlignment.START,
            )
        else:
            self.detect_platform()
            self.devices_view()

        return main_window

    def devicetypes_view(self):
        def create_table(e=None):
            return [ft.Row()]
        def search_data(e=None):
            pass
        def add_note(e=None):
            pass
        def delete_note(e=None):
            pass
        def update_note(e=None):
            pass
        def update(e=None):
            pass

        search_field = ft.TextField(label = "Поиск", on_change = search_data)
        if self.platform == "phone":
            search_field.expand = True
            main_window = ft.Column([
                ft.Container(
                    content = ft.Row([
                            ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.page.go("/")),
                            ft.Text("Типы устройств")
                        ],
                        alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    border=ft.border.only(bottom=ft.BorderSide(1, self.border_color)),
                ),
                ft.Column(
                    create_table() + [ft.IconButton(icon=ft.icons.ADD, on_click=add_note),ft.Row()],
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Row([
                        search_field,
                        ft.IconButton(icon=ft.icons.REFRESH, on_click=update)
                    ],
                    expand = True,
                    alignment = ft.MainAxisAlignment.START,
                    vertical_alignment = ft.CrossAxisAlignment.END,
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
                                    ft.Text("Типы устройств")
                                ],
                                alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            border=ft.border.only(bottom=ft.BorderSide(1, self.border_color)),
                        ),
                        ft.Row([
                                search_field,
                                ft.TextButton(text="Добавить", on_click=add_note),
                                ft.IconButton(icon=ft.icons.REFRESH, on_click=update),
                            ],
                        ),
                    ],
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Column(
                    create_table(),
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Row(),
                ],
                expand = True,
                alignment = ft.MainAxisAlignment.START,
                horizontal_alignment = ft.CrossAxisAlignment.START,
            )
        else:
            self.detect_platform()
            self.devicetypes_view()

        return main_window

    def employees_view(self):
        def create_table(e=None):
            return [ft.Row()]
        def search_data(e=None):
            pass
        def add_note(e=None):
            pass
        def delete_note(e=None):
            pass
        def update_note(e=None):
            pass
        def update(e=None):
            pass

        search_field = ft.TextField(label = "Поиск", on_change = search_data)
        if self.platform == "phone":
            search_field.expand = True
            main_window = ft.Column([
                ft.Container(
                    content = ft.Row([
                            ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.page.go("/")),
                            ft.Text("Сотрудники")
                        ],
                        alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    border=ft.border.only(bottom=ft.BorderSide(1, self.border_color)),
                ),
                ft.Column(
                    create_table() + [ft.IconButton(icon=ft.icons.ADD, on_click=add_note),ft.Row()],
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Row([
                        search_field,
                        ft.IconButton(icon=ft.icons.REFRESH, on_click=update)
                    ],
                    expand = True,
                    alignment = ft.MainAxisAlignment.START,
                    vertical_alignment = ft.CrossAxisAlignment.END,
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
                                    ft.Text("Сотрудники")
                                ],
                                alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            border=ft.border.only(bottom=ft.BorderSide(1, self.border_color)),
                        ),
                        ft.Row([
                                search_field,
                                ft.TextButton(text="Добавить", on_click=add_note),
                                ft.IconButton(icon=ft.icons.REFRESH, on_click=update),
                            ],
                        ),
                    ],
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Column(
                    create_table(),
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Row(),
                ],
                expand = True,
                alignment = ft.MainAxisAlignment.START,
                horizontal_alignment = ft.CrossAxisAlignment.START,
            )
        else:
            self.detect_platform()
            self.employees_view()

        return main_window

    def orderspareparts_view(self):
        def create_table(e=None):
            return [ft.Row()]
        def search_data(e=None):
            pass
        def add_note(e=None):
            pass
        def delete_note(e=None):
            pass
        def update_note(e=None):
            pass
        def update(e=None):
            pass

        search_field = ft.TextField(label = "Поиск", on_change = search_data)
        if self.platform == "phone":
            search_field.expand = True
            main_window = ft.Column([
                ft.Container(
                    content = ft.Row([
                            ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.page.go("/")),
                            ft.Text("Заказы запчастей")
                        ],
                        alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    border=ft.border.only(bottom=ft.BorderSide(1, self.border_color)),
                ),
                ft.Column(
                    create_table() + [ft.IconButton(icon=ft.icons.ADD, on_click=add_note),ft.Row()],
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Row([
                        search_field,
                        ft.IconButton(icon=ft.icons.REFRESH, on_click=update)
                    ],
                    expand = True,
                    alignment = ft.MainAxisAlignment.START,
                    vertical_alignment = ft.CrossAxisAlignment.END,
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
                                    ft.Text("Заказы запчастей")
                                ],
                                alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            border=ft.border.only(bottom=ft.BorderSide(1, self.border_color)),
                        ),
                        ft.Row([
                                search_field,
                                ft.TextButton(text="Добавить", on_click=add_note),
                                ft.IconButton(icon=ft.icons.REFRESH, on_click=update),
                            ],
                        ),
                    ],
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Column(
                    create_table(),
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Row(),
                ],
                expand = True,
                alignment = ft.MainAxisAlignment.START,
                horizontal_alignment = ft.CrossAxisAlignment.START,
            )
        else:
            self.detect_platform()
            self.orderspareparts_view()

        return main_window

    def orderservices_view(self):
        def create_table(e=None):
            return [ft.Row()]
        def search_data(e=None):
            pass
        def add_note(e=None):
            pass
        def delete_note(e=None):
            pass
        def update_note(e=None):
            pass
        def update(e=None):
            pass

        search_field = ft.TextField(label = "Поиск", on_change = search_data)
        if self.platform == "phone":
            search_field.expand = True
            main_window = ft.Column([
                ft.Container(
                    content = ft.Row([
                            ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.page.go("/")),
                            ft.Text("Заказы услуг")
                        ],
                        alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    border=ft.border.only(bottom=ft.BorderSide(1, self.border_color)),
                ),
                ft.Column(
                    create_table() + [ft.IconButton(icon=ft.icons.ADD, on_click=add_note),ft.Row()],
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Row([
                        search_field,
                        ft.IconButton(icon=ft.icons.REFRESH, on_click=update)
                    ],
                    expand = True,
                    alignment = ft.MainAxisAlignment.START,
                    vertical_alignment = ft.CrossAxisAlignment.END,
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
                                    ft.Text("Заказы услуг")
                                ],
                                alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            border=ft.border.only(bottom=ft.BorderSide(1, self.border_color)),
                        ),
                        ft.Row([
                                search_field,
                                ft.TextButton(text="Добавить", on_click=add_note),
                                ft.IconButton(icon=ft.icons.REFRESH, on_click=update),
                            ],
                        ),
                    ],
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Column(
                    create_table(),
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Row(),
                ],
                expand = True,
                alignment = ft.MainAxisAlignment.START,
                horizontal_alignment = ft.CrossAxisAlignment.START,
            )
        else:
            self.detect_platform()
            self.orderservices_view()

        return main_window

    def statuses_view(self):
        def create_table(e=None):
            return [ft.Row()]
        def search_data(e=None):
            pass
        def add_note(e=None):
            pass
        def delete_note(e=None):
            pass
        def update_note(e=None):
            pass
        def update(e=None):
            pass

        search_field = ft.TextField(label = "Поиск", on_change = search_data)
        if self.platform == "phone":
            search_field.expand = True
            main_window = ft.Column([
                ft.Container(
                    content = ft.Row([
                            ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.page.go("/")),
                            ft.Text("Статусы")
                        ],
                        alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    border=ft.border.only(bottom=ft.BorderSide(1, self.border_color)),
                ),
                ft.Column(
                    create_table() + [ft.IconButton(icon=ft.icons.ADD, on_click=add_note),ft.Row()],
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Row([
                        search_field,
                        ft.IconButton(icon=ft.icons.REFRESH, on_click=update)
                    ],
                    expand = True,
                    alignment = ft.MainAxisAlignment.START,
                    vertical_alignment = ft.CrossAxisAlignment.END,
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
                                    ft.Text("Статусы")
                                ],
                                alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            border=ft.border.only(bottom=ft.BorderSide(1, self.border_color)),
                        ),
                        ft.Row([
                                search_field,
                                ft.TextButton(text="Добавить", on_click=add_note),
                                ft.IconButton(icon=ft.icons.REFRESH, on_click=update),
                            ],
                        ),
                    ],
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Column(
                    create_table(),
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Row(),
                ],
                expand = True,
                alignment = ft.MainAxisAlignment.START,
                horizontal_alignment = ft.CrossAxisAlignment.START,
            )
        else:
            self.detect_platform()
            self.statuses_view()

        return main_window

    def spareparts_view(self):
        def create_table(e=None):
            return [ft.Row()]
        def search_data(e=None):
            pass
        def add_note(e=None):
            pass
        def delete_note(e=None):
            pass
        def update_note(e=None):
            pass
        def update(e=None):
            pass

        search_field = ft.TextField(label = "Поиск", on_change = search_data)
        if self.platform == "phone":
            search_field.expand = True
            main_window = ft.Column([
                ft.Container(
                    content = ft.Row([
                            ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.page.go("/")),
                            ft.Text("Запчасти")
                        ],
                        alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    border=ft.border.only(bottom=ft.BorderSide(1, self.border_color)),
                ),
                ft.Column(
                    create_table() + [ft.IconButton(icon=ft.icons.ADD, on_click=add_note),ft.Row()],
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Row([
                        search_field,
                        ft.IconButton(icon=ft.icons.REFRESH, on_click=update)
                    ],
                    expand = True,
                    alignment = ft.MainAxisAlignment.START,
                    vertical_alignment = ft.CrossAxisAlignment.END,
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
                                    ft.Text("Запчасти")
                                ],
                                alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            border=ft.border.only(bottom=ft.BorderSide(1, self.border_color)),
                        ),
                        ft.Row([
                                search_field,
                                ft.TextButton(text="Добавить", on_click=add_note),
                                ft.IconButton(icon=ft.icons.REFRESH, on_click=update),
                            ],
                        ),
                    ],
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Column(
                    create_table(),
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Row(),
                ],
                expand = True,
                alignment = ft.MainAxisAlignment.START,
                horizontal_alignment = ft.CrossAxisAlignment.START,
            )
        else:
            self.detect_platform()
            self.spareparts_view()

        return main_window

    def services_view(self):
        def create_table(e=None):
            return [ft.Row()]
        def search_data(e=None):
            pass
        def add_note(e=None):
            pass
        def delete_note(e=None):
            pass
        def update_note(e=None):
            pass
        def update(e=None):
            pass

        search_field = ft.TextField(label = "Поиск", on_change = search_data)
        if self.platform == "phone":
            search_field.expand = True
            main_window = ft.Column([
                ft.Container(
                    content = ft.Row([
                            ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.page.go("/")),
                            ft.Text("Услуги")
                        ],
                        alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    border=ft.border.only(bottom=ft.BorderSide(1, self.border_color)),
                ),
                ft.Column(
                    create_table() + [ft.IconButton(icon=ft.icons.ADD, on_click=add_note),ft.Row()],
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Row([
                        search_field,
                        ft.IconButton(icon=ft.icons.REFRESH, on_click=update)
                    ],
                    expand = True,
                    alignment = ft.MainAxisAlignment.START,
                    vertical_alignment = ft.CrossAxisAlignment.END,
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
                                    ft.Text("Услуги")
                                ],
                                alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            border=ft.border.only(bottom=ft.BorderSide(1, self.border_color)),
                        ),
                        ft.Row([
                                search_field,
                                ft.TextButton(text="Добавить", on_click=add_note),
                                ft.IconButton(icon=ft.icons.REFRESH, on_click=update),
                            ],
                        ),
                    ],
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Column(
                    create_table(),
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Row(),
                ],
                expand = True,
                alignment = ft.MainAxisAlignment.START,
                horizontal_alignment = ft.CrossAxisAlignment.START,
            )
        else:
            self.detect_platform()
            self.services_view()

        return main_window

    def orders_view(self):
        def create_table(e=None):
            return [ft.Row()]
        def search_data(e=None):
            pass
        def add_note(e=None):
            pass
        def delete_note(e=None):
            pass
        def update_note(e=None):
            pass
        def update(e=None):
            pass

        search_field = ft.TextField(label = "Поиск", on_change = search_data)
        if self.platform == "phone":
            search_field.expand = True
            main_window = ft.Column([
                ft.Container(
                    content = ft.Row([
                            ft.IconButton(icon=ft.icons.ARROW_BACK, on_click=lambda _: self.page.go("/")),
                            ft.Text("Заказы")
                        ],
                        alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    border=ft.border.only(bottom=ft.BorderSide(1, self.border_color)),
                ),
                ft.Column(
                    create_table() + [ft.IconButton(icon=ft.icons.ADD, on_click=add_note),ft.Row()],
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Row([
                        search_field,
                        ft.IconButton(icon=ft.icons.REFRESH, on_click=update)
                    ],
                    expand = True,
                    alignment = ft.MainAxisAlignment.START,
                    vertical_alignment = ft.CrossAxisAlignment.END,
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
                                    ft.Text("Заказы")
                                ],
                                alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            border=ft.border.only(bottom=ft.BorderSide(1, self.border_color)),
                        ),
                        ft.Row([
                                search_field,
                                ft.TextButton(text="Добавить", on_click=add_note),
                                ft.IconButton(icon=ft.icons.REFRESH, on_click=update),
                            ],
                        ),
                    ],
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Column(
                    create_table(),
                    alignment = ft.MainAxisAlignment.START,
                    horizontal_alignment = ft.CrossAxisAlignment.START,
                ),
                ft.Row(),
                ],
                expand = True,
                alignment = ft.MainAxisAlignment.START,
                horizontal_alignment = ft.CrossAxisAlignment.START,
            )
        else:
            self.detect_platform()
            self.orders_view()

        return main_window


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
        "/devicetypes": {
            "function": devicetypes_view,
            "view": ft.View(
                route="/devicetypes",
            ),
        },
        "/employees": {
            "function": employees_view,
            "view": ft.View(
                route="/employees",
            ),
        },
        "/orderspareparts": {
            "function": orderspareparts_view,
            "view": ft.View(
                route="/orderspareparts",
            ),
        },
        "/orderservices": {
            "function": orderservices_view,
            "view": ft.View(
                route="/orderservices",
            ),
        },
        "/statuses": {
            "function": statuses_view,
            "view": ft.View(
                route="/statuses",
            ),
        },
        "/spareparts": {
            "function": spareparts_view,
            "view": ft.View(
                route="/spareparts",
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