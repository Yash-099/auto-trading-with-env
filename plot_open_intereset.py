import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime
# Function to read CSV files and extract relevant data
def read_csv_files(folder_path):
    files_with_dates = []
    
    # Collect filenames and corresponding dates
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv") and filename.startswith("Spurts-in-OI-By-Underlying"):
            date_str = filename.split('-')[-1].split('.')[0]  # Extract date from filename
            date = datetime.strptime(date_str, '%d%m%Y')  # Convert date string to datetime object
            files_with_dates.append((filename, date))

    files_with_dates.sort(key=lambda x: x[1])
    


    data_frames = []
    for filename, date in files_with_dates  :
        if filename.endswith(".csv") and filename.startswith("Spurts-in-OI-By-Underlying"):
            file_path = os.path.join(folder_path, filename)
            df = pd.read_csv(file_path)
            df['Date'] = date
            print(df.columns)
            data_frames.append(df)
    return pd.concat(data_frames, ignore_index=True)

# Function to plot Open Interest
def plot_open_interest(symbol_data, symbol):
    plt.figure(figsize=(10, 5))
    plt.plot(symbol_data['Date'], symbol_data['Open Interest'], label='Open Interest', color='tab:blue')
    plt.xlabel('Date')
    plt.ylabel('Open Interest')
    plt.title(f'{symbol} - Open Interest')
    plt.xticks(rotation=45)
    plt.grid(True)
    st.pyplot(plt)

# Function to plot Underlying value
def plot_futures_value(symbol_data, symbol):
    plt.figure(figsize=(10, 5))
    plt.plot(symbol_data['Date'], symbol_data['Underlying value'], label='Underlying value', color='tab:red')
    plt.xlabel('Date')
    plt.ylabel('Underlying value')
    plt.title(f'{symbol} - Underlying value')
    plt.xticks(rotation=45)
    plt.grid(True)
    st.pyplot(plt)

# Main function to run the Streamlit app
def main():
    st.title('Stock Open Interest and Underlying value Visualization')

    folder_path = '/Users/ybhavsar/Documents/open_interest_data'
    df = read_csv_files(folder_path)
    
    # Ensure the Date column is properly formatted
    df['Date'] = pd.to_datetime(df['Date'], format='%d%m%Y').dt.date
    
    symbols = df['Symbol'].unique()
    selected_symbol = st.selectbox('Select a stock symbol:', symbols)

    if selected_symbol:
        symbol_data = df[df['Symbol'] == selected_symbol]
        plot_open_interest(symbol_data, selected_symbol)
        plot_futures_value(symbol_data, selected_symbol)

if __name__ == "__main__":
    main()
