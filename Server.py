import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()


class Database:
    def __init__(self):
        self.host = os.getenv("MYSQL_HOST")
        self.user = os.getenv("MYSQL_USER")
        self.password = os.getenv("MYSQL_PASSWORD")
        self.database = os.getenv("MYSQL_DATABASE")
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return self.connection
        except Error as e:
            print(f"Ошибка подключения к MySQL: {e}")
            return None

    def close(self):
        if self.connection:
            self.connection.close()

    def save_user(self, user_id, fio, email, phone):
        conn = self.connect()
        if conn is None:
            return False

        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (user_id, fio, email, phone)
                VALUES (%s, %s, %s, %s)
            ''', (user_id, fio, email, phone))
            conn.commit()
            return True
        except Error as e:
            print(f"Ошибка сохранения пользователя: {e}")
            return False
        finally:
            cursor.close()
            self.close()
