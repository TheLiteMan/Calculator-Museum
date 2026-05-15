from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = StringField(
        'Электронная почта (Email)', 
        validators=[
            DataRequired(message="Поле email обязательно для заполнения"),
            Email(message="Некорректный формат адреса электронной почты")
        ]
    )
    
    password = PasswordField(
        'Пароль', 
        validators=[
            DataRequired(message="Поле пароля не может быть пустым"),
            Length(min=4, max=32, message="Пароль должен содержать от 4 до 32 символов")
        ]
    )
    
    remember_me = BooleanField('Запомнить меня на этом устройстве')
    
    submit = SubmitField('Войти в систему')