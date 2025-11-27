# Telegram Bot - Анкета

Telegram бот на aiogram для заполнения анкеты с множеством разделов.

## Установка

1. Клонируйте репозиторий или скачайте файлы
2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` в корне проекта и заполните переменные окружения:
- `BOT_TOKEN` - токен вашего бота от @BotFather
- `ADMIN_ID` - ваш Telegram ID (опционально)
- `GOOGLE_SHEETS_ID` - ID вашей Google таблицы (можно взять из URL)

4. Создайте файл `credentials.json` в корне проекта:
   - Скачайте ключ сервисного аккаунта из Google Cloud Console
   - Сохраните его как `credentials.json` в корне проекта
   - Убедитесь, что сервисный аккаунт имеет доступ к вашей Google таблице

## Запуск

```bash
python bot.py
```

## Деплой на VPS (Ubuntu/Debian)

### Подготовка сервера
- Обновите систему и установите зависимости:
  ```bash
  sudo apt update && sudo apt upgrade -y
  sudo apt install -y python3 python3-venv python3-pip git
  ```
- Создайте отдельного системного пользователя:
  ```bash
  sudo adduser --system --group --home /opt/anketa-bot bot
  sudo install -d -o bot -g bot /opt/anketa-bot
  ```

### Развёртывание проекта
- Клонируйте репозиторий:
  ```bash
  sudo -u bot git clone <URL_РЕПОЗИТОРИЯ> /opt/anketa-bot
  ```
- Скопируйте `.env` и `credentials.json`:
  ```bash
  sudo cp /path/to/.env /opt/anketa-bot/.env
  sudo cp /path/to/credentials.json /opt/anketa-bot/credentials.json
  sudo chown bot:bot /opt/anketa-bot/.env /opt/anketa-bot/credentials.json
  sudo chmod 600 /opt/anketa-bot/.env /opt/anketa-bot/credentials.json
  ```
- Сделайте скрипты исполняемыми (если требуется):
  ```bash
  sudo chmod +x /opt/anketa-bot/scripts/*.sh
  ```
- Установите зависимости в виртуальное окружение:
  ```bash
  cd /opt/anketa-bot
  sudo -u bot bash scripts/setup-venv.sh
  ```

### Настройка systemd
- Скопируйте и включите сервис:
  ```bash
  sudo cp /opt/anketa-bot/deploy/telegram-anketa-bot.service /etc/systemd/system/telegram-anketa-bot.service
  sudo systemctl daemon-reload
  sudo systemctl enable telegram-anketa-bot.service
  sudo systemctl start telegram-anketa-bot.service
  ```
- При необходимости отредактируйте `User`, `Group`, `WorkingDirectory`, `EnvironmentFile` и `ExecStart` в `/etc/systemd/system/telegram-anketa-bot.service`.
- Посмотрите статус:
  ```bash
  sudo systemctl status telegram-anketa-bot.service
  ```

### Обновление и логи
- Для обновления кода с GitHub:
  ```bash
  cd /opt/anketa-bot
  sudo -u bot git pull origin main  # или master, в зависимости от вашей ветки
  sudo -u bot bash scripts/post-update.sh
  ```
  При необходимости можно переопределить имя сервиса: `SERVICE_NAME=custom.service sudo -u bot bash scripts/post-update.sh`.
  
  **Важно**: После обновления проверьте, что все зависимости установлены и сервис перезапустился:
  ```bash
  sudo systemctl status telegram-anketa-bot.service
  ```
- Для просмотра логов:
  ```bash
  journalctl -u telegram-anketa-bot.service -f
  ```
- Для просмотра последних 100 строк логов:
  ```bash
  journalctl -u telegram-anketa-bot.service -n 100
  ```

## Структура проекта

```
.
├── bot.py              # Главный файл запуска бота
├── config.py           # Конфигурация и настройки
├── states.py           # FSM состояния для анкеты
├── keyboards.py        # Клавиатуры бота
├── utils.py            # Утилиты для работы с данными
├── google_sheets.py    # Интеграция с Google Sheets
├── game_utils.py       # Игровые утилиты (прогресс, мотивация)
├── credentials.json    # Ключ сервисного аккаунта Google
├── handlers/           # Обработчики
│   ├── __init__.py
│   ├── start.py        # Обработчики команд /start, /help
│   └── form.py         # Обработчики заполнения анкеты
├── data/               # Сохраненные данные (создается автоматически)
│   ├── photos/         # Фото пользователей
│   └── documents/      # Документы пользователей
└── requirements.txt    # Зависимости проекта
```

## Функционал

Бот поддерживает заполнение анкеты по следующим разделам с ветвлением для граждан РФ и иностранных граждан:

1. **Личные данные** - ФИО, дата рождения, место рождения, гражданство, пол
2. **Выбор гражданства** - Гражданин России / Иностранный гражданин
3. **Паспортные данные** - серия/номер, кем выдан, дата выдачи, адреса, фото паспорта
4. **Контактная информация** - телефон
5. **Документы** - медкнижка, регистрация, СНИЛС, ИНН
   - **Для иностранцев дополнительно**: ID, дактилоскопия, медосмотр по дактилоскопии, проверка в Реестре МВД
6. **Готовность к работе** - когда готов начать вахту, готовность к командировкам, город проживания
7. **Согласия** - обработка ПД, готовность к вахте
8. **Комментарии** - дополнительные комментарии
9. **Подтверждения (только для иностранцев)** - подтверждения об отсутствии заболеваний, готовность оформить документы, самозанятость, компенсация затрат

## Особенности

- **Ветвление логики** - разные вопросы для граждан РФ и иностранных граждан
- Пошаговое заполнение с возможностью пропуска полей
- Сохранение данных в SQLite БД и Google Sheets
- Загрузка файлов (фото паспорта, медицинская книжка)
- Предпросмотр анкеты перед отправкой
- Возможность редактирования разделов
- Игровые элементы: прогресс-бар, мотивационные сообщения
- Автоматическая запись в Google таблицу при отправке анкеты
- Минимальный набор полей в таблице для удобства работы

## Получение токена бота

1. Найдите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в файл `.env`

## Настройка Google Sheets

1. Создайте Google таблицу или используйте существующую
2. Поделитесь таблицей с email сервисного аккаунта: `tg-bot-shhets@anketa-478017.iam.gserviceaccount.com`
   - Дайте права "Редактор"
3. Скопируйте ID таблицы из URL:
   - URL выглядит так: `https://docs.google.com/spreadsheets/d/ВАШ_ID_ТАБЛИЦЫ/edit`
   - Скопируйте `ВАШ_ID_ТАБЛИЦЫ` и добавьте в `.env` как `GOOGLE_SHEETS_ID`
4. При первой отправке анкеты автоматически создастся лист "Анкеты" с заголовками

## Лицензия

MIT

