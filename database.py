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
            'auth_plugin': 'mysql_native_password'
        }

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            print("Данные успешно сохранены в MySQL✅")
            return self.connection
        except Error as e:
            print(f"❌ Ошибка подключения: {e}")
            return None

    def save_user(self, user_id, fio, email, phone, photo_id, photo_url, local_path, size):
        try:
            connection = self.connect()
            if not connection:
                return False

            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO users 
                (user_id, fio, email, phone, photo_id, photo_url, local_path, size)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (user_id, fio, email, phone, photo_id, photo_url, local_path, size))

            connection.commit()
            return True
        except Error as e:
            print(f"❌ Ошибка: {e}")
            return False
        finally:
            if connection:
                connection.close()

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔌 Соединение закрыто")