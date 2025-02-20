from flet import ThemeMode, Theme, Colors

THEME_MODES = {
    "Светлая стандартная": ThemeMode.LIGHT,
    "Темная стандартная": ThemeMode.DARK
}
THEME_COLORS = {
    "Индиго": Theme(
        color_scheme_seed=Colors.INDIGO,
        use_material3=True,
    ),
    "Фиолетовая ночь": Theme(
        color_scheme_seed=Colors.DEEP_PURPLE,
        use_material3=True,
    ),
    "Лесная зелень": Theme(
        color_scheme_seed=Colors.GREEN,
        use_material3=True,
    ),
    "Песчаный берег": Theme(
        color_scheme_seed=Colors.AMBER,
        use_material3=True,
    ),
    "Лазурный бриз": Theme(
        color_scheme_seed=Colors.BLUE_400,
        use_material3=True,
    ),
    "Тестовый": Theme(
        color_scheme_seed=Colors.random(),
        use_material3=True
    ),
}
THEME_LOGOS = {
    "Светлая стандартная": r"source\img\logo\light_default.png",
    "Темная стандартная": r"source\img\logo\dark_default.png"
}