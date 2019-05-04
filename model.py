from peewee import CharField, ForeignKeyField, IntegerField, DateTimeField, Model
import os

from playhouse.db_url import connect

from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import UserMixin

database = connect(os.environ.get('DATABASE_URL', 'sqlite:///auction.db'))
# database.execute_sql('PRAGMA foreign_keys = ON;')  # needed for sqlite only


class BaseModel(Model):
    class Meta:
        database = database


class Team(BaseModel):
    """
        This class defines a team to bid on
    """
    team = CharField(max_length=30, unique=True)


class Bid(BaseModel):
    """
        This class defines bids that people make on teams
    """
    participant = CharField(max_length=30)
    team_bid = ForeignKeyField(Team)
    bid_amount = IntegerField()
    bid_time_stamp = DateTimeField(primary_key=True)


class User(UserMixin, BaseModel):
    """
        This class defines Users
    """
    username = CharField(max_length=30, unique=True)
    first_name = CharField(max_length=30, unique=True)
    last_name = CharField(max_length=30, unique=True)
    email = CharField(max_length=64, unique=True)
    password_hash = CharField(max_length=128)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Auction(BaseModel):
    """
        This class defines the auction groups
    """
    auction_name = CharField(max_length=30, unique=True)
    code = CharField(max_length=30)


class User_access(BaseModel):
    """
        This class defines the auctions to which users have access
    """
    user_in_auction = ForeignKeyField(User)
    auction = ForeignKeyField(Auction)
