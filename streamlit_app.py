import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

st.title("Stock Price Dashboard")

# Sidebar for user input
ticker = st.sidebar.text_input("Enter Stock Ticker", value="RELIANCE.BO")
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2022-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("today"))

# Fetch data
data = yf.download(ticker, start=start_date, end=end_date)

if not data.empty:
    st.write(f"## {ticker} Stock Prices")
    data = data.reset_index()
    # Ensure the index is named 'Date' for plotting
    if 'Date' in data.columns:
        st.line_chart(data.set_index('Date')['Close'])
    else:
        # fallback: plot Close with default index
        st.line_chart(data['Close'])
    st.write("### Data Table")
    st.dataframe(data)
else:
    st.warning("No data found for the selected ticker and date range.")
