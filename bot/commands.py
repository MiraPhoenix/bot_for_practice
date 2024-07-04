import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler
from parser_from_habr import parse_habr_vacancies
from create_db_connection import create_db_connection
import asyncio
import concurrent.futures

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Привет! Этот бот создан по заданию для учебной практики Мариной из БВТ2305\n'
                                    f'Чтобы начать поиск вакансий пожалуйста вбейте команду search_by_user_query и следом укажите ваш запрос\n'
                                    f'Пример запроса - /search_by_user_query Python разработчик\n'
                                    f'Для удобства весь функционал собран в команду /help_command')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'/start - Команда для отображения приветственного сообщения и перезапуска бота\n'
                                    f'/search_by_user_query - Команда для поиска новых вакансий по запросу\n'
                                    f'/five_random_vacancies - Показать 5 случайных вакансий из базы данных.\n'
                                    f'/count_all_of_vacancies - Получить общее количество вакансий в базе данных.\n'
                                    f'/part_or_full_time - Выбрать график работы и получить количество вакансий с выбранным графиком.\n'
                                    f'/search_by_company_command - Поиск по компании\n'
                                    f'/search_by_vacancy_command - Поиск по вакансии')

async def search_by_user_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    search_query = ' '.join(context.args)
    logging.info(f"Ищу вакансии по запросу: {search_query}")
    if not search_query:
        await update.message.reply_text('')
        return

    db_conn = create_db_connection()
    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM vacancies;")
        initial_count = cur.fetchone()[0]
    db_conn.close()

    await update.message.reply_text(f'Ищу вакансии по запросу: {search_query}')
    await perform_job_scraping(search_query)
    await update.message.reply_text('Поиск закончен. Чтобы проверить взаимодействие с бд можно воспользоваться одной из предложенный команд в /help_command')

    db_conn = create_db_connection()
    with db_conn.cursor() as cur:
        cur.execute("SELECT company, vacancy, location, salary, skills, link FROM vacancies WHERE id > %s ORDER BY id LIMIT 5;", (initial_count,))
        results = cur.fetchall()
    db_conn.close()

    if not results:
        await update.message.reply_text('Новых вакансий не найдено')
    else:
        await update.message.reply_text(f'5 первых вакансий по запросу: {search_query}')
        for result in results:
            await update.message.reply_text(f'Компания: {result[0]}\nВакансия: {result[1]}\nМестоположение: {result[2]}\nЗарплата: {result[3]}\nСкиллы: {result[4]}\nСсылка: {result[5]}\n')

async def perform_job_scraping(query: str):
    loop = asyncio.get_event_loop()
    executor = concurrent.futures.ThreadPoolExecutor()
    await loop.run_in_executor(executor, parse_habr_vacancies, query)

async def five_random_vacancies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db_conn = create_db_connection()
    with db_conn.cursor() as cur:
        cur.execute("SELECT company, vacancy, location, salary, skills, link FROM vacancies ORDER BY RANDOM() LIMIT 5;")
        results = cur.fetchall()
    db_conn.close()

    if not results:
        await update.message.reply_text('No recent jobs found.')
    else:
        for result in results:
           await update.message.reply_text(f'Компания: {result[0]}\nВакансия: {result[1]}\nМестоположение: {result[2]}\nЗарплата: {result[3]}\nНавыки: {result[4]}\nСсылка: {result[5]}\n')

async def count_all_of_vacancies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db_conn = create_db_connection()
    with db_conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM vacancies;")
        total_count = cur.fetchone()[0]
    db_conn.close()
    await update.message.reply_text(f'Total job vacancies: {total_count}')

async def part_or_full_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    buttons = [
        [
            InlineKeyboardButton("Part-time", callback_data='part_time'),
            InlineKeyboardButton("Full-time", callback_data='full_time')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text('Выбери рабочий график ', reply_markup=reply_markup)

async def search_by_company_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    company_name = ' '.join(context.args)
    logging.info(f"Ищу вакансии по запросу: {company_name}")
    if not company_name:
        await update.message.reply_text('Укажи компанию по которой хочешь получить 5 случайных вакансий после /search_by_company.')
        return

    db_conn = create_db_connection()
    with db_conn.cursor() as cur:
        cur.execute("SELECT company, vacancy, location, salary, skills, link FROM vacancies WHERE company ILIKE %s ORDER BY RANDOM() LIMIT 5;", (f"%{company_name}%",))
        results = cur.fetchall()
    db_conn.close()

    if not results:
        await update.message.reply_text(f'Ничего не найдено по запросу: "{company_name}".')
    else:
        for result in results:
            await update.message.reply_text(f'Компания: {result[0]}\nВакансия: {result[1]}\nМестоположение: {result[2]}\nЗарплата: {result[3]}\nСкиллы: {result[4]}\nСсылка: {result[5]}\n')

async def search_by_vacancy_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    vacancy_name = ' '.join(context.args)
    logging.info(f"Ищу вакансии по запросу: {vacancy_name}")
    if not vacancy_name:
        await update.message.reply_text('Введите название вакансии после команды /search_vacancy.')
        return

    connection = create_db_connection()
    with connection.cursor() as cursor:
        cursor.execute("SELECT company, vacancy, location, salary, skills, link FROM vacancies WHERE vacancy ILIKE %s ORDER BY RANDOM() LIMIT 5;", (f"%{vacancy_name}%",))
        results = cursor.fetchall()
    connection.close()

    if not results:
        await update.message.reply_text(f'Вакансии по запросу "{vacancy_name}" не найдены.')
    else:
        for result in results:
            await update.message.reply_text(f'Компания: {result[0]}\nВакансия: {result[1]}\nМестоположение: {result[2]}\nЗарплата: {result[3]}\nСкиллы: {result[4]}\nСсылка: {result[5]}\n')

