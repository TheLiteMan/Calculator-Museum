from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange


class ExhibitForm(FlaskForm):
    title = StringField('Название экспоната', validators=[DataRequired()])
    short_description = StringField('Краткое описание', validators=[DataRequired()])
    full_description = TextAreaField('Полное историческое описание', validators=[Optional()])
    creation_year = IntegerField('Год создания/изобретения', validators=[
        Optional(), NumberRange(min=-5000, max=2026, message="Некорректный исторический период")
    ])
    simulator_type = StringField('Тип симулятора (abacus/pascalina/arithmometer/rpn/none)', validators=[DataRequired()])
    image_path = StringField('Путь к изображению', validators=[Optional()])
    is_visible = BooleanField('Отображать в зале витрин')
    submit = SubmitField('Сохранить экспонат')