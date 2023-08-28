from datetime import datetime, timedelta
import yfinance as yf
import yoptions as yo
import pandas as pd

class Stock():
    def __init__(self, stock_ticker, strike_margin = 0, days=31):
        self.stock_ticker = stock_ticker
        self.strike_maring = strike_margin
        self.days = days
        self.datetime_now = datetime.now()
        self.datetime_range = self.datetime_now + timedelta(self.days)

        try:
            self.ticker = yf.Ticker(stock_ticker)
        except:
            print(f"Could not find ticker {stock_ticker}")


        date_format = '%Y-%m-%d'
        date_str_list = list(self.ticker.options)
        good_dates = [i for i in date_str_list if datetime.strptime(i, date_format) < self.datetime_range]

        self.day_high = self.ticker.basic_info.day_high
        self.day_low = self.ticker.basic_info.day_low
        dummy_chain = yo.get_chain_greeks_date(
            stock_ticker=self.stock_ticker,
            dividend_yield=0,
            option_type='c',
            expiration_date=good_dates[-1],
            risk_free_rate=None
        )
        self.strike_values = dummy_chain["Strike"].values.tolist()
        self.strike_high = [i for i in self.strike_values if i > (self.day_high + strike_margin)]
        self.strike_high = min(self.strike_high)
        self.strike_low = [i for i in self.strike_values if i < (self.day_high + strike_margin)]
        self.strike_low = max(self.strike_low)

        self.data_by_date = []
        for good_dates_i in good_dates:
            data_dummy = {}
            data_dummy["Date"] = good_dates_i

            date_diff = datetime.strptime(good_dates_i, date_format) - self.datetime_now
            date_diff_days = date_diff.days
            date_diff_weeks = int(date_diff_days / 7) + 1
            data_dummy["Weeks Time"] = date_diff_weeks

            chain = yo.get_plain_option(
                stock_ticker=self.stock_ticker,
                option_type='c',
                expiration_date=good_dates_i,
                strike=self.strike_high
            )

            data_dummy["Stock Price"] = self.day_high
            data_dummy["Option Price"] = float(chain["Last Price"])
            data_dummy["Option Percent"] = float(chain["Last Price"]) / self.strike_high

            apr_constant = int(50 / date_diff_weeks)
            apr_value = (1 + data_dummy["Option Percent"]) ** apr_constant - 1
            data_dummy["Option APR"] = apr_value

            self.data_by_date.append(data_dummy)

        self.df = pd.DataFrame(self.data_by_date)
        print(self.df)
        print("DONE")


stck = Stock("AFRM")
