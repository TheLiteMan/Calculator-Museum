from flask_wtf import FlaskForm
from wtforms import TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange


class FeedbackForm(FlaskForm):
    text = TextAreaField('Ваш отзыв / впечатление', validators=[DataRequired()])
    rating = IntegerField('Оценка (1-5)', validators=[
        DataRequired(), NumberRange(min=1, max=5, message="Оценка должна быть от 1 до 5")
    ])
    submit = SubmitField('Оставить отзыв')