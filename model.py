from peewee import *
import os

from playhouse.db_url import connect

database = connect(os.environ.get('DATABASE_URL', 'sqlite:///my_database.db'))
database.execute_sql('PRAGMA foreign_keys = ON;')  # needed for sqlite only


class BaseModel(Model):
    class Meta:
        database = database


class Team(BaseModel):
    """
        This class definds Department, which maintains details of a department
        which might employ a person
    """
    team = CharField(max_length=30, unique=True)


class Bid(BaseModel):
    """
        This class definds Department, which maintains details of a department
        which might employ a person
    """
    participant = CharField(max_length=30)
    team_bid = ForeignKeyField(Team)
    bid_amount = IntegerField()
    bid_time_stamp = DateTimeField(primary_key=True)
