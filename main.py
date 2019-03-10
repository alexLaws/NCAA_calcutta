import os
import datetime

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pusher import Pusher
import uuid

from model import Bid, Team
import model

from peewee import fn

# create flask app
app = Flask(__name__)
# app.secret_key = os.environ.get('SECRET_KEY').encode()

# create Pusher app
pusher = Pusher(
    app_id='732112',
    key="162355e8decc1f5cd0a7",
    secret="bafc69ad0a7e680e2139",
    cluster="us2",
    ssl=True)


def get_leader():
    team_for_bid = Team.select()
    try:
        high_bid = Bid.select(fn.MAX(Bid.bid_amount)).where(Bid.team_bid == team_for_bid[0]).scalar()
        leader = Bid.select().where((Bid.team_bid == team_for_bid[0]) & (Bid.bid_amount == high_bid)).get()
        bid_leader = leader.participant
    except model.BidDoesNotExist:
        high_bid = 0
        bid_leader = 'Nobody'
    return team_for_bid, high_bid, bid_leader


@app.route('/')
def home():
    return render_template('home.jinja2')

@app.route('/auction/', methods=['GET', 'POST'])
def auction():
    team_for_bid, high_bid, bid_leader = get_leader()
    return render_template('auction.jinja2',
                           team=team_for_bid[0].team,
                           leader=bid_leader,
                           high_bid=high_bid)


# store new bid
@app.route('/bid', methods=['POST'])
def addBid():
    team_for_bid, high_bid, bid_leader = get_leader()
    bidder = request.form['name']
    bid_amt = int(request.form['bid'])
    if bid_amt > high_bid:
        Bid.create(participant=bidder,
                   team_bid=team_for_bid[0],
                   bid_amount=bid_amt,
                   bid_time_stamp=datetime.datetime.now())
        data = {'id': "bid-{}".format(uuid.uuid4().hex),
                'team': team_for_bid[0].team,
                'bidder': bidder,
                'bid_amt': bid_amt,
                'status': 'active',
                'event_name': 'created'
                }
        pusher.trigger("auction", "bid-added", data)
        return jsonify(data)


@app.route('/view/')
def view():
    all_teams = Team.select()
    all_bids = Bid.select().where(Bid.team_bid == all_teams[0]).order_by(Bid.bid_amount)
    return render_template('view.jinja2', all_teams=all_teams, bids=all_bids)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port)
