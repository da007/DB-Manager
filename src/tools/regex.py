from re import match

REGEX_PATTERN_TYPES = {
    "int": r"^\d+$",
    "positive_int": r"^[1-9]\d*$",
    "float": r"^\d+(\.\d{1,2})?$",
    "text": r"^[\d\w\s.,!?\-()]+$",
    "name": r"^[a-zA-Zа-яА-Я\s\-]+$",
    "loggin": r"^[a-zA-Z][a-zA-Z0-9_]{3,19}$",
    "password": r"[a-zA-Z0-9@#$%^&+=!]{8,30}$",
    "phone": r"^\+?\d[\d\s()\-]+$",
    "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "date": r"^\d{4}-\d{2}-\d{2}$",
    "datetime": r"^\d{4}-\d{2}-\d{2}$",
    "part_number": r"^[\w\s.\-/]+$",
    "serial_number": r"^[\w\s.\-/]+$",
    "boolean": r"^(0|1)$",
}

def is_match(type_pattern="text", string=""):
    try:
        pattern = REGEX_PATTERN_TYPES[type_pattern]
    except KeyError as err:
        pattern = REGEX_PATTERN_TYPES["text"]
    finally:
        return bool(match(pattern, string))