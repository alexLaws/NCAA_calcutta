import os
import datetime

from flask import Flask, render_template, request, redirect, flash, url_for, session, jsonify
from pusher import Pusher
import uuid

from model import Bid, Team, User, Auction, User_access
import model

from peewee import fn

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo

from flask_login import LoginManager, current_user, login_user, logout_user, login_required

from werkzeug.urls import url_parse
from werkzeug.exceptions import abort

# create flask app
app = Flask(__name__)
# app.secret_key = os.environ.get('SECRET_KEY').encode()

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

sign_in = LoginManager(app)
sign_in.login_view = 'login'

# create Pusher app
pusher = Pusher(
    app_id='732112',
    key="162355e8decc1f5cd0a7",
    secret="bafc69ad0a7e680e2139",
    cluster="us2",
    ssl=True)


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first = StringField('First Name', validators=[DataRequired()])
    last = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user_count = User.select(fn.Count(User.username)).where(User.username == username.data).scalar()
        if user_count == 1:
            raise ValidationError('There is already a user with that username.')

    def validate_email(self, email):
        user_count = User.select(fn.Count(User.email)).where(User.email == email.data).scalar()
        if user_count == 1:
            raise ValidationError('There is already a user with that email.')


def get_object_or_404(model, *criterion):
    output = model.select().where(*criterion).get()
    if output is None:
        abort(404)
    else:
        return output


def get_leader(auction):
    team_for_bid = Team.select()
    try:
        high_bid = Bid.select(fn.MAX(Bid.bid_amount)).where((Bid.team_bid == team_for_bid[0]) &
                                                            (Bid.auction == auction)).scalar()
        leader = Bid.select().where((Bid.team_bid == team_for_bid[0]) &
                                    (Bid.bid_amount == high_bid) &
                                    (Bid.auction == auction)).get()
        bid_leader = leader.participant
    except model.BidDoesNotExist:
        high_bid = 0
        bid_leader = 'Nobody'
    return team_for_bid, high_bid, bid_leader


@app.route('/')
def home():
    return render_template('home.jinja2')


@sign_in.user_loader
def load_user(id):
    return User.select().where(User.id == id).get()


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.select().where(User.username == form.username.data).get()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    return render_template('login.jinja2', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    first_name=form.first.data,
                    last_name=form.last.data)
        user.set_password(form.password.data)
        user.save()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.jinja2', title='Register', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


# store new bid
@app.route('/bid', methods=['POST'])
@login_required
def addBid():
    bidder = request.form['name']
    bid_amt = int(request.form['bid'])
    auction_name = request.form['auction']
    auction = Auction.select().where(Auction.auction_name == auction_name).get()
    team_for_bid, high_bid, bid_leader = get_leader(auction)
    if bid_amt > high_bid:
        Bid.create(participant=bidder,
                   team_bid=team_for_bid[0],
                   bid_amount=bid_amt,
                   bid_time_stamp=datetime.datetime.now(),
                   auction=auction)
        data = {'id': "bid-{}".format(uuid.uuid4().hex),
                'team': team_for_bid[0].team,
                'bidder': bidder,
                'bid_amt': bid_amt,
                'status': 'active',
                'event_name': 'created'
                }
        pusher.trigger("auction", "bid-added", data)
        return jsonify(data)
    else:
        message = bidder + ' - FAILED BID'
        data = {'id': "bid-{}".format(uuid.uuid4().hex),
                'team': team_for_bid[0].team,
                'bidder': message,
                'bid_amt': bid_amt,
                'status': 'active',
                'event_name': 'created'
                }
        pusher.trigger("auction", "bid-added", data)
        return jsonify(data)


@app.route('/view/')
@login_required
def view():
    all_teams = Team.select()
    all_bids = Bid.select().where(Bid.team_bid == all_teams[0]).order_by(Bid.bid_amount)
    return render_template('view.jinja2', all_teams=all_teams, bids=all_bids)


@app.route('/user/<username>')
@login_required
def user(username):
    user = get_object_or_404(User, User.username == username)
    auctions = User_access.select().where(User_access.user_in_auction == user)
    return render_template('user.jinja2', user=user, auctions=auctions)


@app.route('/auction/<auction_name>', methods=['GET', 'POST'])
@login_required
def auction(auction_name):
    auction = Auction.select().where(Auction.auction_name == auction_name).get()
    team_for_bid, high_bid, bid_leader = get_leader(auction)
    return render_template('auction.jinja2',
                           team=team_for_bid[0].team,
                           leader=bid_leader,
                           high_bid=high_bid,
                           auction=auction)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port)
