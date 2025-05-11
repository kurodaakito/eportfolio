import sqlite3
from models import User
from werkzeug.security import generate_password_hash, check_password_hash

def get_connection(autocommit=True):
    if autocommit:
        return sqlite3.connect("eportfolio.db")
    else:
        con = sqlite3.connect("eportfolio.db")
        con.isolation_level = None
        return con

def create_db():
    query1 = """
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """
    query2 = """
    CREATE TABLE IF NOT EXISTS learning_record (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        category TEXT NOT NULL, 
        teacher_comment TEXT, 
        user_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES user(id)
    )
    """
    query3 = """
    CREATE TABLE IF NOT EXISTS course (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
    """
    query4 = """
    CREATE TABLE IF NOT EXISTS thread (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        course_id INTEGER NOT NULL,
        created_by INTEGER NOT NULL,
        FOREIGN KEY(course_id) REFERENCES course(id),
        FOREIGN KEY(created_by) REFERENCES user(id)
    )
    """
    query5 = """
    CREATE TABLE IF NOT EXISTS post (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        thread_id INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(thread_id) REFERENCES thread(id)
    )
    """
    con = get_connection(autocommit=False)
    try:
        cur = con.cursor()
        cur.execute(query1)
        cur.execute(query2)
        cur.execute(query3)
        cur.execute(query4)
        cur.execute(query5)
        cur.execute("SELECT COUNT(*) FROM course")
        count = cur.fetchone()[0]
        if count == 0:
            courses = [('統計学'), ('機械学習'), ('姿勢推定'),('物体検知')]
            cur.executemany("INSERT INTO course (name) VALUES (?)", [(name,) for name in courses])

        con.commit()
    except Exception as e:
        print(e)
        con.rollback()
    finally:
        con.close()

def auth(username, password):
    query = """
    SELECT * FROM user WHERE username = ?
    """
    con = get_connection()
    try:
        con.row_factory = sqlite3.Row  # 辞書形式で結果を取得
        cur = con.cursor()
        cur.execute(query, (username,))
        res = cur.fetchone()
        if res:
            user = User()
            user.id = res["id"]
            user.username = res["username"]
            user.password_hash = res["password_hash"]
            if user.check_password(password):
                return user
        return None
    except Exception as e:
        print(e)
        return None
    finally:
        con.close()

def get_all_records(user_id):
    query = """
    SELECT * FROM learning_record WHERE user_id = ? ORDER BY created_at DESC
    """
    con = get_connection()
    try:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(query, (user_id,))
        records = cur.fetchall()
        return records
    except Exception as e:
        print(e)
        return []
    finally:
        con.close()

def add_record(title, content, user_id, category):
    query = """
    INSERT INTO learning_record (title, content, user_id, category,created_at) VALUES (?, ?, ?, ?,datetime('now'))
    """
    con = get_connection()
    try:
        cur = con.cursor()
        cur.execute(query, (title, content, user_id,category))
        con.commit()
    except Exception as e:
        print(e)
        con.rollback()
    finally:
        con.close()

def get_user_by_username(username):
    query = """
    SELECT * FROM user WHERE username = ?
    """
    con = get_connection()
    try:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(query, (username,))
        res = cur.fetchone()
        if res:
            user = User()
            user.id = res["id"]
            user.username = res["username"]
            user.password_hash = res["password_hash"]
            return user
        return None
    except Exception as e:
        print(e)
        return None
    finally:
        con.close()
def get_all_records_for_teacher():
    query = """
    SELECT lr.*, u.username FROM learning_record lr
    JOIN user u ON lr.user_id = u.id
    ORDER BY lr.created_at DESC
    """
    con = get_connection()
    try:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(query)
        records = cur.fetchall()
        return records
    except Exception as e:
        print(e)
        return []
    finally:
        con.close()
def get_record_by_id(record_id):
    query = """
    SELECT lr.*, u.username FROM learning_record lr
    JOIN user u ON lr.user_id = u.id
    WHERE lr.id = ?
    """
    con = get_connection()
    try:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(query, (record_id,))
        record = cur.fetchone()
        return record
    except Exception as e:
        print(e)
        return None
    finally:
        con.close()
def add_teacher_comment(record_id, comment):
    query = """
    UPDATE learning_record SET teacher_comment = ? WHERE id = ?
    """
    con = get_connection()
    try:
        cur = con.cursor()
        cur.execute(query, (comment, record_id))
        con.commit()
    except Exception as e:
        print(e)
        con.rollback()
    finally:
        con.close()
def get_all_courses():
    query = "SELECT * FROM course"
    con = get_connection()
    try:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(query)
        courses = cur.fetchall()
        return courses
    except Exception as e:
        print(e)
        return []
    finally:
        con.close()
def add_thread(title, course_id, created_by):
    query = """
    INSERT INTO thread (title, course_id, created_by) VALUES (?, ?, ?)
    """
    con = get_connection()
    try:
        cur = con.cursor()
        cur.execute(query, (title, course_id, created_by))
        con.commit()
    except Exception as e:
        print(e)
        con.rollback()
    finally:
        con.close()
def get_all_threads():
    query = """
    SELECT t.*, c.name as course_name FROM thread t
    JOIN course c ON t.course_id = c.id
    ORDER BY t.id DESC
    """
    con = get_connection()
    try:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(query)
        threads = cur.fetchall()
        return threads
    except Exception as e:
        print(e)
        return []
    finally:
        con.close()
def get_thread_by_id(thread_id):
    query = """
    SELECT t.*, c.name as course_name FROM thread t
    JOIN course c ON t.course_id = c.id
    WHERE t.id = ?
    """
    con = get_connection()
    try:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(query, (thread_id,))
        thread = cur.fetchone()
        return thread
    except Exception as e:
        print(e)
        return None
    finally:
        con.close()
def get_posts_by_thread_id(thread_id):
    query = """
    SELECT * FROM post WHERE thread_id = ? ORDER BY created_at ASC
    """
    con = get_connection()
    try:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(query, (thread_id,))
        posts = cur.fetchall()
        return posts
    except Exception as e:
        print(e)
        return []
    finally:
        con.close()
def add_post(content, thread_id):
    query = """
    INSERT INTO post (content, thread_id, created_at) VALUES (?, ?, datetime('now'))
    """
    con = get_connection()
    try:
        cur = con.cursor()
        cur.execute(query, (content, thread_id))
        con.commit()
    except Exception as e:
        print(e)
        con.rollback()
    finally:
        con.close()

