import datetime
import sqlalchemy
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class Exhibit(SqlAlchemyBase):
    __tablename__ = 'exhibits'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    short_description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    full_description = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    creation_year = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    simulator_type = sqlalchemy.Column(sqlalchemy.String, nullable=False, default="none")
    image_path = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    is_visible = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    views_count = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    feedbacks = orm.relationship("Feedback", back_populates="exhibit", cascade="all, delete-orphan")