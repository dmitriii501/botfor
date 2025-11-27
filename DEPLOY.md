# Инструкции по развертыванию и обновлению

## Загрузка изменений на GitHub

### Первая загрузка (если репозиторий еще не создан)

1. Создайте новый репозиторий на GitHub
2. Инициализируйте git в локальной папке:
   ```bash
   cd "C:\Users\dimah\OneDrive\Рабочий стол\Новая папка\botfor"
   git init
   git add .
   git commit -m "Initial commit: Telegram bot for form filling"
   git branch -M main
   git remote add origin https://github.com/ВАШ_USERNAME/НАЗВАНИЕ_РЕПОЗИТОРИЯ.git
   git push -u origin main
   ```

### Обновление существующего репозитория

```bash
cd "C:\Users\dimah\OneDrive\Рабочий стол\Новая папка\botfor"
git add .
git commit -m "Обновление бота: ветвление по гражданству, новые поля, обновленная структура"
git push origin main
```

**Важно**: Убедитесь, что файлы `.env` и `credentials.json` не попадают в репозиторий (они уже в `.gitignore`)

## Обновление бота на VPS

### Быстрое обновление (если бот уже развернут)

1. Подключитесь к VPS по SSH:
   ```bash
   ssh user@your-vps-ip
   ```

2. Перейдите в директорию бота и обновите код:
   ```bash
   cd /opt/anketa-bot
   sudo -u bot git pull origin main
   ```

   **Если запрашивает пароль**, используйте один из вариантов ниже.

3. Обновите зависимости и перезапустите сервис:
   ```bash
   sudo -u bot bash scripts/post-update.sh
   ```

4. Проверьте статус:
   ```bash
   sudo systemctl status telegram-anketa-bot.service
   ```

### Решение проблемы с паролем при git pull

Если при `git pull` запрашивается пароль, это означает, что репозиторий использует HTTPS вместо SSH. Есть несколько решений:

#### Вариант 1: Использовать SSH вместо HTTPS (рекомендуется)

1. Проверьте текущий remote URL:
   ```bash
   cd /opt/anketa-bot
   sudo -u bot git remote -v
   ```

