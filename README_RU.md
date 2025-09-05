# FastAPI Backend Project

Это бэкенд‑сервис на FastAPI с архитектурным паттерном repository/service. Система реализует аутентификацию пользователей, управление профилем, систему уведомлений и ролевую модель доступа (RBAC) с использованием современных инструментов Python и лучших практик.

## Возможности

- Аутентификация пользователей с помощью JWT токенов
- Система управления профилем
- Система уведомлений с возможностью работы в реальном времени
- Система личных сообщений между пользователями
- Ролевой контроль доступа (клиент, исполнитель, администратор)
- Восстановление пароля с подтверждением по email
- Миграции базы данных с помощью Alembic
- Внедрение зависимостей через Dishka

## Технологический стек

- **Фреймворк**: FastAPI (Python 3.11+)
- **ASGI сервер**: Uvicorn
- **База данных**: SQLite с SQLAlchemy 2.0 (AsyncSession)
- **Миграции**: Alembic
- **Dependency Injection**: Dishka
- **Валидация данных**: Pydantic v2
- **Безопасность**: Passlib (bcrypt/argon2), PyJWT
- **Email**: aiosmtplib
- **Конфигурация**: python-dotenv
- **Тестирование**: pytest, httpx, pytest-asyncio
- **Качество кода**: ruff, black, mypy

## Структура проекта

```
app/
  core/
    config.py          # Конфигурация приложения
    security.py        # Хеширование и проверка паролей
    jwt.py             # Создание и валидация JWT токенов
    email.py           # Отправка email
  db/
    base.py            # Базовые модели БД
    session.py         # Управление сессией БД
  domain/
    users/
      models.py        # Модель пользователя
      schemas.py       # Pydantic‑схемы пользователя
      repository.py    # Слой доступа к данным пользователя
      service.py       # Бизнес‑логика пользователя
      router.py        # API endpoints пользователя
      enums.py         # Enum‑классы для пользователей
      policies.py      # Политики доступа пользователей
    profiles/
      models.py        # Модель профиля
      schemas.py       # Pydantic‑схемы профиля
      repository.py    # Слой доступа к данным профиля
      service.py       # Бизнес‑логика профиля
      router.py        # API endpoints профиля
    auth/
      router.py        # API endpoints аутентификации
      schemas.py       # Pydantic‑схемы аутентификации
      service.py       # Бизнес‑логика аутентификации
      repository.py    # Слой доступа к данным аутентификации
    notifications/
      models.py        # Модель уведомления
      schemas.py       # Pydantic‑схемы уведомлений
      repository.py    # Слой доступа к данным уведомлений
      service.py       # Бизнес‑логика уведомлений
      router.py        # API endpoints уведомлений
      enums.py         # Enum‑классы уведомлений
    messages/
      models.py        # Модель сообщения
      schemas.py       # Pydantic‑схемы сообщений
      repository.py    # Слой доступа к данным сообщений
      service.py       # Бизнес‑логика сообщений
      router.py        # API endpoints сообщений
  di/
    container.py       # Контейнер зависимостей
  api/
    deps.py            # Зависимости API
    router.py          # Главный роутер API
  utils/
    crypto.py          # Криптографические утилиты
    exceptions.py      # Кастомные исключения
  main.py              # Точка входа приложения
alembic/
  env.py               # Конфигурация Alembic
  versions/            # Скрипты миграций
docs/                  # Документация
scripts/               # Скрипты для разработки
tests/
  test_auth.py         # Тесты аутентификации
  test_users.py        # Тесты пользователей
  test_profiles.py     # Тесты профилей
  test_notifications.py # Тесты уведомлений
.env.example           # Пример env‑переменных
README.md              # Документация проекта
```

## Установка

### Быстрый старт

Запустите скрипт инициализации:
```bash
./scripts/init-dev.sh
```

### Ручная установка

1. Создайте виртуальное окружение:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. Установите зависимости:
   ```bash
   make install-dev
   ```
   
   Или напрямую через pip:
   ```bash
   pip install -r requirements.txt
   ```
   
   Для разработки:
   ```bash
   pip install -r requirements-dev.txt
   ```
   
   Или с установкой всех зависимостей в dev‑режиме:
   ```bash
   pip install -e ".[dev]"
   ```

3. Скопируйте и настройте переменные окружения:
   ```bash
   cp .env.example .env
   # Отредактируйте .env по необходимости
   ```

4. Выполните миграции БД:
   ```bash
   alembic upgrade head
   ```

5. Запустите сервер:
   ```bash
   make dev
   ```
   
   Или напрямую:
   ```bash
   uvicorn app.main:app --reload
   ```

## API endpoints

