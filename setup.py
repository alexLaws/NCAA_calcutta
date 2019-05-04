from model import Bid, Team, User, Auction, User_access, database
import datetime

database.drop_tables([Bid, Team, User, Auction, User_access])
database.create_tables([Bid, Team, User, Auction, User_access])

duke = Team(team="Duke Blue Devils")
duke.save()

Bid.create(participant="Alex",
           team_bid=duke,
           bid_amount=1,
           bid_time_stamp=datetime.datetime.now())

alex = User(username='lawsalex',
            email='tal1286@gmail.com',
            first_name='Alex',
            last_name='Laws')
alex.set_password('admin')
alex.save()

chris = User(username='bubernakChris',
             email='Chris.Bubernak@gmail.com',
             first_name='Chris',
             last_name='Bubernak')
chris.set_password('captain')
chris.save()

kober = Auction(auction_name="Kober6",
                code="crapfest")
kober.save()

seattle = Auction(auction_name="Voodoo",
                  code="do the doo")
seattle.save()

User_access.create(user_in_auction=alex,
                   auction=kober)
User_access.create(user_in_auction=alex,
                   auction=seattle)
User_access.create(user_in_auction=chris,
                   auction=seattle)
