from model import Bid, Team, User, Auction, User_access, Auction_result, database
import datetime

database.drop_tables([Bid, Team, User, Auction, User_access, Auction_result])
database.create_tables([Bid, Team, User, Auction, User_access, Auction_result])

duke = Team(team="Duke Blue Devils")
duke.save()

georgetown = Team(team="Georgetown Hoyas")
georgetown.save()

gonzaga = Team(team="Gonzaga Bulldogs")
gonzaga.save()

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

keith = User(username='porcaroKeith',
             email='bluelightspecial@gmail.com',
             first_name='Keith',
             last_name='Porcaro')
keith.set_password('boston')
keith.save()

kober = Auction(auction_name="Kober6",
                code="crapfest",
                current_team=duke)
kober.save()

seattle = Auction(auction_name="Voodoo",
                  code="do the doo",
                  current_team=duke)
seattle.save()

boston = Auction(auction_name="WorstCoast",
                 code="Least",
                 current_team=duke)
boston.save()

User_access.create(user_in_auction=alex,
                   auction=kober)
User_access.create(user_in_auction=alex,
                   auction=seattle)
User_access.create(user_in_auction=alex,
                   auction=boston)
User_access.create(user_in_auction=chris,
                   auction=seattle)
User_access.create(user_in_auction=keith,
                   auction=kober)
User_access.create(user_in_auction=keith,
                   auction=boston)

Bid.create(participant="Alex",
           team_bid=duke,
           bid_amount=1,
           bid_time_stamp=datetime.datetime.now(),
           auction=kober)

Bid.create(participant="chris",
           team_bid=duke,
           bid_amount=2,
           bid_time_stamp=datetime.datetime.now(),
           auction=seattle)

Bid.create(participant="keith",
           team_bid=duke,
           bid_amount=3,
           bid_time_stamp=datetime.datetime.now(),
           auction=boston)

Auction_result.create(auction=kober,
                      team=gonzaga,
                      buyer=alex,
                      price=10)

Auction_result.create(auction=seattle,
                      team=gonzaga,
                      buyer=chris,
                      price=15)

Auction_result.create(auction=boston,
                      team=gonzaga,
                      buyer=keith,
                      price=13)
