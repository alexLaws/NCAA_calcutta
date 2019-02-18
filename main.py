import os
import datetime

from flask import Flask, render_template, request, redirect, url_for, session

from model import Bid, Team

from peewee import fn

app = Flask(__name__)
# app.secret_key = os.environ.get('SECRET_KEY').encode()

@app.route('/')
def home():
    return render_template('home.jinja2')

@app.route('/auction/', methods=['GET', 'POST'])
def auction():
    team_for_bid = Team.select()
    try:
        high_bid = Bid.select(fn.MAX(Bid.bid_amount)).where(Bid.team_bid == team_for_bid[0]).scalar()
        leader = Bid.select().where((Bid.team_bid == team_for_bid[0]) & (Bid.bid_amount == high_bid)).get()
        bid_leader = leader.participant
    except model.BidDoesNotExist:
        high_bid = 0
        bid_leader = 'Nobody'

    if request.method == 'POST':
        bidder = request.form['name']
        bid_amt = int(request.form['bid'])
        if bid_amt > high_bid:
            Bid.create(participant=bidder,
                       team_bid=team_for_bid[0],
                       bid_amount=bid_amt,
                       bid_time_stamp=datetime.datetime.now())
            return render_template('auction.jinja2',
                                   team=team_for_bid[0].team,
                                   leader=bidder,
                                   high_bid=bid_amt)
        else:
            return render_template('auction.jinja2',
                                   team=team_for_bid[0].team,
                                   leader=bid_leader,
                                   high_bid=high_bid,
                                   error="You've already been outbid. Try again.")
    return render_template('auction.jinja2',
                           team=team_for_bid[0].team,
                           leader=bid_leader,
                           high_bid=high_bid)


@app.route('/view/')
def view():
    all_teams = Team.select()
    print(all_teams)
    all_bids = Bid.select().where(Bid.team_bid == all_teams[0]).order_by(Bid.bid_amount)
    for bid in all_bids:
        print(bid.bid_amount)
    return render_template('view.jinja2', all_teams=all_teams, bids=all_bids)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port)
