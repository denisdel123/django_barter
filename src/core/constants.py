import os
from dotenv import load_dotenv

load_dotenv()

# Секретный ключ проекта
SECRET_KEY = os.getenv("SECRET_KEY")

# Переменные для PostgreSQL
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DEBUG = os.getenv("DEBUG")

# Не обязательное поле
NULLABLE = {
    "blank": True,
    "null": True
}

# Переменные для моделей ads
MAX_LENGTH_ADS = 30
MAX_LENGTH_CATEGORY = 20
MAX_LENGTH_CHOICES = 20



