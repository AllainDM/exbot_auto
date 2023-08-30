# Пример как должен выглядеть config.py

BOT_API_TOKEN = ''
URL = 'https://api.telegram.org/bot'

# Логин пароль для UserSide
loginUS = ""
pswUS = ""

# id общего телеграм чата
chat_id = '-'
# id для отправки в личку, для тестов, чтоб не скидывать в общий чат
tg_user_id = ''

# Логин пароль для goodscat
login_goodscat = ""
psw_goodscat = ""

# Парсить ли goodscat. Он очень долго парсится, лучшее отключать для тестов, если не нужен
gk_need = True
# Задержка для запросов ГК в секундах, чтобы не банило, ставить минимум 3-5
delay = 8

# Старт каждодневного парсера.
# "Время еженедельного выставлено в коде"
time_for_start_parser = "00:10"
# За сколько дней назад нужен отчет(для тестов) по умолчанию 1
days_ago = 1

# Настройка отправки в личку и в общий чат
# Тестовый бот должен кидать только в личку
send_to_ls = True
send_to_chat = True

# Запуск отчетов при запуске программы(для теста или ручной запуск)
global_test_day = True
global_test_week = False

# Запуск дневных по ТО, "выключать" для тестов
day_north = True
day_south = True
day_west = True
day_east = True

# Запуск недельных по ТО, "выключать" для тестов
week_north = True
week_south = True
week_west = True
week_east = True
