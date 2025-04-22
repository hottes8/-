import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()


class Database:
    def __init__(self):
        self.connection = None
        self.config = {
            'host': os.getenv('DB_HOST'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME'),
            'auth_plugin': 'mysql_native_password'  # Для MySQL 8+
        }

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            print("✅ Успешное подключение к MySQL!")
            return self.connection
        except Error as e:
            print(f"❌ Ошибка подключения: {e}")
            return None

    def save_user(self, user_id, fio, email, phone):
        try:
            if not self.connection:
                self.connect()

            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO users (user_id, fio, email, phone)
                VALUES (%s, %s, %s, %s)
            ''', (user_id, fio, email, phone))
            self.connection.commit()
            return True
        except Error as e:
            print(f"❌ Ошибка сохранения: {e}")
            return False
        finally:
            if cursor:
                cursor.close()

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔌 Соединение закрыто")
