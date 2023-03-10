# Quick Demo

![](readmeFiles/cs50finance.gif)

# Purpose

The purpose of CS50's Finance lab is to simulate the buying and selling of stocks in the stock market.
Users can register with a username and password. Once signed up, users are given 10,000$ to buy a stock
at the current market prices. Users can also sell their purchased stocks they bought at the current market prices.
If users want to look at current prices, they can ask for a quote on the quotes navigation link. On the home page, users can see all their purchased stocks and the money they have left. Users also have the option to see their purchase history from the history navigation link.

# Contents

This project consists of two folders, static, and templates.

1. Static contains the styles.css and icon images for the site.

2. Templates contains all the html files for this page. The base html file for every other html file is layout.html which takes advantage of Jinja templating, to reduce repition of code.

The remaining files in this project are:

1. app.py: Handles all the routing for the pages using flask.

2. helpers.py: Contains functions that handle 404 page, formatting, login, and api calls to [IEXCloud](https://iexcloud.io/cloud-login#/).

3. finance.db: Sqlite database file, contains all the information for users accounts.

4. requirements.txt: Contains all the python libraries needed to run this project.

# How to run

1. Clone the project 

```
git clone https://github.com/mark8769/CS50-Finance-PSET9
```

2. Create a python virtual environment inside the project. (1st: Mac, 2nd: Windows)

[Python virtual environments](https://docs.python.org/3/tutorial/venv.html)

```
python3 -m venv environment_name
```

```
python -m venv ./venv
```

2. Activate the virtual environment. (1st: Mac, 2nd: Windows)

```
source venv/bin/activate
```

```
.\venv\Scripts\activate
```

3. Install the required libraries.

```
pip3 install -r requirements.txt
```

4. Create an account here https://iexcloud.io/cloud-login#/ This is to get the api key required to run the project. (Free 30 days)

5. In terminal in the project directory run:

```
export API_KEY=your_free_api_key_here
```

6. Start the application inside the project directory.

```
flask run
```

7. Project is hosted locally, flask will give you the address to use. Command + Clicking link is much easier than copying and pasting the url into your browser.
