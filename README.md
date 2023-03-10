# PURPOSE

The purpose of CS50's Finance lab is to simulate the buying and selling of stocks in the stock market.
Users can register with a username and password. Once signed up, users are given 10,000$ to buy a stock
at the current market prices. Users can also sell their purchases stocks they bought at the current market prices.
If users want to look at current prices, they can ask for a quote on the quotes navigation link. On the home page, users can see all their purchased stocks and the money they have left. Users also have the option to see their purchase history from the history navigation link.

# CONTENTS

This project consists of two folders, static, and templates.

1. Static contains the styles.css and icon images for the site.

2. Templates contains all the html files for this page. The base html file for every other html file is layout.html which takes advantage of Jinja templating, to reduce repition of code.

The remaining files in this project are:

1. app.py: Handles all the routing for the pages using flask.

2. helpers.py: Contains functions that handle 404 page, formatting, login functions, and a function that makes the api calls to [IEXCloud](https://iexcloud.io/cloud-login#/).

3. finance.db: Sqlite database file, contains all the information for users, and their accounts.

4. requirements.txt: Contains all the python libraries needed to run this project.

# HOW TO RUN

