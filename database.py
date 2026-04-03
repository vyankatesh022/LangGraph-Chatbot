import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def _get_db_config(include_database=True):
    config={
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER"),
        "password": os.getenv("MYSQL_PASSWORD"),
        "charset": "utf8mb4",
    }
    database=os.getenv("MYSQL_DATABASE")

    if not config["user"] or config["password"] is None or not database:
        raise ValueError("MYSQL_USER, MYSQL_PASSWORD, and MYSQL_DATABASE must be set in the environment.")

    if include_database:
        config["database"]=database
    return config

def get_connection(include_database=True):
    return mysql.connector.connect(**_get_db_config(include_database=include_database))

def init_table():
    database_name=os.getenv("MYSQL_DATABASE")

    server_conn=get_connection(include_database=False)
    server_cursor=server_conn.cursor()
    try:
        server_cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        server_conn.commit()
    finally:
        server_cursor.close()
        server_conn.close()

    conn=get_connection()
    cursor=conn.cursor()
    try:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_titles(
                thread_id VARCHAR(255) PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages(
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                thread_id VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_thread_messages (thread_id, id)
            )
            """
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def save_title(thread_id, title):
    conn=get_connection()
    cursor=conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO chat_titles (thread_id, title)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE title=VALUES(title)
            """,
            (str(thread_id), title),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def load_chat_titles():
    conn=get_connection()
    cursor=conn.cursor()
    try:
        cursor.execute("SELECT thread_id, title FROM chat_titles ORDER BY updated_at ASC")
        return {thread_id: title for thread_id, title in cursor.fetchall()}
    finally:
        cursor.close()
        conn.close()

def save_message(thread_id, role, content):
    conn=get_connection()
    cursor=conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO chat_messages (thread_id, role, content)
            VALUES (%s, %s, %s)
            """,
            (str(thread_id), role, content),
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def load_thread_messages(thread_id):
    conn=get_connection()
    cursor=conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """
            SELECT role, content
            FROM chat_messages
            WHERE thread_id=%s
            ORDER BY id ASC
            """,
            (str(thread_id),),
        )
        return [{"role": row["role"], "content": row["content"]} for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()

def list_thread_ids():
    conn=get_connection()
    cursor=conn.cursor()
    try:
        cursor.execute(
            """
            SELECT DISTINCT thread_id
            FROM chat_messages
            ORDER BY thread_id
            """
        )
        return [thread_id for (thread_id,) in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()