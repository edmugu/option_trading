import yfinance as yf
import yoptions as yo
import pandas as pd
from datetime import datetime, timedelta


class StockStrategySimulator:
    def __init__(self, stock_symbol, contract_num, start_date, end_date):
        self.stock_symbol = stock_symbol
        self.initial_cash = contract_num
        self.start_date = start_date
        self.end_date = end_date
        # data = yf.download('AAPL','2016-01-01','2019-08-01')
        self.historical_data = yf.download(stock_symbol, start_date, end_date)

    def get_option_data(self, expiration_date, days_to_expiration, option_type='p'):
        if self.option_data is None:
            self.option_data = yo.get_historical_option(self.stock_symbol, expiration_date, days_to_expiration,
                                                        option_type)

    def sell_cover_call(self):
        strike_price = (1 + self.strike_price_pct) * self.current_stock_price
        option_data = self.option_data[self.option_data['Date'] == self.current_date.strftime('%Y-%m-%d')]
        call_price = option_data.iloc[0]['Close']

        if self.current_stocks >= 100:
            num_calls = self.current_stocks // 100
            income_from_calls = num_calls * call_price * 100
            self.income.append(income_from_calls)
            self.total_revenue += income_from_calls
            self.current_cash += income_from_calls
            self.current_stocks -= num_calls * 100
            return num_calls, strike_price, call_price, income_from_calls
        else:
            return 0, strike_price, 0, 0

    def execute_strategy(self):
        self.get_historical_data()
        while self.current_date <= datetime.strptime(self.end_date, '%Y-%m-%d'):
            if self.current_date.weekday() == 0:  # Monday
                num_calls, strike_price, call_price, income_from_calls = self.sell_cover_call()
                print(f"Date: {self.current_date.strftime('%Y-%m-%d')}, Money: ${self.current_cash:.2f}, "
                      f"Stocks: {self.current_stocks}, Revenue in Cover Call: ${income_from_calls:.2f}")
                self.current_date += timedelta(days=7)  # Move to the next Monday
            else:
                self.current_date += timedelta(days=1)  # Move to the next day
        print(
            f"Summary of all actions - Total Income: ${sum(self.income):.2f}, Total Revenue: ${self.total_revenue:.2f}")

    def simulate(self):
        self.execute_strategy()


# Example usage:
if __name__ == "__main__":
    stock_symbol = 'AAPL'
    start_date = '2016-01-01'
    end_date = '2019-08-01'
    initial_cash = 10000
    num_stocks = 1000

    simulator = StockStrategySimulator(stock_symbol, start_date, end_date, initial_cash, num_stocks)
    simulator.simulate()