### Аутентификация
- `POST /api/v1/auth/register` – регистрация нового пользователя и создание пустого профиля
- `POST /api/v1/auth/login` – аутентификация и получение JWT токенов
- `POST /api/v1/auth/refresh` – обновление access‑токена через refresh‑токен
- `POST /api/v1/auth/logout` – отзыв текущего refresh‑токена
- `POST /api/v1/auth/logout-all` – отзыв всех refresh‑токенов пользователя
- `POST /api/v1/auth/request-password-reset` – запрос на сброс пароля по email
- `POST /api/v1/auth/confirm-password-reset` – подтверждение сброса пароля по токену

### Пользователи
- `GET /api/v1/users/me` – получить текущего пользователя (без профиля) – авторизованный
- `GET /api/v1/users/{id}` – получить конкретного пользователя – администратор
- `PATCH /api/v1/users/{id}` – обновить пользователя – администратор
- `GET /api/v1/users` – список всех пользователей – администратор

### Профили
- `GET /api/v1/profiles/me` – получить профиль текущего пользователя – авторизованный
- `PATCH /api/v1/profiles/me` – обновить профиль текущего пользователя – авторизованный
- `GET /api/v1/profiles/{user_id}` – получить профиль пользователя – администратор
- `PATCH /api/v1/profiles/{user_id}` – обновить профиль пользователя – администратор

### Уведомления
- `POST /api/v1/notifications/` – отправить уведомление пользователю – авторизованный
- `GET /api/v1/notifications/` – получить уведомления текущего пользователя – авторизованный
- `GET /api/v1/notifications/unread-count` – количество непрочитанных уведомлений – авторизованный
- `GET /api/v1/notifications/{notification_id}` – получить уведомление – авторизованный
- `PATCH /api/v1/notifications/{notification_id}` – обновить уведомление – авторизованный
- `POST /api/v1/notifications/mark-as-read` – отметить несколько уведомлений как прочитанные – авторизованный
- `DELETE /api/v1/notifications/{notification_id}` – удалить уведомление – авторизованный

### Сообщения
- `POST /api/v1/messages/` – отправить сообщение пользователю – авторизованный
- `GET /api/v1/messages/inbox` – входящие сообщения – авторизованный
- `GET /api/v1/messages/sent` – исходящие сообщения – авторизованный
- `GET /api/v1/messages/{message_id}` – получить сообщение – авторизованный
- `PATCH /api/v1/messages/{message_id}` – обновить сообщение (только отправитель) – авторизованный
- `DELETE /api/v1/messages/{message_id}` – удалить сообщение (отправитель или получатель) – авторизованный

## Тестирование

Запуск тестов:
```bash
make test
```

С покрытием:
```bash
make test-cov
```

Или через скрипт:
```bash
./scripts/test-coverage.sh
```

## Качество кода

Проект использует инструменты для поддержания качества кода:

- **Black** – автоформатирование
- **Ruff** – быстрый линтер
- **MyPy** – статическая типизация

Запуск всех проверок:
```bash
make check-quality
```

Или скриптом:
```bash
./scripts/code-quality.sh
```

Форматирование кода:
```bash
make format
```

## CI/CD

Проект включает GitHub Actions для CI/CD:

- **CI Pipeline** (`.github/workflows/ci.yml`): выполняется при push и pull request в `main`
  - Тесты под Python 3.11 и 3.12
  - Проверка форматирования (black)
  - Линтинг (ruff)
  - Проверка типов (mypy)
  - Проверка сборки

- **Deployment Pipeline** (`.github/workflows/deploy.yml`): запускается при релизе
  - Миграции базы данных
  - Деплой приложения
  - Health‑checks

## Docker

Для контейнеризации используется Docker:

- **Dockerfile** – мульти‑стейдж сборка для продакшена
- **docker-compose.yml** – для локальной разработки с PostgreSQL

Запуск:
```bash
docker-compose up --build
```

Тесты в контейнере:
```bash
docker-compose run api pytest
```

Сборка и запуск напрямую:
```bash
docker build -t fastapi-backend .
docker run -p 8000:8000 fastapi-backend
```

## Конфигурация проекта

Проект использует современные стандарты Python‑пакетов:

- **pyproject.toml** – основная конфигурация (PEP 621)
- **setup.py** – обратная совместимость
- **setup.cfg** – настройки flake8, pytest, mypy
- **requirements.txt** – зависимости для продакшена
- **requirements-dev.txt** – зависимости для разработки

## Скрипты разработки

В каталоге `scripts/` доступны:

- **init-dev.sh** – инициализация окружения разработки
- **code-quality.sh** – запуск проверок качества кода
- **test-coverage.sh** – тесты с отчетом покрытия

## Документация

В папке `docs/`:

- **index.md** – основная документация

## Makefile

Проект включает Makefile с командами:

- `make install` – установка продакшен зависимостей
- `make install-dev` – установка зависимостей для разработки
- `make test` – запуск тестов
- `make test-cov` – тесты с покрытием
- `make lint` – линтинг кода
- `make format` – форматирование (black)
- `make check-quality` – все проверки
- `make run` – запуск приложения
- `make dev` – запуск в dev‑режиме
- `make clean` – очистка временных файлов

