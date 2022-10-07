import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

# https://www.w3schools.com/sql/sql_create_table.asp
# go into database from command line
# and run following command inside the database, thus only creating the table once
# db.execute("CREATE TABLE account_history(id INTEGER PRIMARY KEY, stock TEXT, shares INTEGER, purchase_price NUMERIC)")
# DROP TABLE table_name # in case you mess up and need to try again
# could also have some statement checking if the table already exists, and only creating it once
# CREATE TABLE purchase_history (user_id INTEGER, stock TEXT, shares INTEGER, price NUMERIC, FOREIGN KEY(user_id) REFERENCES users(id));

# delete all rows in an sql table
#DELETE FROM table_name;

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# if post request, give purchase successful alert/banner
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show portfolio of stocks"""
    # List stocks user owns and number of shares owned for each
    # Current price of each stock
    # Value of each holding
    # Display users current cash balance
    # Display users grand total (cash balance + stocks value)


    # when user completes purchase, redirect here
    #if request.method == "POST":

    id = session["user_id"]
    #return apology(str(id))
    list_of_dict_purchases = db.execute("SELECT DISTINCT(stock) FROM purchase_history WHERE user_id == (?)", session["user_id"])

    list_of_tickers = []
    for purchase in list_of_dict_purchases:
        list_of_tickers.append(purchase["stock"])

    overview = []
    # set to none, in case this is user first time loging in
    total_holding = None
    total_holding_sum = 0
    for ticker in list_of_tickers:

        buys_dict = db.execute("SELECT SUM(shares) as amount FROM purchase_history WHERE stock == (?) and user_id == (?) and type == 'buy'", ticker, session["user_id"])
        shares = buys_dict[0]["amount"]
        sells_dict = db.execute("SELECT SUM(shares) as amount FROM purchase_history WHERE stock == (?) and user_id == (?) and type == 'sell'", ticker, session["user_id"])
        sells = sells_dict[0]["amount"]
        # fixes column we added for sells
        if sells is None:
            sells = 0

        shares = shares - sells

        ticker_dict = lookup(ticker)
        price_per_share = ticker_dict["price"]
        full_ticker_name = ticker_dict["name"]
        total_holding = shares * price_per_share
        total_holding_sum += total_holding

        # make ticker appear all uppercase
        ticker = ticker.upper()

        if shares > 0:
            overview.append([ticker, full_ticker_name, shares, usd(price_per_share), usd(total_holding)])


    cash_list_of_dict = db.execute("SELECT cash FROM users WHERE id == (?)", session["user_id"])
    cash = cash_list_of_dict[0]['cash']
    total_value = total_holding_sum + cash

    return render_template("index.html", overview_list_of_list=overview, cash=usd(cash), total=usd(total_value))

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():

    """Buy shares of stock"""

    # got here from clicking on buy nav link
    if request.method == "GET":
        return render_template("buy.html")

    # else we got here from a form
    # request.form for forms using the post method
    ticker = request.form.get("symbol")

    if ticker is None:
        return apology("Sorry you need to enter a ticker symbol!")

    shares_amount = request.form.get("shares")

    if shares_amount is None:
        return apology("Sorry you need to enter an amount to purchase shares!")

    ticker_dict = lookup(ticker)

    if ticker_dict is None:
        return apology("Sorry that ticker symbol does not exist!")

    shares_amount = int(shares_amount)
    if shares_amount < 0:
        return apology("Sorry you can only enter a positive amount of shares to buy!")

    ticker_price = ticker_dict["price"]
    total_price = ticker_price * shares_amount
    # have to get users amount of cash available
    # SELECT cash FROM users WHERE id == primary_key
    # id == user's cookie session, how do we initially create it?
    # how do we logout?
    # Looks like we logout by clearing session

    cash_list_of_dict_entrys = db.execute("SELECT cash FROM users WHERE id == ?", session["user_id"])
    cash_dict_item = cash_list_of_dict_entrys[0] # return with curly brackets, but not a dict, a list??? So access by index
    cash = cash_dict_item["cash"]

    new_balance = cash - total_price
    if new_balance < 0:

        return apology(f"Sorry not enough funds available. Available cash: {cash}\n Amount for shares: {total_price}")

    # Ok now store relevant information to purchase
    # store primary key from regular table and
    id = session["user_id"]
    # https://www.w3schools.com/sql/func_sqlserver_current_timestamp.asp
    timestamp = db.execute("SELECT CURRENT_TIMESTAMP")
    # return list of dictionary values, grab first one, dictionary value is what we passed in
    timestamp = timestamp[0]["CURRENT_TIMESTAMP"]

    ticker = ticker.upper()
    db.execute("INSERT INTO purchase_history (user_id, stock,shares, price, datetime, type) VALUES(?,?,?,?,?,?)",
                id, ticker, shares_amount, total_price, timestamp, "buy")
    db.execute("UPDATE users SET cash = (?) WHERE (?) == id", new_balance, id)

    return redirect('/')


@app.route("/history")
@login_required
def history():

    """Show history of transactions"""
    account_history_list_of_dicts = db.execute("SELECT * FROM purchase_history WHERE user_id == (?)", session["user_id"])

    for x in range(len(account_history_list_of_dicts)):
        account_history_list_of_dicts[x]["price"] = usd(account_history_list_of_dicts[x]["price"])

    return render_template("history.html", history_dicts=account_history_list_of_dicts)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in, I guess this keeps one instance?
        # session only knows the current user logged in? Since cookie is stored on filesystem
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":
        ticker = request.form.get("symbol")
        # return apology(ticker)
        if ticker is None:
            return redirect("quote.html")
        else:
            # this will return a dictionary (json)
            #ticker_info["name"]
            #ticker_info["price"]
            #ticker_info["symbol"]
            ticker_dict_of_info = lookup(ticker)

        if ticker_dict_of_info is None:
            return apology("Sorry ticker symbol not available!")

        #return apology(str(type(ticker_list)))
        # an api call to IDX
        # get information and serve to customer

        # not sure how to change inside jinja template
        # { value | usd } not working inside quoted.html so modify here
        ticker_dict_of_info["price"] = usd(ticker_dict_of_info["price"])
        return render_template("quoted.html", ticker_info=ticker_dict_of_info)

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # get username, since it came from a form
    # it will most likely be post to hide username
    # from url link. Look in templates/login.html

    # have to differentiate, POST is for submitting forms
    # if we dont, then we get stuck at apology pages
    if request.method == "POST":
        # ok there is request.args for get request
        # there is request.form for post request
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if username is None:
            return apology("No username entered!")
        if password is None:
            return apology("No password entered!")
        if password != confirmation:
            return apology("Passwords entered do not match, try again!")

        # db is an SQL object connected to our database
        # .execute will generate an SQL command in our database

        list_of_dicts = db.execute("SELECT username FROM users WHERE username == (?)", username)

        if len(list_of_dicts) > 0:
            return apology("Username already taken!")

        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, generate_password_hash(password))

        # redirect back to homepage once successful
        # would want to likely add a success page, keep them there for 3 seconds
        # then redirect them back to the homepage to login?
        # TODO: Add a success page

        # Query database for username, check its there. Login user
        rows = db.execute("SELECT id FROM users WHERE username = ?", request.form.get("username"))

        # Remember which user has logged in, I guess this keeps one instance?
        # session only knows the current user logged in? Since cookie is stored on filesystem
        # TODO: I had the logic wrong for entries, to delete all rows use following command
        # DELETE FROM users;
        session["user_id"] = rows[0]["id"]
        session["user_id"] = rows[0]["id"]
        return redirect("/")

    # if user clicked on register then we get a get request
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():

    """Sell shares of stock"""

    if request.method == "GET":
        tickers_list_of_dict = db.execute("SELECT DISTINCT(stock) FROM purchase_history WHERE user_id == (?)", session["user_id"])
        tickers_list = []
        for ticker in tickers_list_of_dict:
            tickers_list.append(ticker["stock"])

        return render_template("sell.html", tickers=tickers_list)

    # dont need this, but want to be explicit
    # Else we got a post request, eg. user wants to sell something
    else:

        ticker = request.form.get("symbol")
        shares = int(request.form.get("shares"))
        ticker_lookup_dict = lookup(ticker)
        share_price = ticker_lookup_dict["price"]

        # be explicit about this, don't necessarily want to use LIKE for stocks
        # entries in database are uppercase, be consistent throughout application
        ticker = ticker.upper()
        buys_dict = db.execute("SELECT stock, shares as buys FROM purchase_history WHERE user_id == (?) and stock == (?) and type == (?)", session["user_id"], ticker, "buy")
        buys = buys_dict[0]["buys"]

        sells_dict = db.execute("SELECT SUM(shares) as sells FROM purchase_history WHERE user_id == (?) and stock == (?) and type ==(?)", session["user_id"], ticker, "sell")
        sells = sells_dict[0]["sells"]

        if buys is None:
            buys = 0
        if sells is None:
            sells = 0

        total_shares = buys - sells

        # subtract shares user wants to sell
        total_shares -= shares

        if total_shares <= -1:
            return apology(f"Sorry you don't have enough shares: {total_shares}")

        timestamp = db.execute("SELECT CURRENT_TIMESTAMP")
        # return list of dictionary values, grab first one, dictionary value is what we passed in
        timestamp = timestamp[0]["CURRENT_TIMESTAMP"]

        total_price = shares * share_price

        db.execute("INSERT INTO purchase_history (user_id, stock,shares, price, datetime, type) VALUES(?,?,?,?,?,?)",
                    session["user_id"], ticker, shares, total_price, timestamp, "sell")

        cash_dict = db.execute("SELECT cash FROM users WHERE id == (?)", session["user_id"])
        cash = cash_dict[0]["cash"]

        new_balance = cash + (shares * share_price)
        db.execute("UPDATE users SET cash = (?) WHERE (?) == id", new_balance, session["user_id"])

        return redirect("/")



