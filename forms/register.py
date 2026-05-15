from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegisterForm(FlaskForm):
    name = StringField(
        'Имя пользователя / Никнейм', 
        validators=[
            DataRequired(message="Пожалуйста, укажите ваше имя или никнейм"),
            Length(min=2, max=40, message="Имя должно быть от 2 до 40 символов")
        ]
    )
    
    email = StringField(
        'Адрес электронной почты (Email)', 
        validators=[
            DataRequired(message="Email необходим для создания учетной записи"),
            Email(message="Введен неверный формат почты")
        ]
    )
    
    password = PasswordField(
        'Придумайте пароль', 
        validators=[
            DataRequired(message="Пароль обязателен"),
            Length(min=6, message="В целях безопасности пароль должен быть не менее 6 символов")
        ]
    )
    
    password_again = PasswordField(
        'Повторите пароль', 
        validators=[
            DataRequired(message="Пожалуйста, подтвердите ваш пароль"),
            EqualTo('password', message="Введенные пароли должны полностью совпадать")
        ]
    )
    
    about = TextAreaField(
        'О себе / Сфера интересов (необязательно)', 
        validators=[Length(max=500, message="Описание не должно превышать 500 символов")]
    )
    
    submit = SubmitField('Зарегистрироваться')