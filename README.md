<<<<<<< HEAD
# django_barter
=======
# Django_Barter


## Описание:
Веб-приложение на Django для организации обмена вещами между пользователями.

## Как работать с проектом:
Установка Poetry (если не установлен):
Для brew (macOS)
```
brew install poetry
```

Или официальный скрипт(macOS и Linux):
```
curl -sSL https://install.python-poetry.org | python3 -
```

Перезапускаем терминал и проверяем наличие poetry:
```
poetry --version
```

Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:denisdel123/django_barter.git
```
```
cd djagno_barter
```

Создать и активировать виртуальное окружение:
```
poetry env activate
```

Установить зависимости:
```
poetry install --no-root
```

В корне проекта создать файл .env
```
touch .env
```


и заполнить его по следующему образцу:
```
# Переменные для PostgreSQL
POSTGRES_DB=django_barter
POSTGRES_USER=
POSTGRES_PASSWORD=
DB_PORT=5432

# Режим разработчика
DEBUG=True
```

Выполнить миграции <br>
<sub>Для того, чтобы заработали все миграции, в каждом приложении создана папка `migrations` с файлом `__init__.py` </sub>

```
python manage.py makemigrations
python manage.py migrate
```

Запустите проект:
```
python manage.py runserver
```
>>>>>>> de53676 (Загружаю проект django_barter)
