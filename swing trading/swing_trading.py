import tkinter as tk
from tkinter import ttk
from stock_plotter import StockPlotter
from multi_timeframe_plotter import MultiTimeFramePlotter

# Main window setup
window = tk.Tk()
window.title("Stock Analysis Tool")
window.geometry("1000x600")

# Create Notebook (Tab control)
tab_control = ttk.Notebook(window)

# Tab 1: Stock Price Plotter
tab1 = ttk.Frame(tab_control)
tab_control.add(tab1, text='Stock Price Plotter')
stock_plotter = StockPlotter(tab1)

# Tab 2: Multi-Timeframe Stock Plotter
tab2 = ttk.Frame(tab_control)
tab_control.add(tab2, text='Multi-Timeframe Stock Plotter')
multi_timeframe_plotter = MultiTimeFramePlotter(tab2)

tab_control.pack(expand=1, fill="both")

# Run the application
window.mainloop()
