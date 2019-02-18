from model import Bid, Team, database
import datetime

database.drop_tables([Bid, Team])
database.create_tables([Bid, Team])

duke = Team(team="Duke Blue Devils")
duke.save()

Bid.create(participant="Alex",
           team_bid=duke,
           bid_amount=1,
           bid_time_stamp=datetime.datetime.now())
