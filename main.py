import os
import dotenv
import logging
from telegram.ext import Application, CommandHandler

from bot.commands import (
    start,
    help_command,
    search_by_user_query,
    five_random_vacancies,
    count_all_of_vacancies,
    part_or_full_time,
    search_by_company_command,
    search_by_vacancy_command
)
from bot.callback import button_handler

dotenv.load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help_command", help_command))
    application.add_handler(CommandHandler("search_by_user_query", search_by_user_query))
    application.add_handler(CommandHandler("five_random_vacancies", five_random_vacancies))
    application.add_handler(CommandHandler("count_all_of_vacancies", count_all_of_vacancies))
    application.add_handler(CommandHandler("part_or_full_time", part_or_full_time))
    application.add_handler(CommandHandler("search_by_company_command", search_by_company_command))
    application.add_handler(CommandHandler("search_by_vacancy_command", search_by_vacancy_command))
    application.add_handler(button_handler)

    application.run_polling()

if __name__ == '__main__':
    main()
