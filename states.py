from aiogram.fsm.state import State, StatesGroup


class AddExpenseSG(StatesGroup):
    """Группа состояний для пошагового добавления расхода."""
    waiting_for_amount = State()    # Шаг 1: Ожидание ввода суммы трат
    waiting_for_category = State()  # Шаг 2: Ожидание выбора категории