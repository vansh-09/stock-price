import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
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

        # Check for MultiIndex columns and flatten them
        if isinstance(data.columns, pd.MultiIndex):
            print("Data has MultiIndex columns:", data.columns, file=sys.stderr)
            data.columns = [' '.join(map(str, col)).strip() for col in data.columns.values]
            print("Flattened columns:", list(data.columns), file=sys.stderr)

        # Print debug info to console only, NOT in Streamlit UI
        print("Columns in DataFrame:", list(data.columns), file=sys.stderr)
        print("DataFrame dtypes:\n", data.dtypes, file=sys.stderr)

        st.write("### Data Table")
        st.dataframe(data)

        numeric_cols = data.select_dtypes(include=['number']).columns.tolist()
        print("Numeric columns detected:", numeric_cols, file=sys.stderr)

        if len(numeric_cols) == 0:
            st.warning("No numeric columns available to plot.")
        else:
            selected_col = st.selectbox(
                "Select numeric column to plot",
                options=numeric_cols,
                index=numeric_cols.index('Close RELIANCE.BO') if 'Close RELIANCE.BO' in numeric_cols else 0
            )

            print("Selected column:", selected_col, file=sys.stderr)

            if isinstance(selected_col, (list, tuple)):
                selected_col = selected_col[0]

            if 'Date' not in data.columns:
                st.warning("Date column missing, cannot generate chart.")
            elif selected_col not in data.columns:
                st.error(f"Selected column '{selected_col}' not found in data columns.")
            else:
                data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
                plot_data = data.dropna(subset=['Date', selected_col])

                print(f"Rows after dropping NaNs: {len(plot_data)}", file=sys.stderr)

                if plot_data.empty:
                    st.warning("No valid data available for plotting after cleaning.")
                else:
                    fig = px.line(
                        plot_data,
                        x='Date',
                        y=selected_col,
                        title=f"{selected_col} Price over Time for {ticker}"
                    )
                    fig.update_layout(xaxis_title='Date', yaxis_title=selected_col)
                    st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("No data found for the selected ticker and date range.")
