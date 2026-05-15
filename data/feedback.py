import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Feedback(SqlAlchemyBase):
    __tablename__ = 'feedbacks'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    rating = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=5)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    exhibit_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("exhibits.id"))

    user = orm.relationship('User')
    exhibit = orm.relationship('Exhibit', back_populates='feedbacks')