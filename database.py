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
            'port': os.getenv('DB_PORT'),
            'auth_plugin': 'mysql_native_password'
        }

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            return self.connection
        except Error as e:
            print(f"❌ Ошибка подключения: {e}")
            return None

    def save_user(self, user_id, fio, email, phone, photo_id, photo_url, local_path, size, price):
        try:
            connection = self.connect()
            if connection is None:
                return False

            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO users 
                (user_id, fio, email, phone, photo_id, photo_url, local_path, size, status, price)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Заказ создан', %s)
            ''', (user_id, fio, email, phone, photo_id, photo_url, local_path, size, price))
            connection.commit()
            return True
        except Error as e:
            print(f"❌ Ошибка: {e}")
            return False
        finally:
            if connection and connection.is_connected():
                connection.close()

    def update_order_status(self, user_id, new_status):
        try:
            connection = self.connect()
            if connection is None:
                return False

            cursor = connection.cursor()
            cursor.execute('UPDATE users SET status = %s WHERE user_id = %s',
                           (new_status, user_id))
            connection.commit()
            return True
        except Error as e:
            print(f"❌ Ошибка обновления статуса: {e}")
            return False
        finally:
            if connection and connection.is_connected():
                connection.close()

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def get_order_status(self, user_id):
        try:
            connection = self.connect()
            if connection is None:
                return None

            cursor = connection.cursor()
            cursor.execute('SELECT status FROM users WHERE user_id = %s', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Error as e:
            print(f"❌ Ошибка получения статуса: {e}")
            return None
        finally:
            if connection and connection.is_connected():
                connection.close()

    def get_price(self, size):
        try:
            connection = self.connect()
            if connection is None:
                return None

            cursor = connection.cursor(dictionary=True)
            cursor.execute('SELECT price FROM prices WHERE size = %s', (size,))
            result = cursor.fetchone()
            return result['price'] if result else None
        except Error as e:
            print(f"❌ Ошибка получения цены: {e}")
            return None
        finally:
            if connection and connection.is_connected():
                connection.close()

    def get_prices(self):
        try:
            connection = self.connect()
            if connection is None:
                return []

            cursor = connection.cursor(dictionary=True)
            cursor.execute('SELECT size, price, is_custom FROM prices')
            return cursor.fetchall()
        except Error as e:
            print(f"❌ Ошибка получения списка цен: {e}")
            return []
        finally:
            if connection and connection.is_connected():
                connection.close()

    def update_price(self, size, price, is_custom=False):
        try:
            connection = self.connect()
            if connection is None:
                return False

            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO prices (size, price, is_custom) 
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE price = VALUES(price)
            ''', (size, price, is_custom))
            connection.commit()
            return True
        except Error as e:
            print(f"❌ Ошибка обновления цены: {e}")
            return False
        finally:
            if connection and connection.is_connected():
                connection.close()