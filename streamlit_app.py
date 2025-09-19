import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import numpy as np
import sys  # for console debug printing

st.title("Stock Price Dashboard")

# Sidebar inputs
ticker = st.sidebar.text_input("Enter Stock Ticker", value="RELIANCE.BO")
start_date = st.sidebar.date_input("Start Date", value=pd.to_datetime("2022-01-01"))
end_date = st.sidebar.date_input("End Date", value=pd.to_datetime("today"))

if start_date > end_date:
    st.error("Error: Start Date must be before End Date.")
else:
    data = yf.download(ticker, start=start_date, end=end_date)

    if not data.empty:
        st.write(f"## {ticker} Stock Prices")
        data = data.reset_index()

        # Flatten MultiIndex columns if any
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [' '.join(map(str, col)).strip() for col in data.columns.values]

        # Just to confirm columns
        print("Columns in DataFrame:", list(data.columns), file=sys.stderr)

        st.write("### Data Table")
        st.dataframe(data)

        numeric_cols = data.select_dtypes(include=['number']).columns.tolist()

        if len(numeric_cols) == 0:
            st.warning("No numeric columns available to plot.")
        else:
            selected_col = st.selectbox(
                "Select numeric column to plot",
                options=numeric_cols,
                index=numeric_cols.index('Close') if 'Close' in numeric_cols else 0
            )

            # Prepare historical data
            data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
            plot_data = data.dropna(subset=['Date', selected_col]).copy()

            # === PREDICTION PART ===
            # For demo purposes: generate a simple mock prediction for next 30 days
            last_date = plot_data['Date'].max()
            future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=30, freq='B')  # business days

            # Simple model: last known value + random walk
            last_value = plot_data[selected_col].iloc[-1]
            np.random.seed(42)
            random_walk = np.random.normal(loc=0, scale=1, size=len(future_dates)).cumsum()
            predicted_values = last_value + random_walk

            pred_df = pd.DataFrame({
                'Date': future_dates,
                f'{selected_col}_predicted': predicted_values
            })

            # Combine historical and prediction data for plotting
            combined_df = pd.merge(plot_data[['Date', selected_col]], pred_df, on='Date', how='outer')

            # Plot both actual and predicted data
            import plotly.graph_objects as go

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=plot_data['Date'],
                y=plot_data[selected_col],
                mode='lines+markers',
                name='Actual'
            ))

            fig.add_trace(go.Scatter(
                x=pred_df['Date'],
                y=pred_df[f'{selected_col}_predicted'],
                mode='lines+markers',
                name='Predicted',
                line=dict(dash='dash')
            ))

            fig.update_layout(
                title=f"{selected_col} Price over Time for {ticker} (Actual vs Predicted)",
                xaxis_title='Date',
                yaxis_title=selected_col,
                legend=dict(x=0, y=1)
            )

            st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("No data found for the selected ticker and date range.")
