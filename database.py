import sqlite3
import asyncio
from datetime import datetime


def _init_db_sync(db_name: str) -> None:
    """Синхронное создание таблицы трат."""
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL
            )
            """
        )
        conn.commit()


async def init_db(db_name: str) -> None:
    await asyncio.to_thread(_init_db_sync, db_name)


def _add_expense_sync(db_name: str, user_id: int, amount: float, category: str) -> None:
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO expenses (user_id, amount, category, date)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, amount, category, current_date)
        )
        conn.commit()


async def add_expense(db_name: str, user_id: int, amount: float, category: str) -> None:
    await asyncio.to_thread(_add_expense_sync, db_name, user_id, amount, category)


def _get_today_expenses_sync(db_name: str, user_id: int) -> tuple[float, list[tuple[str, float]]]:
    today = datetime.now().strftime("%Y-%m-%d")
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT SUM(amount) 
            FROM expenses 
            WHERE user_id = ? AND date LIKE ?
            """,
            (user_id, f"{today}%")
        )
        total = cursor.fetchone()
        total_amount = total[0] if total[0] is not None else 0.0

        cursor.execute(
            """
            SELECT category, SUM(amount) 
            FROM expenses 
            WHERE user_id = ? AND date LIKE ?
            GROUP BY category
            """,
            (user_id, f"{today}%")
        )
        categories = cursor.fetchall()

    return total_amount, categories


async def get_today_expenses(db_name: str, user_id: int) -> tuple[float, list[tuple[str, float]]]:
    return await asyncio.to_thread(_get_today_expenses_sync, db_name, user_id)


def _get_month_expenses_sync(db_name: str, user_id: int) -> tuple[float, list[tuple[str, float]]]:
    current_month = datetime.now().strftime("%Y-%m")
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT SUM(amount) 
            FROM expenses 
            WHERE user_id = ? AND date LIKE ?
            """,
            (user_id, f"{current_month}%")
        )
        total = cursor.fetchone()
        total_amount = total[0] if total[0] is not None else 0.0

        cursor.execute(
            """
            SELECT category, SUM(amount) 
            FROM expenses 
            WHERE user_id = ? AND date LIKE ?
            GROUP BY category
            ORDER BY SUM(amount) DESC
            """,
            (user_id, f"{current_month}%")
        )
        categories = cursor.fetchall()

    return total_amount, categories


async def get_month_expenses(db_name: str, user_id: int) -> tuple[float, list[tuple[str, float]]]:
    return await asyncio.to_thread(_get_month_expenses_sync, db_name, user_id)


def _delete_last_expense_sync(db_name: str, user_id: int) -> bool:
    with sqlite3.connect(db_name) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id FROM expenses 
            WHERE user_id = ? 
            ORDER BY id DESC LIMIT 1
            """,
            (user_id,)
        )
        row = cursor.fetchone()

        if not row:
            return False

        last_id = row[0]
        cursor.execute("DELETE FROM expenses WHERE id = ?", (last_id,))
        conn.commit()
        return True


async def delete_last_expense(db_name: str, user_id: int) -> bool:
    return await asyncio.to_thread(_delete_last_expense_sync, db_name, user_id)