from datetime import datetime, timedelta
import yfinance as yf
import yoptions as yo
import pandas as pd
import fire
import math
from collections import OrderedDict
import copy

class StockStrategy():
    def __init__(self, stock_ticker='AFRM', contracts=10, start_date='2023-01-15', end_date='2023-09-20'):
        self.stock_ticker = stock_ticker
        self.contracts = contracts
        self.start_date = start_date
        self.end_date = end_date
        self.date_format = '%Y-%m-%d'

        start_datetime = datetime.strptime(start_date, self.date_format)
        end_datetime = datetime.strptime(end_date, self.date_format)

        start_weekday = start_datetime.strftime('%w')
        end_weekday = end_datetime.strftime('%w')

        start_delta = int(start_weekday) - 1
        end_delta = int(end_weekday) - 1

        self.start_monday = start_datetime - timedelta(days=start_delta)
        self.end_monday = end_datetime - timedelta(days=end_delta)

        start_monday_str = self.start_monday.strftime(self.date_format)

        # data = yf.download('AAPL', '2016-01-01', '2019-08-01')
        try:
            self.stock_price_history = yf.download(stock_ticker, start_date, end_date)
        except:
            print(f"Failed to find {stock_ticker} for these dates {start_date} {end_date}")
        print()


    def get_strike_price(self, option_date, price=0):
        """
        Gets the strike price close to the price assigned
        :param price:
        :return:
        """
        print(f"getting strike price close to {price:5.3f} on {option_date}...")
        strike_price_list = yo.get_chain_greeks_date(
            stock_ticker=self.stock_ticker,
            dividend_yield=0,
            option_type='c',
            expiration_date=option_date,
            risk_free_rate=None
        )
        val_list = list(strike_price_list['Strike'].values)
        strike_price = min([i for i in val_list if i > price])
        print(f'returning {strike_price} from {val_list}')
        return strike_price

    def get_option(self, buy_date, exp_date, strike, type):
        buy_date_str = buy_date.strftime(self.date_format)
        exp_date_str = exp_date.strftime(self.date_format)
        valid_strike = self.get_strike_price(exp_date_str, strike)

        print(f"trying to get {buy_date_str} {type} {exp_date_str} {strike} valid strike {valid_strike}")

        # yo.get_historical_option('AAPL', '2021-07-16', 90, 'p')
        df = yo.get_historical_option(self.stock_ticker, exp_date_str, valid_strike, type)
        df1 = df[df['Date'] == buy_date_str]
        val = df1['Open']
        return (val, valid_strike)

    def calc(self):
        self.all_data = []
        self.week_data = OrderedDict()
        self.week_data['week'] = 0
        self.week_data['date'] = self.start_date
        self.week_data['cash'] = 0
        self.week_data['stock'] = self.contracts * 100
        self.week_data['calls'] = 0
        self.week_data['puts'] = 0
        #self.week_data = {'week': 0, 'cash': 0, 'stock': self.contracts * 100, 'calls': 0, 'puts': 0}

        days_to_study = int((self.end_monday - self.start_monday).days)
        days_list = range(0, days_to_study, 7)
        for days_to_add in days_list:
            self.all_data.append(copy.deepcopy(self.week_data))
            self.week_data['week'] += 1

            current_monday = self.start_monday + timedelta(days=days_to_add)
            current_friday = current_monday + timedelta(days=4)

            self.week_data['date'] = current_monday.strftime(self.date_format)
            try:
                # first get all the data to do calculation
                monday_stock_price = self.stock_price_history.loc[current_monday]['Open']
                friday_stock_price_open = self.stock_price_history.loc[current_friday]['Open']
                friday_stock_price_close = self.stock_price_history.loc[current_friday]['Close']
                price_for_call, strike_for_call = self.get_option(
                    buy_date=current_monday,
                    exp_date=current_friday,
                    strike=monday_stock_price,
                    type='c'
                )
                price_for_put, strike_for_put = self.get_option(
                    buy_date=current_monday,
                    exp_date=current_friday,
                    strike=monday_stock_price * 0.89,
                    type='c'
                )

                ##############################
                # Mondays tasks
                #   1. buy stock
                #   2. sell cover call
                #   3. buy put
                ##############################
                total_price = (monday_stock_price * 100) - price_for_call + price_for_put
                for n in range(999):
                    if self.week_data['cash'] > total_price:
                        self.week_data['cash'] -= total_price
                        self.week_data['stock'] += 100
                        self.week_data['calls'] -= 1
                        self.week_data['puts'] += 1


                ##############################
                # Friday tasks
                #   1. got assigned
                #       a. sell at close price
                #       b. null options
                #   2. exit
                #       a. sell at open
                #       b. sell options
                ##############################
                for n in range(999):
                    if strike_for_call > friday_stock_price_close:
                        self.week_data['cash'] += strike_for_call * self.week_data['stock']
                        self.week_data['stock'] = 0
                    if strike_for_put > friday_stock_price_open:
                        self.week_data['cash'] += strike_for_put * self.week_data['stock']
                        self.week_data['stock'] = 0
                self.week_data['calls'] = 0
                self.week_data['puts'] = 0
                self.all_data.append(self.week_data.deepcopy())
                df = pd.DataFrame(self.all_data)
                df.to_csv("my_sim.csv")
            except:
                print("skipping week")


if __name__ == '__main__':
    fire.Fire(StockStrategy)
