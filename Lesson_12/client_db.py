from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime


BASE = declarative_base()


class ClientDatabase(object):

    def __init__(self, name):
        self.db_engine = create_engine(
            f'sqlite:///Lesson_12/client_{name}.db3',
            echo=False,
            pool_recycle=7200,
            connect_args={'check_same_thread': False},
        )
        BASE.metadata.create_all(self.db_engine)
        Session = sessionmaker(bind=self.db_engine)
        self.session = Session()
        self.session.query(self.Contacts).delete()
        self.session.commit()

    class Knowns(BASE):
        __tablename__ = 'knowns'
        id = Column(Integer, primary_key=True)
        username = Column(String)

        def __init__(self, username):
            self.username = username

    class MessageHistory(BASE):
        __tablename__ = 'message_history'
        id = Column(Integer, primary_key=True)
        from_user = Column(String)
        to_user = Column(String)
        message = Column(Text)
        date = Column(DateTime)

        def __init__(self, from_user, to_user, message):
            self.from_user = from_user
            self.to_user = to_user
            self.message = message
            self.date = datetime.now()

    class Contacts(BASE):
        __tablename__ = 'contacts'
        id = Column(Integer, primary_key=True)
        username = Column(String, unique=True)

        def __init__(self, username):
            self.username = username

    def add_contact(self, username):
        if not self.session.query(self.Contacts).filter_by(username=username).count():
            new_contact = self.Contacts(username)
            self.session.add(new_contact)
            self.session.commit()

    def del_contact(self, username):
        self.session.query(self.Contacts).filter_by(username=username).delete()

    def get_contacts(self):
        return [contact[0] for contact in self.session.query(self.Contacts.username).all()]

    def check_contact(self, username):
        if self.session.query(self.Contacts).filter_by(username=username).count():
            return True
        else:
            return False

    def add_knowns(self, users_list):
        self.session.query(self.Knowns).delete()
        for user in users_list:
            user_row = self.Knowns(user)
            self.session.add(user_row)
        self.session.commit()

    def get_knowns(self):
        return [user[0] for user in self.session.query(self.Knowns.username).all()]

    def check_known(self, username):
        if self.session.query(self.Knowns).filter_by(username=username).count():
            return True
        else:
            return False

    def save_message(self, from_user, to_user, message):
        message_row = self.MessageHistory(from_user, to_user, message)
        self.session.add(message_row)
        self.session.commit()

    def get_history(self, from_user=None, to_user=None):
        query = self.session.query(self.MessageHistory)
        if from_user:
            query = query.filter_by(from_user=from_user)
        if to_user:
            query = query.filter_by(to_user=to_user)
        return [(history_row.from_user,
                 history_row.to_user,
                 history_row.message,
                 history_row.date) for history_row in query.all()]


if __name__ == '__main__':
    db = ClientDatabase('tester1')
    
    for i in ['tester1', 'tester2', 'tester3', 'tester4']:
        db.add_contact(i)
    db.add_contact('tester4')
    db.add_knowns(['tester1', 'tester2', 'tester3', 'tester4', 'tester5'])
    db.save_message('tester1', 'tester2', f'Привет')
    db.save_message('tester2', 'tester1', f'Пока')
    print(db.get_contacts())
    print(db.get_knowns())
    print(db.check_known('tester1'))
    print(db.check_known('tester8'))
    print(db.get_history('tester4'))
    print(db.get_history(to_user='tester4'))
    print(db.get_history('tester1'))
    print(db.get_history('tester2'))
    db.del_contact('tester4')
    print(db.get_contacts())
