from aiogram.fsm.state import State, StatesGroup


class AddExpenseSG(StatesGroup):
    """Группа состояний для пошагового добавления расхода."""
    waiting_for_amount = State()    
    waiting_for_category = State()  