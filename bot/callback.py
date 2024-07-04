from telegram import Update
from telegram.ext import ContextTypes, CallbackQueryHandler
from create_db_connection import create_db_connection

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    callback_query = update.callback_query
    callback_data = callback_query.data

    connection = create_db_connection()
    with connection.cursor() as cursor:
        if callback_data == 'part_time':
            cursor.execute("SELECT COUNT(*) FROM vacancies WHERE location ILIKE '%Неполный рабочий день%';")
        elif callback_data == 'full_time':
            cursor.execute("SELECT COUNT(*) FROM vacancies WHERE location ILIKE '%Полный рабочий день%';")
        count = cursor.fetchone()[0]
    connection.close()

    await callback_query.answer()
    await callback_query.edit_message_text(text=f'Вакансий с графиком "{callback_data}": {count}')

button_handler = CallbackQueryHandler(button_handler)