2. Если используется HTTPS (https://github.com/...), переключите на SSH:
   ```bash
   sudo -u bot git remote set-url origin git@github.com:ВАШ_USERNAME/НАЗВАНИЕ_РЕПОЗИТОРИЯ.git
   ```

3. Настройте SSH ключ для пользователя bot:
   ```bash
   # Переключитесь на пользователя bot
   sudo -u bot bash
   
   # Создайте SSH ключ (если еще нет)
   ssh-keygen -t ed25519 -C "bot@vps" -f ~/.ssh/id_ed25519 -N ""
   
   # Скопируйте публичный ключ
   cat ~/.ssh/id_ed25519.pub
   ```
   
4. Добавьте публичный ключ в GitHub:
   - Зайдите на GitHub → Settings → SSH and GPG keys → New SSH key
   - Вставьте содержимое `~/.ssh/id_ed25519.pub`
   
5. Проверьте подключение:
   ```bash
   ssh -T git@github.com
   ```
   
6. Теперь git pull должен работать без пароля:
   ```bash
   exit  # выйти из сессии bot
   cd /opt/anketa-bot
   sudo -u bot git pull origin main
   ```

#### Вариант 2: Использовать Personal Access Token (если HTTPS)

1. Создайте токен на GitHub:
   - GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate new token (classic)
   - Выберите права: `repo` (полный доступ к репозиториям)
   - Скопируйте токен

2. Настройте git credential helper для пользователя bot:
   ```bash
   sudo -u bot git config --global credential.helper store
   ```

3. При первом `git pull` введите:
   - Username: ваш GitHub username
   - Password: вставьте токен (не пароль!)

4. Или настройте URL с токеном напрямую:
   ```bash
   cd /opt/anketa-bot
   sudo -u bot git remote set-url origin https://ВАШ_ТОКЕН@github.com/ВАШ_USERNAME/НАЗВАНИЕ_РЕПОЗИТОРИЯ.git
   ```

#### Вариант 3: Использовать sudo с опцией -i (временное решение)

Если нужно быстро обновить без настройки:
```bash
sudo -i -u bot bash -c "cd /opt/anketa-bot && git pull origin main"
```

Но это все равно может запросить пароль, если используется HTTPS.

### Полная инструкция по обновлению

```bash
# 1. Подключитесь к VPS
ssh user@your-vps-ip

# 2. Перейдите в директорию бота
cd /opt/anketa-bot

# 3. Сохраните текущие изменения (если есть локальные правки)
sudo -u bot git stash

# 4. Получите последние изменения с GitHub
sudo -u bot git fetch origin
sudo -u bot git pull origin main

# 5. Если были конфликты, разрешите их:
# sudo -u bot git merge origin/main

# 6. Обновите зависимости Python
sudo -u bot bash scripts/post-update.sh

# 7. Перезапустите сервис (если post-update.sh не сделал это автоматически)
sudo systemctl restart telegram-anketa-bot.service

# 8. Проверьте, что сервис запустился
sudo systemctl status telegram-anketa-bot.service

# 9. Просмотрите логи для проверки
journalctl -u telegram-anketa-bot.service -n 50
```

### Настройка sudoers для пользователя bot (решение проблемы с паролем)

Если `post-update.sh` запрашивает пароль, нужно настроить права для пользователя bot:

1. **Создайте файл sudoers для пользователя bot**:
   ```bash
   sudo visudo -f /etc/sudoers.d/bot
   ```

2. **Добавьте следующую строку** (позволяет bot перезапускать только свой сервис без пароля):
   ```
   bot ALL=(ALL) NOPASSWD: /bin/systemctl restart telegram-anketa-bot.service, /bin/systemctl status telegram-anketa-bot.service
   ```

3. **Сохраните и закройте** (в nano: Ctrl+X, затем Y, затем Enter)

4. **Проверьте синтаксис**:
   ```bash
   sudo visudo -c
   ```

5. **Теперь скрипт должен работать без пароля**:
   ```bash
   cd /opt/anketa-bot
   sudo -u bot bash scripts/post-update.sh
   ```

**Альтернативный вариант**: Если не хотите настраивать sudoers, можно запускать обновление в два этапа:
```bash
cd /opt/anketa-bot
sudo -u bot git pull origin main
sudo -u bot bash -c "source venv/bin/activate && pip install --upgrade pip && pip install --upgrade -r requirements.txt && deactivate"
sudo systemctl restart telegram-anketa-bot.service
```

### Если возникли проблемы

1. **Проверьте логи**:
   ```bash
   journalctl -u telegram-anketa-bot.service -f
   ```

2. **Проверьте права доступа**:
   ```bash
   ls -la /opt/anketa-bot
   sudo chown -R bot:bot /opt/anketa-bot
   ```

3. **Проверьте виртуальное окружение**:
   ```bash
   cd /opt/anketa-bot
   sudo -u bot source venv/bin/activate
   pip list
   deactivate
   ```

4. **Переустановите зависимости**:
   ```bash
   cd /opt/anketa-bot
   sudo -u bot bash scripts/setup-venv.sh
   sudo systemctl restart telegram-anketa-bot.service
   ```

## Автоматическое обновление (опционально)

Можно настроить cron для автоматического обновления:

```bash
# Откройте crontab для пользователя bot
sudo crontab -u bot -e

# Добавьте строку для ежедневного обновления в 3:00 ночи
0 3 * * * cd /opt/anketa-bot && git pull origin main && bash scripts/post-update.sh
```

## Откат к предыдущей версии

Если новая версия работает некорректно:

```bash
cd /opt/anketa-bot

# Посмотрите историю коммитов
sudo -u bot git log --oneline -10

# Откатитесь к нужному коммиту (замените COMMIT_HASH)
sudo -u bot git checkout COMMIT_HASH

# Перезапустите сервис
sudo systemctl restart telegram-anketa-bot.service
```

Или создайте новую ветку для тестирования:

```bash
cd /opt/anketa-bot
sudo -u bot git checkout -b testing
sudo -u bot git pull origin main
# Протестируйте изменения
# Если все ок, вернитесь в main:
sudo -u bot git checkout main
sudo -u bot git merge testing
```

