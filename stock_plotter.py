import tkinter as tk
from tkinter import ttk
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from datetime import datetime, timedelta

class StockPlotter:
    def __init__(self, master):
        self.master = master
        self.create_widgets()

    def format_date(self, x, pos=None):
        date = mdates.num2date(x)
        return date.strftime('%U-%Y')

    def plot_stock(self):
        ticker_symbol = self.ticker_entry.get()
        start_date = f"{self.start_year_var.get()}-{self.start_month_var.get()}-01"
        end_date = f"{self.end_year_var.get()}-{self.end_month_var.get()}-01"
        
        data = yf.download(ticker_symbol, start=start_date, end=end_date)
        self.ax.clear()  # Clear the previous plot

        if not data.empty:
            start_price = data.iloc[0]['Close']
            data['Percentage Change'] = (data['Close'] - start_price) / start_price * 100

            self.ax.plot(data.index, data['Percentage Change'], label='Percentage Change from Start')
            self.ax.set_title(f'Stock Price Percentage Change of {ticker_symbol}')
            self.ax.set_xlabel('Week-Year')
            self.ax.set_ylabel('Percentage Change')
            self.ax.legend()

            self.ax.xaxis.set_major_locator(ticker.MaxNLocator(10))
            self.ax.xaxis.set_major_formatter(ticker.FuncFormatter(self.format_date))

            self.canvas.draw()

            end_price = data.iloc[-1]['Close']
            price_change = end_price - start_price
            percent_change = (price_change / start_price) * 100

            self.info_text.set(f"Start Price: {start_price:.2f}, End Price: {end_price:.2f}, "
                               f"Change: {price_change:.2f} ({percent_change:.2f}%)")

    def create_widgets(self):
        # Create a frame for input fields and button
        input_frame = tk.Frame(self.master, borderwidth=2, relief="groove")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Entry for stock ticker
        tk.Label(input_frame, text="Stock Ticker:").grid(row=0, column=0, padx=5, pady=5)
        self.ticker_entry = tk.Entry(input_frame)
        self.ticker_entry.grid(row=0, column=1, padx=5, pady=5)

        # Dropdown for start and end year/month
        current_date = datetime.now()
        one_year_ago = current_date - timedelta(days=365)

        years = list(range(2000, current_date.year + 1))
        months = list(range(1, 13))

        self.start_year_var = tk.StringVar(value=one_year_ago.year)
        self.start_month_var = tk.StringVar(value=one_year_ago.month)
        self.end_year_var = tk.StringVar(value=current_date.year)
        self.end_month_var = tk.StringVar(value=current_date.month)

        tk.Label(input_frame, text="Start Year:").grid(row=1, column=0, padx=5, pady=5)
        tk.Label(input_frame, text="Start Month:").grid(row=1, column=2, padx=5, pady=5)
        tk.Label(input_frame, text="End Year:").grid(row=1, column=4, padx=5, pady=5)
        tk.Label(input_frame, text="End Month:").grid(row=1, column=6, padx=5, pady=5)

        start_year_menu = ttk.Combobox(input_frame, textvariable=self.start_year_var, values=years)
        start_month_menu = ttk.Combobox(input_frame, textvariable=self.start_month_var, values=months)
        end_year_menu = ttk.Combobox(input_frame, textvariable=self.end_year_var, values=years)
        end_month_menu = ttk.Combobox(input_frame, textvariable=self.end_month_var, values=months)

        start_year_menu.grid(row=1, column=1, padx=5, pady=5)
        start_month_menu.grid(row=1, column=3, padx=5, pady=5)
        end_year_menu.grid(row=1, column=5, padx=5, pady=5)
        end_month_menu.grid(row=1, column=7, padx=5, pady=5)

        # Plot button
        plot_button = tk.Button(input_frame, text="Plot Stock", command=self.plot_stock)
        plot_button.grid(row=0, column=8, padx=10, pady=5)

        # Embedding the plot in the tkinter window
        canvas_frame = tk.Frame(self.master, borderwidth=2, relief="groove")
        canvas_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        fig, self.ax = plt.subplots(figsize=(9, 4))
        self.ax.plot([], [])
        self.ax.set_xlabel('Week-Year')
        self.ax.set_ylabel('Price')

        self.canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Price information panel
        info_frame = tk.Frame(self.master, borderwidth=2, relief="groove")
        info_frame.grid(row=3, column=0, padx=10, pady=10, sticky="ew")

        self.info_text = tk.StringVar()
        info_label = tk.Label(info_frame, textvariable=self.info_text)
        info_label.pack(padx=10, pady=5)
