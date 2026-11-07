from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Формирует главное меню бота (Reply-кнопки под полем ввода)."""
    kb = [
        [
            KeyboardButton(text="➕ Добавить расход"),
            KeyboardButton(text="❌ Отменить последний")
        ],
        [
            KeyboardButton(text="📊 Траты за сегодня"),
            KeyboardButton(text="📅 Траты за месяц")
        ]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие из меню..."
    )


def get_categories_keyboard() -> InlineKeyboardMarkup:
    """Формирует Inline-кнопки с популярными категориями расходов."""
    categories = ["🍔 Еда", "🚌 Транспорт", "🏠 Жилье", "🎉 Развлечения", "📦 Другое"]
    
    # Создаем по одной Inline-кнопке на каждую категорию
    buttons = []
    for cat in categories:
        # callback_data — это скрытая строка, которая отправится боту при нажатии
        button = InlineKeyboardButton(text=cat, callback_data=f"category:{cat}")
        buttons.append([button])

    return InlineKeyboardMarkup(inline_keyboard=buttons)