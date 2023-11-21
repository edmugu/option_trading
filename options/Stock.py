from datetime import datetime, timedelta
import yfinance as yf
import yoptions as yo
import pandas as pd
import fire
import math

pd.options.display.max_colwidth = 200  # set a value as your need

class Stock():
    def __init__(self, stock="CMCSA", days=31):
        self.stock_ticker = stock
        self.days = days
        self.datetime_now = datetime.now()
        self.datetime_range = self.datetime_now + timedelta(self.days)

        try:
            self.ticker = yf.Ticker(stock)
        except:
            print(f"Could not find ticker {stock}")
        self.stock_price = self.ticker.basic_info.last_price
        self.date_format = '%Y-%m-%d'
        date_str_list = list(self.ticker.options)
        self.options_dates = [i for i in date_str_list if datetime.strptime(i, self.date_format) < self.datetime_range]
        self.options_dict = {}
        self.data_entry = {}
        self.data_by_date = []

        print("Getting strike price list...")
        strike_price_list = yo.get_chain_greeks_date(
            stock_ticker=self.stock_ticker,
            dividend_yield=0,
            option_type='c',
            expiration_date=self.options_dates[-1],
            risk_free_rate=None
        )
        self.strike_price_list = list(strike_price_list['Strike'].values)
        print()

    def __repr__(self):
        self.__str__()

    def __str__(self):
        s = f"Stock {self.stock_ticker} is at {self.stock_price}"
        return s

    def get_strike_price(self, option_date, price=0):
        """
        Gets the strike price close to the percent assigned
        :param price:
        :return:
        """
        if price < 0.01:
            price = self.stock_price
        print(f"getting strike price close to {price:5.3f} ...")
        strike_price_list = yo.get_chain_greeks_date(
            stock_ticker=self.stock_ticker,
            dividend_yield=0,
            option_type='c',
            expiration_date=option_date,
            risk_free_rate=None
        )
        val_list = list(strike_price_list['Strike'].values)
        if price >= self.stock_price:
            strike_price = min([i for i in val_list if i > price])
        else:
            strike_price = max([i for i in val_list if i < price])
        return strike_price

    def get_option_price(self, option_date, option_price, option_type='c'):
        price = self.get_strike_price(option_date, option_price)
        skey = f"{option_type}, {price:6.3f}, {option_date}"
        print(f"getting option price {skey}")
        if skey not in self.options_dict.keys():
            self.options_dict[skey] = yo.get_plain_option(
                stock_ticker=self.stock_ticker,
                option_type=option_type,
                expiration_date=option_date,
                strike=price
            )
        tmp = float(self.options_dict[skey]["Last Price"])
        self.data_entry[f"{option_type} @ {price:09.3f}"] = tmp
        return tmp

    def calc(self, method="XYLD"):
        strategy_options = {
            "XYLD": [['c', 1.0, 1.00]],
            "XYLG": [['c', 0.5, 1.00]],
            "XRMI": [['c', 1.0, 1.00], ['p', 1.0, 0.95]],
            "XTR" : [['p', 1.0, 0.90]],
            "XCLR": [['c', 1.0, 1.10], ['p', 1.0, 0.95]]
        }
        if method not in strategy_options.keys():
            raise ValueError(f"method {method} not in {strategy_options.keys()}")


        self.data_by_date = []
        for options_dates_i in self.options_dates:
            self.data_entry = {}
            self.data_entry["Date"] = options_dates_i
            self.data_entry["Stock Price"] = self.stock_price

            date_diff = datetime.strptime(options_dates_i, self.date_format) - self.datetime_now
            date_diff_days = date_diff.days
            date_diff_weeks = int(date_diff_days / 7) + 1
            self.data_entry["Weeks Time"] = date_diff_weeks
            apr_constant = int(50 / date_diff_weeks)

            option_income = 0
            for op_type, op_percent, op_strike_percent in strategy_options[method]:
                try:
                    op_price = self.get_option_price(
                                        options_dates_i,
                                        op_strike_percent * self.stock_price,
                                        op_type)
                    if op_type.upper() == "C":
                        option_income += op_percent * op_price
                    if op_type.upper() == "P":
                        option_income -= op_percent * op_price

                    self.data_entry["Option Income"] = option_income
                    self.data_entry["Option Income Perc"] = option_income / self.stock_price

                    apr_value = (1 + self.data_entry["Option Income Perc"]) ** apr_constant - 1
                    self.data_entry["Option APR"] = apr_value

                    self.data_by_date.append(self.data_entry)
                except:
                    pass

                self.df = pd.DataFrame(self.data_by_date)
                self.df.to_csv("data.csv")
                print(self.df)

if __name__ == '__main__':
    fire.Fire(Stock)
