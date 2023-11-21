import tkinter as tk
from tkinter import ttk
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

class MultiTimeFramePlotter:
    def __init__(self, master):
        self.master = master
        self.create_widgets()

    def plot_stock_multi_timeframe(self):
        ticker_symbol = self.ticker_entry.get()
        start_year = int(self.start_year_var.get())
        end_year = int(self.end_year_var.get())
        start_month = int(self.start_month_var.get())
        end_month = int(self.end_month_var.get())

        self.ax.clear()  # Clear the previous plot

        # Initialize data frame to track cumulative percentage change
        cumulative_data = []

        x = 0  # Initialize x-axis value

        for year in range(start_year, end_year + 1):
            #for month in range(start_month, end_month + 1):
            # Calculate the start and end dates for the current time frame
            start_date = f"{year}-{start_month:02d}-01"
            end_date = f"{year}-{end_month:02d}-01"

            data = yf.download(ticker_symbol, start=start_date, end=end_date)
            if not data.empty:
                # Calculate the percentage change from the beginning of the time frame
                start_price = data.iloc[0]['Close']
                x = list((data['Close'] - start_price) / start_price * 100)

                # Add the data to the cumulative data frame with updated x values
                self.ax.plot(x, label=str(year))


        self.ax.set_title(f'Stock Price Percentage Change (Multiple Timeframes)')
        self.ax.set_xlabel('Time (from the beginning of timeframes)')
        self.ax.set_ylabel('Percentage Change')
        self.ax.legend()
        self.canvas.draw()

    def create_widgets(self):
        # Create a frame for input fields and button
        input_frame = tk.Frame(self.master, borderwidth=2, relief="groove")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Entry for stock ticker
        tk.Label(input_frame, text="Stock Ticker:").grid(row=0, column=0, padx=5, pady=5)
        self.ticker_entry = tk.Entry(input_frame)
        self.ticker_entry.grid(row=0, column=1, padx=5, pady=5)

        # Dropdown for start and end year/month
        years = list(range(2000, datetime.datetime.now().year + 1))
        months = list(range(1, 13))

        self.start_year_var = tk.StringVar(value=years[0])
        self.end_year_var = tk.StringVar(value=years[-1])
        self.start_month_var = tk.StringVar(value=1)
        self.end_month_var = tk.StringVar(value=12)

        tk.Label(input_frame, text="Start Year:").grid(row=1, column=0, padx=5, pady=5)
        tk.Label(input_frame, text="End Year:").grid(row=1, column=2, padx=5, pady=5)
        tk.Label(input_frame, text="Start Month:").grid(row=1, column=4, padx=5, pady=5)
        tk.Label(input_frame, text="End Month:").grid(row=1, column=6, padx=5, pady=5)

        start_year_menu = ttk.Combobox(input_frame, textvariable=self.start_year_var, values=years)
        end_year_menu = ttk.Combobox(input_frame, textvariable=self.end_year_var, values=years)
        start_month_menu = ttk.Combobox(input_frame, textvariable=self.start_month_var, values=months)
        end_month_menu = ttk.Combobox(input_frame, textvariable=self.end_month_var, values=months)

        start_year_menu.grid(row=1, column=1, padx=5, pady=5)
        end_year_menu.grid(row=1, column=3, padx=5, pady=5)
        start_month_menu.grid(row=1, column=5, padx=5, pady=5)
        end_month_menu.grid(row=1, column=7, padx=5, pady=5)

        # Plot button
        plot_button = tk.Button(input_frame, text="Plot Stock", command=self.plot_stock_multi_timeframe)
        plot_button.grid(row=0, column=8, padx=10, pady=5)

        # Embedding the plot in the tkinter window
        canvas_frame = tk.Frame(self.master, borderwidth=2, relief="groove")
        canvas_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        fig, self.ax = plt.subplots(figsize=(9, 4))
        self.ax.plot([], [])
        self.ax.set_xlabel('Date')
        self.ax.set_ylabel('Price')

        self.canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
