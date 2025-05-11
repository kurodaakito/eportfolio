from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class LearningRecord:
    def __init__(self, id=None, title=None, content=None, created_at=None, user_id=None,category=None, teacher_comment=None):
        self.id = id
        self.title = title
        self.content = content
        self.created_at = created_at
        self.user_id = user_id
        self.category = category
        self.teacher_comment = teacher_comment
    def __repr__(self):
        return f"<LearningRecord {self.title}>"

class User(UserMixin):
    def __init__(self):
        self.id = None
        self.username = None
        self.password_hash = None
        self.role = None

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"<User {self.username}>"
class Course:
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

class Thread:
    def __init__(self, id=None, title=None, course_id=None, created_by=None):
        self.id = id
        self.title = title
        self.course_id = course_id
        self.created_by = created_by

class Post:
    def __init__(self, id=None, content=None, thread_id=None, created_at=None):
        self.id = id
        self.content = content
        self.thread_id = thread_id
        self.created_at = created_at

