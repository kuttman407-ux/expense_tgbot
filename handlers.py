from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import load_config
from states import AddExpenseSG
from keyboards import get_main_keyboard, get_categories_keyboard
from database import (
    add_expense,
    get_today_expenses,
    get_month_expenses,
    delete_last_expense
)

# Создаём роутер (маршрутизатор) обработчиков
router = Router()
# Загружаем конфигурацию для доступа к имени БД
config = load_config()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start."""
    # Сбрасываем активное состояние FSM, если оно было
    await state.clear()
    
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n\n"
        "Я бот для удобного учёта твоих личных расходов.\n"
        "Воспользуйся кнопками меню ниже для управления транзакциями.",
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "➕ Добавить расход")
async def start_add_expense(message: Message, state: FSMContext):
    """Начало сценария добавления расхода: переход к первому шагу FSM."""
    await state.set_state(AddExpenseSG.waiting_for_amount)
    await message.answer("Введите сумму расхода (например: 250 или 15.5):")


@router.message(AddExpenseSG.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext):
    """Валидация и обработка введённой суммы трат."""
    # Заменяем запятую на точку, чтобы пользователь мог ввести и "15,5", и "15.5"
    text = message.text.replace(",", ".")
    
    try:
        amount = float(text)
        if amount <= 0:
            await message.answer("Сумма должна быть больше нуля! Попробуйте ещё раз:")
            return
    except ValueError:
        await message.answer("Ошибка ввода! Введите числовое значение (например: 150 или 45.5):")
        return

    # Сохраняем валидную сумму в временную память FSM
    await state.update_data(amount=amount)
    
    # Переходим ко второму шагу FSM (выбор категории)
    await state.set_state(AddExpenseSG.waiting_for_category)
    
    await message.answer(
        f"Сумма {amount:.2f} принята.\nТеперь выберите категорию расхода:",
        reply_markup=get_categories_keyboard()
    )


@router.callback_query(AddExpenseSG.waiting_for_category, F.data.startswith("category:"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора категории через Inline-кнопку и сохранение в БД."""
    # Извлекаем название категории из callback_data ("category:🍔 Еда" -> "🍔 Еда")
    category = callback.data.split(":", 1)[1]
    
    # Считываем ранее сохранённые данные из FSM
    user_data = await state.get_data()
    amount = user_data.get("amount")

    # Сохраняем запись в базу данных
    await add_expense(
        db_name=config.db_name,
        user_id=callback.from_user.id,
        amount=amount,
        category=category
    )

    # Завершаем сценарий FSM и очищаем память
    await state.clear()

    # Редактируем сообщение с кнопками на итоговое подтверждение
    await callback.message.edit_text(
        f"✅ **Расход успешно записан!**\n\n"
        f"💵 Сумма: {amount:.2f}\n"
        f"🏷 Категория: {category}",
        parse_mode="Markdown"
    )
    # Обязательный ответ на CallbackQuery, чтобы у пользователя убралась «загрузка» на кнопке
    await callback.answer()


@router.message(F.text == "📊 Траты за сегодня")
async def show_today_expenses(message: Message):
    """Вывод статистики расходов за текущие сутки."""
    total, categories = await get_today_expenses(config.db_name, message.from_user.id)
    
    if total == 0:
        await message.answer("За сегодняшний день расходов пока нет! 🎉")
        return

    text = f"📊 **Ваши расходы за сегодня:** {total:.2f}\n\n"
    text += "Разбивка по категориям:\n"
    for cat, sum_amt in categories:
        text += f"• {cat}: {sum_amt:.2f}\n"

    await message.answer(text, parse_mode="Markdown")


@router.message(F.text == "📅 Траты за месяц")
async def show_month_expenses(message: Message):
    """Вывод статистики расходов за текущий месяц."""
    total, categories = await get_month_expenses(config.db_name, message.from_user.id)
    
    if total == 0:
        await message.answer("За этот месяц расходов пока нет! 🎉")
        return

    text = f"📅 **Ваши расходы за текущий месяц:** {total:.2f}\n\n"
    text += "Разбивка по категориям:\n"
    for cat, sum_amt in categories:
        text += f"• {cat}: {sum_amt:.2f}\n"

    await message.answer(text, parse_mode="Markdown")


@router.message(F.text == "❌ Отменить последний")
async def cancel_last_expense(message: Message):
    """Удаление последней внесённой транзакции."""
    success = await delete_last_expense(config.db_name, message.from_user.id)
    if success:
        await message.answer("🗑 Последний внесенный расход успешно удалён!")
    else:
        await message.answer("У вас нет сохранённых расходов для удаления.")