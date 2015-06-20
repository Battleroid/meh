from peewee import CharField, TextField, ForeignKeyField, Model, DateTimeField
from playhouse.sqlite_ext import FTSModel, SqliteExtDatabase
from datetime import datetime

db = SqliteExtDatabase('data.db')

class Base(Model):
    class Meta:
        database = db

class BaseFTS(FTSModel):
    class Meta:
        database = db

class Board(Base):
    name = CharField(max_length=4, unique=True)
    title = CharField()

class Thread(Base):
    board = ForeignKeyField(Board, related_name='threads')
    no = CharField(unique=True, primary_key=True)
    post = TextField()
    add_date = DateTimeField(default=datetime.now())

class FTSThread(BaseFTS):
    thread = ForeignKeyField(Thread, primary_key=True)
    post = TextField()

if __name__ == '__main__':
    Board.create_table()
    Thread.create_table()
    FTSThread.create_table()
    Board.create(name='g', title='Technology')
