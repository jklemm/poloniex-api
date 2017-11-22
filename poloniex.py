import json
import time
import hmac
import hashlib
import requests


def create_time_stamp(datestr, date_format="%Y-%m-%d %H:%M:%S"):
    return time.mktime(time.strptime(datestr, date_format))


class Poloniex:
    def __init__(self, apikey, secret):
        self.apikey = apikey
        self.secret = secret

    def post_process(self, before):
        after = before
        # Add timestamps if there isnt one but is a datetime
        if 'return' in after:
            if isinstance(after['return'], list):
                for x in range(0, len(after['return'])):
                    if isinstance(after['return'][x], dict):
                        if 'datetime' in after['return'][x] and 'timestamp' not in after['return'][x]:
                            after['return'][x]['timestamp'] = float(create_time_stamp(after['return'][x]['datetime']))
        return after

    def api_query(self, command, req=None):

        if req is None:
            req = {}

        if command == 'returnTicker' or command == 'return24Volume':
            response = requests.get('https://poloniex.com/public?command=' + command)
            return json.loads(response.content)
        elif command == 'returnOrderBook':
            response = requests.get('https://poloniex.com/public?command=' + command + '&currencyPair=' + str(req['currencyPair']))
            return json.loads(response.content)
        elif command == 'returnMarketTradeHistory':
            response = requests.get('https://poloniex.com/public?command=' + "returnTradeHistory" + '&currencyPair=' + str(req['currencyPair']))
            return json.loads(response.content)
        else:
            post_data = '{}={}&{}={}'.format('command', command, 'nonce', int(time.time()*1000))

            sign = hmac.new(self.secret, post_data, hashlib.sha512).hexdigest()
            headers = {
                'Sign': sign,
                'Key': self.apikey
            }

            response = requests.get('https://poloniex.com/tradingApi', post_data, **headers)
            return self.post_process(json.loads(response.content))

    def return_ticker(self):
        return self.api_query('returnTicker')

    def return_24_volume(self):
        return self.api_query('return24Volume')

    def return_order_book(self, currency_pair):
        return self.api_query('returnOrderBook', {'currencyPair': currency_pair})

    def return_market_trade_history(self, currency_pair):
        return self.api_query('returnMarketTradeHistory', {'currencyPair': currency_pair})

    def return_balances(self):
        """
        Returns all of your balances.
        Outputs: {"BTC":"0.59098578","LTC":"3.31117268", ... }
        """
        return self.api_query('returnBalances')

    def return_open_orders(self, currency_pair):
        """
        Returns your open orders for a given market, specified by the "currencyPair" POST parameter, e.g. "BTC_XCP"
        Inputs: currencyPair  The currency pair e.g. "BTC_XCP"
        Outputs:
            orderNumber   The order number
            type          sell or buy
            rate          Price the order is selling or buying at
            Amount        Quantity of order
            total         Total value of order (price * quantity)
        """
        return self.api_query('returnOpenOrders', {"currencyPair": currency_pair})

    def return_trade_history(self, currency_pair):
        """
        Returns your trade history for a given market, specified by the "currencyPair" POST parameter
        Inputs: currencyPair  The currency pair e.g. "BTC_XCP"
        Outputs:
            date          Date in the form: "2014-02-19 03:44:59"
            rate          Price the order is selling or buying at
            amount        Quantity of order
            total         Total value of order (price * quantity)
            type          sell or buy
        """
        return self.api_query('returnTradeHistory', {"currencyPair": currency_pair})

    def buy(self, currency_pair, rate, amount):
        """
        Places a buy order in a given market. Required POST parameters are "currencyPair", "rate", and "amount".
        If successful, the method will return the order number.
        Inputs:
            currencyPair  The curreny pair
            rate          price the order is buying at
            amount        Amount of coins to buy
        Outputs:
            orderNumber   The order number
        """
        return self.api_query('buy', {"currencyPair": currency_pair, "rate": rate, "amount": amount})

    def sell(self, currency_pair, rate, amount):
        """
        Places a sell order in a given market. Required POST parameters are "currencyPair", "rate", and "amount".
        If successful, the method will return the order number.
        Inputs:
            currencyPair  The curreny pair
            rate          price the order is selling at
            amount        Amount of coins to sell
        Outputs:
            orderNumber   The order number
        """
        return self.api_query('sell', {"currencyPair": currency_pair, "rate": rate, "amount": amount})

    def cancel(self, currency_pair, order_number):
        """
        Cancels an order you have placed in a given market. Required POST parameters are "currencyPair" and "orderNumber".
        Inputs:
            currencyPair  The curreny pair
            orderNumber   The order number to cancel
        Outputs:
            succes        1 or 0
        """
        return self.api_query('cancelOrder', {"currencyPair": currency_pair, "orderNumber": order_number})

    def withdraw(self, currency, amount, address):
        """
        Immediately places a withdrawal for a given currency, with no email confirmation.
        In order to use this method, the withdrawal privilege must be enabled for your API key.
        Required POST parameters are "currency", "amount", and "address".
        Sample output: {"response": "Withdrew 2398 NXT."}
        Inputs:
            currency      The currency to withdraw
            amount        The amount of this coin to withdraw
            address       The withdrawal address
        Outputs:
            response      Text containing message about the withdrawal
        """
        return self.api_query('withdraw', {"currency": currency, "amount": amount, "address": address})
