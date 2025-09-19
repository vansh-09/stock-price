import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import pickle
from tensorflow.keras.models import load_model
import time
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from sklearn.preprocessing import MinMaxScaler

# Load models and scaler
model = load_model('reliance_lstm.h5')  # LSTM model
scaler = pickle.load(open('scaler.pkl', 'rb'))  # Scaler (if needed)

# Function to fetch stock data
def fetch_data(ticker):
    data = yf.download(ticker, period="1d", interval="1m")
    return data

# Function to preprocess data for LSTM model
def preprocess_data(df):
    df = df[['Close']]  # Use the 'Close' prices for prediction
    scaled_data = scaler.transform(df)
    return scaled_data

# Function to make predictions using the LSTM model
def predict_lstm(data):
    # Reshape data for prediction (as expected by the LSTM model)
    prediction_input = data[-60:].reshape(1, 60, 1)  # Adjust this based on your model's input shape
    prediction = model.predict(prediction_input)
    return scaler.inverse_transform(prediction)

# Streamlit Dashboard
def main():
    st.title("LSTM Stock Price Prediction Dashboard")
    
    ticker = st.text_input('Enter Stock Ticker (e.g., AAPL)', 'AAPL')  # Default ticker
    interval = 5  # Data update interval in minutes
    
    # Data Loading
    data = fetch_data(ticker)
    
    # Preprocess the data
    processed_data = preprocess_data(data)
    
    # Predict the next value
    predicted_price = predict_lstm(processed_data)
    
    # Display Latest Data
    st.subheader("Latest Stock Data")
    st.dataframe(data.tail(10))  # Display latest 10 data points
    
    # Display prediction
    st.subheader(f"Predicted Next Price for {ticker}")
    st.write(f"Predicted Price: {predicted_price[0][0]:.2f}")
    
    # Plot the graph
    st.subheader("Stock Price Chart")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Actual Price'))
    fig.update_layout(title=f"{ticker} Stock Price", xaxis_title="Time", yaxis_title="Price (USD)")
    st.plotly_chart(fig)
    
    # Show real-time update (every 5 minutes)
    st.write("Updating every 5 minutes...")

if __name__ == "__main__":
    main()
