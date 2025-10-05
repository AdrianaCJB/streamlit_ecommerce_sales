import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="E-commerce Sales Dashboard",
    page_icon="🛒",
    layout="wide"
)

# Title
st.title("🛒 E-commerce Sales Analytics Dashboard")

# Load data with caching
@st.cache_data
def load_data():
    # Update this path to where your CSV file is located
    df = pd.read_csv('Ecommerce_Sales_Data_2024_2025.csv')
    
    # Convert date column to datetime (adjust column name as needed)
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
    elif 'Order Date' in df.columns:
        df['Order Date'] = pd.to_datetime(df['Order Date'])
    
    return df

try:
    df = load_data()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Date range filter (if date column exists)
    date_col = 'Date' if 'Date' in df.columns else ('Order Date' if 'Order Date' in df.columns else None)
    
    if date_col:
        min_date = df[date_col].min()
        max_date = df[date_col].max()
        
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        if len(date_range) == 2:
            df = df[(df[date_col] >= pd.to_datetime(date_range[0])) & 
                   (df[date_col] <= pd.to_datetime(date_range[1]))]
    
    # Category filter (adjust column name as needed)
    category_col = None
    for col in ['Category', 'Product Category', 'Item Category']:
        if col in df.columns:
            category_col = col
            break
    
    if category_col:
        categories = ['All'] + sorted(df[category_col].unique().tolist())
        selected_category = st.sidebar.selectbox("Select Category", categories)
        
        if selected_category != 'All':
            df = df[df[category_col] == selected_category]
    
    # Key Metrics
    st.header("📊 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate metrics (adjust column names based on actual data)
    amount_col = None
    for col in ['Amount', 'Sales', 'Total', 'Revenue', 'Price']:
        if col in df.columns:
            amount_col = col
            break
    
    quantity_col = None
    for col in ['Quantity', 'Qty', 'Units']:
        if col in df.columns:
            quantity_col = col
            break
    
    if amount_col:
        total_sales = df[amount_col].sum()
        avg_order_value = df[amount_col].mean()
        col1.metric("Total Sales", f"${total_sales:,.2f}")
        col2.metric("Avg Order Value", f"${avg_order_value:,.2f}")
    
    col3.metric("Total Orders", f"{len(df):,}")
    
    if quantity_col:
        total_quantity = df[quantity_col].sum()
        col4.metric("Total Units Sold", f"{total_quantity:,.0f}")
    
    # Main Dashboard Area
    row1_col1, row1_col2 = st.columns(2)
    
    # Sales Trend Over Time
    if date_col and amount_col:
        with row1_col1:
            st.subheader("📈 Sales Trend Over Time")
            daily_sales = df.groupby(df[date_col].dt.date)[amount_col].sum().reset_index()
            daily_sales.columns = ['Date', 'Sales']
            
            fig = px.line(daily_sales, x='Date', y='Sales', 
                         title='Daily Sales',
                         labels={'Sales': 'Total Sales ($)'})
            fig.update_traces(line_color='#1f77b4')
            st.plotly_chart(fig, use_container_width=True)
    
    # Top Products/Categories
    if category_col and amount_col:
        with row1_col2:
            st.subheader("🏆 Top Categories by Revenue")
            top_categories = df.groupby(category_col)[amount_col].sum().sort_values(ascending=False).head(10)
            
            fig = px.bar(x=top_categories.values, y=top_categories.index, 
                        orientation='h',
                        labels={'x': 'Revenue ($)', 'y': 'Category'},
                        title='Top 10 Categories')
            fig.update_traces(marker_color='#ff7f0e')
            st.plotly_chart(fig, use_container_width=True)
    
    row2_col1, row2_col2 = st.columns(2)
    
    # Sales Distribution
    if amount_col:
        with row2_col1:
            st.subheader("💰 Sales Distribution")
            fig = px.histogram(df, x=amount_col, nbins=50,
                             labels={amount_col: 'Order Amount ($)'},
                             title='Distribution of Order Values')
            fig.update_traces(marker_color='#2ca02c')
            st.plotly_chart(fig, use_container_width=True)
    
    # Monthly Sales Comparison
    if date_col and amount_col:
        with row2_col2:
            st.subheader("📅 Monthly Sales Comparison")
            df['Month'] = df[date_col].dt.to_period('M').astype(str)
            monthly_sales = df.groupby('Month')[amount_col].sum().reset_index()
            
            fig = px.bar(monthly_sales, x='Month', y=amount_col,
                        title='Sales by Month',
                        labels={amount_col: 'Total Sales ($)'})
            fig.update_traces(marker_color='#d62728')
            st.plotly_chart(fig, use_container_width=True)
    
    # Data Table
    st.header("📋 Detailed Data View")
    st.dataframe(df.head(100), use_container_width=True)
    
    # Download filtered data
    st.download_button(
        label="Download Filtered Data as CSV",
        data=df.to_csv(index=False).encode('utf-8'),
        file_name='filtered_sales_data.csv',
        mime='text/csv',
    )
    
except FileNotFoundError:
    st.error("⚠️ Dataset not found! Please make sure 'Details.csv' is in the same directory as this script.")
    st.info("""
    **To use this dashboard:**
    1. Download the dataset from Kaggle
    2. Extract the CSV file
    3. Place it in the same directory as this script
    4. Update the file path in the `load_data()` function if needed
    """)
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please check your data file and column names.")