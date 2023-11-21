import yfinance as yf
import yoptions as yo

aapl = yf.Ticker("AAPL")

# show options expirations
print(aapl.options)
chain = yo.get_chain_greeks_date(stock_ticker='AAPL',
                                 dividend_yield=0,
                                 option_type='p',
                                 expiration_date='2023-09-01',
                                 risk_free_rate=None)


strike_list = list(chain.Strike)
print(print(chain.head().to_string()))
print()