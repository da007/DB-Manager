import flet as ft
import mysql.connector

import database
import setting
import config
import tools

class RepairShopApp:

    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "DB manager"

        self.setting = setting.Setting()
        self.database = database.Database(self.setting.db)
        self.alert_dialogs_stack = []
        self.platform = None

        self.page.on_resized = self.detect_platform
        self.page.on_route_change = self.route_change
        self.page.on_close = self.on_close

        self.set_color_theme()
        self.detect_platform()
        self.page.go("/")

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

    def set_color_theme(self):
        self.page.theme_mode = config.THEME_MODES[self.setting.app["theme_mode"]]
        self.page.theme = config.THEME_COLORS[self.setting.app["theme_color"]]
        self.border_color = ft.Colors.BLACK if self.page.theme_mode == ft.ThemeMode.LIGHT else ft.Colors.WHITE
        self.page.update()

    def route_change(self, e):
        self.set_color_theme()
        self.page.views.clear()
        if self.page.route in setting.AVAILABLE_ROUTES[self.setting.right]:
            route = self.page.route
        else:
            route = "/"

        template_view = self.routing_map.get(route)
        view = template_view["view"]
        view.controls = [template_view["function"](self)]
        self.page.views.append(view)
        tools.logger.info(f"Переход по маршруту {route}")
        self.page.update()

    def detect_platform(self, e=None): 
        window_width = self.page.window.width or 0
        window_height = self.page.window.height or 0
        user_agent = self.page.client_user_agent or ""

        platform = "phone"
        if ("Windows" in user_agent or "Linux" in user_agent or "Mac" in user_agent) or self.page.platform in ("windows", "macos", "linux") or (window_width and window_width >= window_height):
            platform = "desktop"

        if self.platform != platform:
            tools.logger.info(f"Платформа изменена {platform}")
            self.platform = platform
            self.update_views()

    def update_views(self):
        if self.page.views:
            self.route_change(None)

    def home_view(self):
        def reconnect(e=None):
            self.database.connect(self.setting.db)
            if self.database.is_connected:
                status_row.controls = [
                    ft.Text("Статус: Подключенно"),
                    ft.IconButton(icon=ft.Icons.REFRESH, on_click=reconnect),
                ]
            else:
                status_row.controls = [
                    ft.Text("Статус: Не подключенно"),                    
                    ft.IconButton(icon=ft.Icons.REFRESH, on_click=reconnect),
                ]
            self.page.update()
        def on_menu_click(e=None):
            self.page.go(f"/tables/{e.control.data}")

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
        items = [all_items[table_name] for table_name in setting.AVAILABLE_TABLES[self.setting.right]]
        if self.database.is_connected:
            status_row = ft.Row([
                    ft.Text("Статус: Подключенно"),
                    ft.IconButton(icon=ft.Icons.REFRESH, on_click=reconnect),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        else:
            status_row = ft.Row([
                    ft.Text("Статус: Не подключенно"),
                    ft.IconButton(icon=ft.Icons.REFRESH, on_click=reconnect),
                ],
                alignment=ft.MainAxisAlignment.START,
                vertical_alignment=ft.CrossAxisAlignment.START,
            )

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
                            status_row,
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Container(
                        content=ft.Image(
                            src=config.THEME_LOGOS[self.setting.app["theme_mode"]],
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
                            status_row,
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Container(
                        content=ft.Image(
                            src=config.THEME_LOGOS[self.setting.app["theme_mode"]],
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
            self.page.go("/")

        return main_window

    def loggin_view(self):
        def submit(e):
            loggin = loggin_field.value.strip()
            password = password_field.value.strip()
            if tools.regex.is_match("loggin", loggin) and tools.regex.is_match("password", password):
                try:
                    results = self.database.manager.get_user(loggin)
                    if results and tools.password.verify_password(results[1], password):
                        self.setting.right = results[0]
                        self.setting.user = loggin
                        self.page.go("/")
                        self.show_alert_dialog(content=ft.Text(f"Здравствуйте, {loggin}"))
                    else:
                        self.show_alert_dialog(content=ft.Text("Неправильные пароль или логин"))
                except mysql.connector.Error as err:
                    self.show_alert_dialog(content=ft.Text(f"Ошибка при выполнении запроса: {err}"))
            else:
                self.show_alert_dialog(content=ft.Text("Некоректно введен пароль или логин"))
            self.page.update()

        def on_change_field(e):
            if loggin_field.value and password_field.value:
                loggin_button.disabled=False
            else:
                loggin_button.disabled=True
            self.page.update()

        loggin_field = ft.TextField(label = "Логин", on_change=on_change_field)
        password_field = ft.TextField(label = "Пароль", on_change=on_change_field, password=True, can_reveal_password=True)
        loggin_button = ft.ElevatedButton(text="Войти", on_click=submit, disabled=True)
        
        if self.platform == "phone":
            main_window = ft.Column([
                ft.IconButton( icon=ft.Icons.ARROW_BACK, on_click=lambda _: self.page.go("/")),
                    ft.Row([
                            ft.Column([
                                    ft.Text("Авторизация"),
                                    loggin_field,
                                    password_field,
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
                                    loggin_field,
                                    password_field,
                                    ft.Row([
                                        ft.ElevatedButton(text="Назад", on_click=lambda _: self.page.go("/")),
                                        ft.ElevatedButton(text="Войти", on_click=submit),
                                        ],
                                        alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                ],
                                width = 400,
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
            self.page.go("/")

        return main_window

    def setting_view(self):
        def on_change_field(e=None):
            if host_field.value and user_field.value and db_field.value:
                button_connect.disabled=False
            else:
                button_connect.disabled=True
            self.page.update()

        def on_change_dropdown(e=None):
            self.page.theme_mode = config.THEME_MODES[th_m_drop.value]
            self.page.theme = config.THEME_COLORS[th_c_drop.value]
            self.page.update()

        def on_click_connect(e=None):
            setting = {
                "host": host_field.value,
                "user": user_field.value,
                "password": pw_field.value,
                "database": db_field.value
            }
            self.database.connect(setting)
            if self.database.is_connected:
                self.show_alert_dialog(content=ft.Text("Подключение успешно!"))
            else:
                self.show_alert_dialog(content=ft.Text(f"Ошибка подключения."))

        def on_click_save(e=None):
            self.setting.app["theme_mode"] = th_m_drop.value
            self.setting.app["theme_color"] = th_c_drop.value
            self.setting.db["host"] = host_field.value
            self.setting.db["user"] = user_field.value
            self.setting.db["password"] = pw_field.value
            self.setting.db["database"] = db_field.value
            self.database.connect(self.setting.db)
            self.setting.save_config()
            self.page.go("/")
        
        host_field = ft.TextField(label = "Host", on_change=on_change_field)
        user_field = ft.TextField(label = "User", on_change=on_change_field)
        pw_field = ft.TextField(label = "Password", on_change=on_change_field, password=True, can_reveal_password=True)
        db_field = ft.TextField(label = "Database", on_change=on_change_field)
        
        host_field.value=self.setting.db["host"]
        user_field.value=self.setting.db["user"]
        db_field.value=self.setting.db["database"]
        
        th_m_drop = ft.Dropdown(
            label="Тема",
            options=[ft.dropdown.Option(key) for key in config.THEME_MODES.keys()],
            on_change=on_change_dropdown,
            value=self.setting.app["theme_mode"],
        )
        th_c_drop = ft.Dropdown(
            label="Цвет",
            options=[ft.dropdown.Option(key) for key in config.THEME_COLORS.keys()],
            on_change=on_change_dropdown,
            value=self.setting.app["theme_color"],
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
            self.page.go("/")

        return main_window

    def table_view(self, table_name):
        def get_row(content):
            controls = content.controls
            return {control.data:control.value for control in controls}
        def check_row_values(content):
            controls = content.controls
            nessesary_columns_list = list(database.TABLES[table_name]["nessesary_columns"])
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
            pattern_type = database.COLUMN_MAPPING[column_name]
            if value:
                if tools.regex.is_match(pattern_type, value):
                    e.control.error_text = None
                else:
                    e.control.error_text = "Поле заполнено не правильно"
            else:
                e.control.error_text = "Данное поле нужно заполнить"
            self.page.update()
        def error_empty(content):
            controls = content.controls
            nessesary_columns_list = list(database.TABLES[table_name]["nessesary_columns"])
            for control in controls:
                if control.data in nessesary_columns_list:
                    if not control.value:
                        control.error_text = "Данное поле нужно заполнить"
            self.page.update()
        def action_button_click(e=None, action=lambda _d, _c: None):
            dialog = e.control.parent
            text = e.control.text
            content = dialog.content
            if text == "Отмена":
                self.page.close(dialog)
            else:
                action(dialog, content)
            self.page.update()
        def create_controls(row, table_column_names, table_row_dependens, primary_columns=[]):
            controls = []
            for table_column_name in table_column_names:
                control = None
                is_disabled = table_column_name in primary_columns
                for table_row_dependen in table_row_dependens:
                    if table_column_name in table_row_dependen["column_name"]:
                        options = []
                        for referenced_table_row in table_row_dependen["referenced_table_rows"]:
                            options.append(ft.dropdown.Option(
                                    key=str(referenced_table_row[table_row_dependen["referenced_column_name"]]),
                                    text=" ".join([str(referenced_table_row[column_name]) for column_name in database.TABLES[table_row_dependen['referenced_table_name']]["label_on_choose"]])
                                )
                            )
                        control = ft.Dropdown(options=options)
                if not control:
                    control=ft.TextField()
                control.data = table_column_name
                control.label = database.COLUMN_NAMES[table_column_name]
                control.on_change = check_value
                control.disabled = is_disabled
                if row:
                    control.value=row[table_column_name]
                if control:
                    if control.data in database.TABLES[table_name]["nessesary_columns"]:
                        control.label = control.label+'*'
                    controls.append(control)
            return controls

        def create_table(table_name, table_rows):
            table_container_in = ft.Row()
            if table_rows:
                def sync_scroll(e: ft.OnScrollEvent):
                    main_table_container_in.scroll_to(offset=e.pixels, delta=e.scroll_delta, duration=0)

                main_columns = [
                    ft.DataColumn(ft.Text(database.COLUMN_NAMES[key])) for key in table_rows[0].keys()
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
                        if tools.search.is_perhabs_match(query, value):
                            match = True
                            break
                    if not match:
                        main_row.visible = False
                        last_row.visible = False
            self.page.update()
        def add_note(e=None):
            def action(dialog, content):
                is_checked = check_row_values(content)
                if is_checked:
                    new_row = get_row(content)
                    self.database.manager.add_table_row(table_name, new_row)
                    self.page.close(dialog)
                    update()
                else:
                    error_empty(content)
            content = ft.Column(
                scroll=ft.ScrollMode.AUTO,
                expand = True,
            )
            actions = [
                ft.TextButton("Отмена", on_click=lambda e, a=action: action_button_click(e, a)),
                ft.TextButton("Применить", on_click=lambda e, a=action: action_button_click(e, a)),
            ]
            
            try:
                table_column_names = []
                for column_name in self.database.manager.get_table_rows(table_name)[0].keys():
                    if column_name not in database.TABLES[table_name]["passed_columns"]:
                        table_column_names.append(column_name)
                table_row_dependens = self.database.manager.get_table_row_dependens(table_name)
                controls = create_controls([], table_column_names, table_row_dependens)
                content.controls.extend(controls)

                self.show_alert_dialog(title="Добавить", content=content, actions=actions, modal=True)
            except mysql.connector.Error as err:
                self.show_alert_dialog(content=ft.Text(f"Ошибка при выполнении запроса: {err}"))
        def delete_row(e=None,table_name=None, row=None):
            try:
                referenced_row_rows = self.database.manager.get_referenced_row_rows(table_name, row)
                if referenced_row_rows:
                    if self.settin.right == "Administrator":
                        actions = [
                            ft.TextButton("Отмена", on_click=action_button_click),
                        ]
                        for referenced_row_row in referenced_row_rows:
                            referenced_table_name = referenced_row_row["referenced_table_name"]
                            referenced_table_rows = referenced_row_row["referenced_table_rows"]
                            content.controls.append(create_table(referenced_table_name, referenced_table_rows))
                        self.show_alert_dialog(title="Удаление", content=content, actions=actions, modal=True)
                    else:
                        actions = [
                            ft.TextButton("Отмена", on_click=action_button_click),
                        ]
                        self.show_alert_dialog(title="Удаление", content=ft.Text("Есть зависимые записи. Удаление не возможно!"), actions=actions, modal=True)
                else:
                    self.database.manager.delete_table_rows(table_name, row)
                update()
            except mysql.connector.Error as err:
                self.show_alert_dialog(content=ft.Text(f"Ошибка при выполнении запроса: {err}"))
        def change_row(e=None,table_name=None, row=None):
            def action(dialog, content):
                is_checked = check_row_values(content)
                if is_checked:
                    new_row = get_row(content)
                    self.database.manager.update_table_row(table_name, new_row)
                    self.page.close(dialog)
                    update()
                else:
                    error_empty(content)

            content = ft.Column(
                scroll=ft.ScrollMode.AUTO,
                expand = True,
            )
            actions = [
                ft.TextButton("Отмена", on_click=lambda e, a=action: action_button_click(e, a)),
                ft.TextButton("Применить", on_click=lambda e, a=action: action_button_click(e, a)),
            ]
            try:
                primary_columns = self.database.manager.get_primary_columns(table_name)
                primary_keys = {primary_column: row[primary_column] for primary_column in primary_columns}
                row = self.database.manager.get_table_row(table_name, primary_keys = primary_keys)
                table_column_names = row.keys()
                table_row_dependens = self.database.manager.get_table_row_dependens(table_name)
                controls = create_controls(row, table_column_names, table_row_dependens, primary_columns)
                content.controls.extend(controls)

                self.show_alert_dialog(title="Обновить", content=content, actions=actions, modal=True)
            except mysql.connector.Error as err:
                self.show_alert_dialog(content=ft.Text(f"Ошибка при выполнении запроса: {err}"))
        def update(e=None):
            try:
                table_rows = self.database.manager.get_table_rows(
                    table_name, database.TABLES[table_name]["view_columns"],
                    database.TABLES[table_name]["join_tables"]
                )
                table_container_out.controls=[create_table(table_name, table_rows)]
                self.page.update()
            except mysql.connector.Error as err:
                self.show_alert_dialog(content=ft.Text(f"Ошибка при выполнении запроса: {err}"))
            
        table_rows = self.database.manager.get_table_rows(
            table_name, database.TABLES[table_name]["view_columns"],
            database.TABLES[table_name]["join_tables"]
        )
        table_container_out=ft.Column(
            controls=[create_table(table_name, table_rows)],
            alignment = ft.MainAxisAlignment.START,
            expand=True,
            horizontal_alignment = ft.CrossAxisAlignment.START,
        )
        search_field = ft.TextField(label = "Поиск", on_change = search_data)
        if self.platform == "phone":
            table_container_out.controls.append(ft.IconButton(icon=ft.Icons.ADD, on_click=add_note))
            search_field.expand = True
            main_window = ft.Column([
                ft.Container(
                    content = ft.Row([
                            ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda _: self.page.go("/")),
                            ft.Text(database.TABLES[table_name]["name"])
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
                                    ft.Text(database.TABLES[table_name]["name"])
                                ],
                                alignment = ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            border=ft.border.only(bottom=ft.BorderSide(1, self.border_color)),
                        ),
                        ft.Row([
                                search_field,
                                ft.IconButton(icon=ft.Icons.REFRESH, on_click=update),
                                ft.TextButton(text="Добавить", on_click=add_note),
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
            self.page.go("/")

        return main_window

    def on_close(self,e):
        self.setting.save_config()
        self.page.window_close()

    routing_map = {
        "/": {
            "function": lambda self: self.home_view(),
            "view": ft.View(
                route="/",
            ),
        },
        "/loggin": {
            "function": lambda self: self.loggin_view(),
            "view": ft.View(
                route="/setting",
            ),
        },
        "/setting": {
            "function": lambda self: self.setting_view(),
            "view": ft.View(
                route="/setting",
            ),
        },
        "/tables/clients": {
            "function": lambda self: self.table_view("clients"),
            "view": ft.View(
                route="/tables/clients",
            ),
        },
        "/tables/devices": {
            "function": lambda self: self.table_view("devices"),
            "view": ft.View(
                route="/tables/devices",
            ),
        },
        "/tables/device_types": {
            "function": lambda self: self.table_view("device_types"),
            "view": ft.View(
                route="/tables/device_types",
            ),
        },
        "/tables/employees": {
            "function": lambda self: self.table_view("employees"),
            "view": ft.View(
                route="/tables/employees",
            ),
        },
        "/tables/order_spare_parts": {
            "function": lambda self: self.table_view("order_spare_parts"),
            "view": ft.View(
                route="/tables/order_spare_parts",
            ),
        },
        "/tables/order_services": {
            "function": lambda self: self.table_view("order_services"),
            "view": ft.View(
                route="/tables/order_services",
            ),
        },
        "/tables/statuses": {
            "function": lambda self: self.table_view("statuses"),
            "view": ft.View(
                route="/tables/statuses",
            ),
        },
        "/tables/spare_parts": {
            "function": lambda self: self.table_view("spare_parts"),
            "view": ft.View(
                route="/tables/spare_parts",
            ),
        },
        "/tables/services": {
            "function": lambda self: self.table_view("services"),
            "view": ft.View(
                route="/tables/services",
            ),
        },
        "/tables/orders": {
            "function": lambda self: self.table_view("orders"),
            "view": ft.View(
                route="/tables/orders",
            ),
        }
    }

ft.app(target=RepairShopApp)