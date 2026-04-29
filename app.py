import streamlit as st
import pandas as pd

# Load your data
data = pd.read_csv('data/baloxavir_stockpile.csv')

# Dashboard title
st.title('Baloxavir Stockpile Dashboard')

# Filters
location = st.sidebar.selectbox('Select Location:', data['Location'].unique())
date_range = st.sidebar.date_input('Select Date Range:', [data['Date'].min(), data['Date'].max()])

# Filter data based on selections
filtered_data = data[(data['Location'] == location) & (data['Date'].between(date_range[0], date_range[1]))]

# KPI Cards
st.write('### Key Performance Indicators')
st.metric('Total Stock', filtered_data['Stock'].sum())
st.metric('Total Distributions', filtered_data['Distributions'].sum())

# Visualizations
st.write('### Visualizations')
st.bar_chart(filtered_data['Stock'])

# Data Table
st.write('### Data Table')
st.dataframe(filtered_data)
