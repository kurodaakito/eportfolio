from wtforms.fields import SubmitField
from markupsafe import Markup
from wtforms.widgets.core import html_params

class ButtonWidget(object):
    """
    フォームのボタンをレンダリングします。
    """
    def __init__(self, input_type='button'):
        self.input_type = input_type

    def __call__(self, field, **kwargs):
        kwargs.setdefault('type', self.input_type)
        params = html_params(name=field.name, **kwargs)
        # Markupを使用してHTMLのエスケープ処理を行う
        return Markup('<button %s>%s</button>' % (params, field.label.text))

class ButtonField(SubmitField):
    """
    Flask-WTFのSubmitFieldでは扱えないHTMLボタンを表現します。
    """
    widget = ButtonWidget()

