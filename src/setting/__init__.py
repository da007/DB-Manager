import tools.cryption as tools
from tools.logging import logger
from setting.const import *

class Setting:
    def __init__(self):
        self.right = "Guest"
        self.user = "guest"
        self.set_setting()

    def set_setting(self):
        data = self.load_config()
        self.app = data["app"]
        self.db = data["db"]

    def load_config(self):
        try:
            with open(SETTING_FILE, "rb") as file:
                encrypted_data = file.read()
                logger.info("Настройки успешно получены.")
                return tools.decrypt(encrypted_data, CRYPT_KEY)
        except (FileNotFoundError, ValueError):
            logger.warning("Не найден файл конфигурации. Загружены настройки по умолчанию")
            return SETTING_DEFAULT

    def save_config(self):
        encrypted_data = tools.encrypt({"app": self.app, "db": self.db}, CRYPT_KEY)
        with open(SETTING_FILE, "wb") as file:
            file.write(encrypted_data)
            logger.info("Настройки успешно сохранены.")
