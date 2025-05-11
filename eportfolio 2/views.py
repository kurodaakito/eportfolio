from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
from markupsafe import Markup
from flask_login import (
    LoginManager, login_user, login_required,
    logout_user, current_user, UserMixin
)
from models import User
from forms import LearningRecordForm, LoginForm, RegistrationForm,CommentForm,ThreadForm,PostForm
from dataaccess import (
    get_all_records,
    add_record,
    get_user_by_username,
    auth,
    create_db,
    get_record_by_id,
    add_teacher_comment,
    get_all_records_for_teacher,
    get_all_courses,
    add_thread,
    get_all_threads,
    get_thread_by_id,
    get_posts_by_thread_id,
    add_post
)
import sqlite3

app = Flask(__name__)
app.config["SECRET_KEY"] = "your-secret-key"  # 安全なランダムなキーに変更してください

Bootstrap(app)
CSRFProtect(app)

# ログイン管理の設定
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ユーザーをロードするためのコールバック
@login_manager.user_loader
def load_user(user_id):
    user = get_user_by_id(user_id)
    return user

# ユーザーIDからユーザーを取得するヘルパー関数
def get_user_by_id(user_id):
    query = """
    SELECT * FROM user WHERE id = ?
    """
    from dataaccess import get_connection
    con = get_connection()
    try:
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(query, (user_id,))
        res = cur.fetchone()
        if res:
            user = User()
            user.id = res["id"]
            user.username = res["username"]
            user.password_hash = res["password_hash"]
            user.role = res["role"] 
            return user
        return None
    except Exception as e:
        print(e)
        return None
    finally:
        con.close()

# ホームページ（学習履歴一覧）
@app.route("/")
@login_required  # ログインが必要
def index():
    if current_user.role == 'student':
        # 学生は自分の学習記録を閲覧
        records_data = get_all_records(current_user.id)
    elif current_user.role == 'teacher':
        # 教員は全学生の学習記録を閲覧
        records_data = get_all_records_for_teacher()
    else:
        records_data = []
    # レコードデータを辞書のリストに変換
    records = []
    for row in records_data:
        record = {
            'id':row['id'],
            'title': row['title'],
            'content': row['content'],
            'created_at': row['created_at'],
            'category': row['category'], 
            'teacher_comment': row['teacher_comment']
        }
        if current_user.role == 'teacher':
            record['username'] = row['username']
        records.append(record)
    return render_template("index.html", records=records)

# 学習履歴の新規登録
@app.route("/new", methods=["GET", "POST"])
@login_required  # ログインが必要
def new_record():
    if current_user.role != 'student':
        flash("学習記録は学生のみが登録できます。")
        return redirect(url_for('index'))

    form = LearningRecordForm()
    if form.validate_on_submit():
        add_record(form.title.data, form.content.data, current_user.id, form.category.data)
        return redirect(url_for("index"))
    return render_template("additem.html", form=form)
# ログイン機能
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = auth(form.username.data, form.password.data)
        if user:
            login_user(user)
            flash("ログインに成功しました。")
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash("ユーザー名またはパスワードが間違っています。")
    return render_template("login.html", form=form)

# ログアウト機能
@app.route("/logout")
@login_required  # ログインが必要
def logout():
    logout_user()
    flash("ログアウトしました。")
    return redirect(url_for('login'))

# ユーザー登録機能
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User()
        user.username = form.username.data
        user.set_password(form.password.data)
        user.role = form.role.data 
        # データベースにユーザーを追加
        from dataaccess import get_connection
        con = get_connection()
        try:
            cur = con.cursor()
            query = "INSERT INTO user (username, password_hash, role) VALUES (?, ?, ?)"
            cur.execute(query, (user.username, user.password_hash, user.role))
            con.commit()
            flash("ユーザー登録が完了しました。ログインしてください。")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("このユーザー名は既に使用されています。")
            return render_template("register.html", form=form)
        except Exception as e:
            print(e)
            flash("エラーが発生しました。")
            return render_template("register.html", form=form)
        finally:
            con.close()
    return render_template("register.html", form=form)
@app.route("/comment/<int:record_id>", methods=["GET", "POST"])
@login_required
def add_comment(record_id):
    if current_user.role != 'teacher':
        flash("コメントは教員のみが追加できます。")
        return redirect(url_for('index'))

    form = CommentForm()
    if form.validate_on_submit():
        add_teacher_comment(record_id, form.teacher_comment.data)
        flash("コメントを追加しました。")
        return redirect(url_for('index'))

    # 対象の学習記録を取得
    record = get_record_by_id(record_id)
    return render_template("add_comment.html", form=form, record=record)
@app.route("/threads/new", methods=["GET", "POST"])
@login_required
def create_thread():
    if current_user.role != 'teacher':
        flash("スレッドの作成は教員のみが可能です。")
        return redirect(url_for('thread_list'))

    form = ThreadForm()
    # コースの選択肢を設定
    courses = get_all_courses()
    form.course_id.choices = [(course['id'], course['name']) for course in courses]

    if form.validate_on_submit():
        add_thread(form.title.data, form.course_id.data, current_user.id)
        flash("スレッドを作成しました。")
        return redirect(url_for('thread_list'))
    return render_template("create_thread.html", form=form)
@app.route("/threads")
@login_required
def thread_list():
    threads_data = get_all_threads()
    threads = []
    for row in threads_data:
        thread = {
            'id': row['id'],
            'title': row['title'],
            'course_name': row['course_name']
        }
        threads.append(thread)
    return render_template("thread_list.html", threads=threads)
@app.route("/threads/<int:thread_id>", methods=["GET", "POST"])
@login_required
def thread_detail(thread_id):
    thread = get_thread_by_id(thread_id)
    if not thread:
        flash("スレッドが見つかりません。")
        return redirect(url_for('thread_list'))

    posts_data = get_posts_by_thread_id(thread_id)
    posts = []
    for row in posts_data:
        post = {
            'content': row['content'],
            'created_at': row['created_at']
        }
        posts.append(post)

    form = PostForm()
    if form.validate_on_submit():
        add_post(form.content.data, thread_id)
        flash("投稿しました。")
        return redirect(url_for('thread_detail', thread_id=thread_id))
    return render_template("thread_detail.html", thread=thread, posts=posts, form=form)
@app.template_filter('nl2br')
def nl2br(value):
    return Markup(value.replace('\n', '\n'))
if __name__ == "__main__":
    create_db()
    app.run(host="0.0.0.0", port=5100, debug=True)
