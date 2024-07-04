import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, StaleElementReferenceException
from create_db_connection import create_db_connection, add_vacancy_to_db

def parse_habr_vacancies(search_query):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-webgl')
    chrome_options.add_argument('--disable-web-security')
    chrome_options.add_argument('--disable-features=WebRtcHideLocalIpsWithMdns,WebContentsDelegate::CheckMediaAccessPermission')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--remote-debugging-port=9222')
    chrome_options.add_argument('--enable-features=NetworkService,NetworkServiceInProcess')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option('prefs', {
        'profile.managed_default_content_settings.images': 2,
        'disk-cache-size': 4096
    })

    set_driver_for_chrome = webdriver.Chrome(options=chrome_options)

    set_db_connection = create_db_connection()

    try:
        set_driver_for_chrome.get('https://career.habr.com')

        search_box = set_driver_for_chrome.find_element(By.CSS_SELECTOR, '.l-page-title__input')
        search_box.send_keys(search_query)
        search_box.send_keys(Keys.RETURN)

        time.sleep(1)

        while True:
            vacancy_cards = set_driver_for_chrome.find_elements(By.CLASS_NAME, 'vacancy-card__info')
            for card in vacancy_cards:
                try:
                    company = card.find_element(By.CLASS_NAME, 'vacancy-card__company-title').text
                except NoSuchElementException:
                    company = 'Компания не указана'

                title = card.find_element(By.CLASS_NAME, 'vacancy-card__title').text
                link = card.find_element(By.TAG_NAME, 'a').get_attribute('href')

                try:
                    location = card.find_element(By.CLASS_NAME, 'vacancy-card__meta').text
                except NoSuchElementException:
                    location = 'Местоположение не указано'

                try:
                    salary = card.find_element(By.CLASS_NAME, 'vacancy-card__salary').text
                except NoSuchElementException:
                    salary = 'Зарплата не указана'

                try:
                    skills = card.find_element(By.CLASS_NAME, 'vacancy-card__skills').text
                except NoSuchElementException:
                    skills = 'Навыки не указаны'

                vacancy_id = add_vacancy_to_db(set_db_connection, company, title, location, salary, skills, link)

                print(f'Компания: {company}\nВакансия: {title}\nСсылка: {link}\nМестоположение: {location}\nЗарплата: {salary}\nСкиллы: {skills}')

            try:
                next_button = set_driver_for_chrome.find_element(By.CSS_SELECTOR, 'a.button-comp--appearance-pagination-button[rel="next"]')
                set_driver_for_chrome.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(1)

                for _ in range(3):
                    try:
                        set_driver_for_chrome.execute_script("arguments[0].click();", next_button)
                        break
                    except StaleElementReferenceException:
                        next_button = set_driver_for_chrome.find_element(By.CSS_SELECTOR, 'a.button-comp--appearance-pagination-button[rel="next"]')
                        time.sleep(1)
                else:
                    break

                time.sleep(1)
            except (NoSuchElementException, ElementClickInterceptedException):
                break

    finally:
        set_driver_for_chrome.quit()
        set_db_connection.close()
