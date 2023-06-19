from sqlalchemy import (create_engine ,Column, Table, Integer, String, DateTime, 
                        ForeignKey, PrimaryKeyConstraint, CheckConstraint)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from datetime import datetime


DB_URL = 'sqlite:///Lesson_11/base.db3'
BASE = declarative_base()


class Storage(object):

    def __init__(self):
        self.db_engine = create_engine(DB_URL, echo=False, pool_recycle=7200)
        BASE.metadata.create_all(self.db_engine)
        Session = sessionmaker(bind=self.db_engine)
        self.session = Session()

    class User(BASE):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        username = Column(String, unique=True)
        last_login = Column(DateTime)

        def __init__(self, username, last_login):
            self.username = username
            self.last_login = last_login

        def __repr__(self):
            return f'User <{self.username}>'

    class LoginHistory(BASE):
        __tablename__ = 'login_history'
        id = Column(Integer, primary_key=True)
        user_id = Column(Integer, ForeignKey('users.id'))
        login_time = Column(DateTime)
        ip = Column(String)
        port = Column(String)

        def __init__(self, user_id, login_time, ip, port):
            self.user_id = user_id
            self.login_time = login_time
            self.ip = ip
            self.port = port

    class Contacts(BASE):
        __tablename__ = 'contacts'
        owner_id = Column(Integer, ForeignKey('users.id'))
        target_id = Column(Integer, ForeignKey('users.id'))

        __table_args__ = (
            PrimaryKeyConstraint('owner_id', 'target_id'),
            CheckConstraint('owner_id != target_id'),
        )

    def get_session(self):
        return self.session

    def create_users(self, name):
        user_request = self.session.query(self.User).filter_by(username=name).one_or_none()
        if user_request is not None:
            print(f'Пользователь с именем {name} уже существует')
            return None
        user = self.User(name, datetime.now())
        self.session.add(user)
        self.session.commit()

    def users_list(self):
        query = self.session.query(self.User)
        return query.all()


if __name__ == '__main__':
    db = Storage()
    db.create_users('Aleksey')
    db.create_users('Ivan')

    print(db.users_list())
