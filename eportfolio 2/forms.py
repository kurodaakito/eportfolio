from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from widgets import ButtonField
from dataaccess import get_user_by_username
from wtforms import SelectField
class LearningRecordForm(FlaskForm):
    title = StringField(
        "タイトル",
        validators=[
            DataRequired(message="タイトルは必須です。"),
            Length(max=128, message="タイトルは128文字以内で入力してください。"),
        ],
    )
    content = TextAreaField(
        "内容",
        validators=[
            DataRequired(message="内容は必須です。"),
        ],
    )
    category = SelectField(
        "カテゴリ",
        choices=[('通常学習', '通常学習'), ('未来創造PJ', '未来創造PJ'), ('インターンシップ', 'インターンシップ')],
        validators=[
            DataRequired(message="カテゴリは必須です。"),
        ],
    )
    cancel = ButtonField("キャンセル")  # ButtonFieldを使用
    submit = SubmitField("登録")

class LoginForm(FlaskForm):
    username = StringField(
        "ユーザー名",
        validators=[
            DataRequired(message="ユーザー名は必須です。"),
            Length(max=64, message="ユーザー名は64文字以内で入力してください。"),
        ],
    )
    password = PasswordField(
        "パスワード",
        validators=[
            DataRequired(message="パスワードは必須です。"),
        ],
    )
    cancel = ButtonField("キャンセル")  # ButtonFieldを使用
    submit = SubmitField("ログイン")

class RegistrationForm(FlaskForm):
    username = StringField(
        "ユーザー名",
        validators=[
            DataRequired(message="ユーザー名は必須です。"),
            Length(min=4, max=64, message="ユーザー名は4~64文字で入力してください。"),
        ],
    )
    password = PasswordField(
        "パスワード",
        validators=[
            DataRequired(message="パスワードは必須です。"),
            Length(min=4, message="パスワードは4文字以上で入力してください。"),
        ],
    )
    password2 = PasswordField(
        "パスワード（確認）",
        validators=[
            DataRequired(message="パスワード（確認）は必須です。"),
            EqualTo('password', message="パスワードが一致しません。"),
        ],
    )
    role = SelectField(
        "役割",
        choices=[('student', '学生'), ('teacher', '教員')],
        validators=[
            DataRequired(message="役割を選択してください。"),
        ],
    )
    cancel = ButtonField("キャンセル")  # ButtonFieldを使用
    submit = SubmitField("登録")
class CommentForm(FlaskForm):
    teacher_comment = TextAreaField(
        "コメント",
        validators=[
            DataRequired(message="コメントは必須です。"),
        ],
    )
    submit = SubmitField("コメントを追加")
    # ユーザー名の重複チェック
    def validate_username(self, username):
        user = get_user_by_username(username.data)
        if user:
            raise ValidationError("このユーザー名は既に使用されています。")
class ThreadForm(FlaskForm):
    title = StringField(
        "スレッドタイトル",
        validators=[DataRequired(), Length(max=128)]
    )
    course_id = SelectField(
        "コース",
        choices=[],  # コースの選択肢を後で設定
        coerce=int,
        validators=[DataRequired()]
    )
    submit = SubmitField("作成")
class PostForm(FlaskForm):
    content = TextAreaField(
        "内容",
        validators=[DataRequired()]
    )
    submit = SubmitField("投稿")
