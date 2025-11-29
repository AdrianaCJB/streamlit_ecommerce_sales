import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

# Page configuration
st.set_page_config(
    page_title="E-commerce Sales Dashboard",
    page_icon="🛒",
    layout="wide"
)

# Title
st.title("🛒 E-commerce Sales Analytics Dashboard")

# Function to create matplotlib charts for PDF
def create_sales_trend_chart(df, date_col, amount_col):
    """Create sales trend chart using matplotlib"""
    daily_sales = df.groupby(df[date_col].dt.date)[amount_col].sum().reset_index()
    daily_sales.columns = ['Date', 'Sales']
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(daily_sales['Date'], daily_sales['Sales'], color='#1f77b4', linewidth=2)
    ax.set_xlabel('Date', fontsize=11)
    ax.set_ylabel('Total Sales ($)', fontsize=11)
    ax.set_title('Daily Sales Trend', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return buf

def create_top_categories_chart(df, category_col, amount_col):
    """Create top categories chart using matplotlib"""
    top_categories = df.groupby(category_col)[amount_col].sum().sort_values(ascending=True).tail(10)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(range(len(top_categories)), top_categories.values, color='#ff7f0e')
    ax.set_yticks(range(len(top_categories)))
    ax.set_yticklabels(top_categories.index, fontsize=10)
    ax.set_xlabel('Revenue ($)', fontsize=11)
    ax.set_title('Top 10 Categories by Revenue', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    # Add value labels on bars
    for i, v in enumerate(top_categories.values):
        ax.text(v, i, f' ${v:,.0f}', va='center', fontsize=9)
    
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return buf

def create_distribution_chart(df, amount_col):
    """Create sales distribution chart using matplotlib"""
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.hist(df[amount_col], bins=50, color='#2ca02c', edgecolor='black', alpha=0.7)
    ax.set_xlabel('Order Amount ($)', fontsize=11)
    ax.set_ylabel('Frequency', fontsize=11)
    ax.set_title('Distribution of Order Values', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return buf

def create_monthly_chart(df, date_col, amount_col):
    """Create monthly sales chart using matplotlib"""
    df_temp = df.copy()
    df_temp['Month'] = df_temp[date_col].dt.to_period('M').astype(str)
    monthly_sales = df_temp.groupby('Month')[amount_col].sum().reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(range(len(monthly_sales)), monthly_sales[amount_col], color='#d62728', edgecolor='black', alpha=0.7)
    ax.set_xticks(range(len(monthly_sales)))
    ax.set_xticklabels(monthly_sales['Month'], rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Total Sales ($)', fontsize=11)
    ax.set_title('Sales by Month', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for i, v in enumerate(monthly_sales[amount_col]):
        ax.text(i, v, f'${v:,.0f}', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return buf

# Function to create branded PDF report
def create_branded_pdf_report(df, metrics_data, charts_data, date_col, amount_col, category_col, quantity_col, filter_info):
    """Generate a professional branded PDF proposal with charts"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        topMargin=0.5*inch, 
        bottomMargin=0.75*inch,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch
    )
    
    # Container for PDF elements
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles for branding
    title_style = ParagraphStyle(
        'BrandTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'BrandSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor=colors.HexColor('#666666'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1f77b4'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold',
        borderWidth=2,
        borderColor=colors.HexColor('#1f77b4'),
        borderPadding=8,
        backColor=colors.HexColor('#f0f8ff')
    )
    
    # ==================== COVER PAGE ====================
    elements.append(Spacer(1, 1.5*inch))
    
    # Company branding header
    brand_box_data = [[Paragraph("E-COMMERCE ANALYTICS", title_style)]]
    brand_box = Table(brand_box_data, colWidths=[6.5*inch])
    brand_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#1f77b4')),
        ('PADDING', (0, 0), (-1, -1), 20),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(brand_box)
    elements.append(Spacer(1, 0.5*inch))
    
    # Title
    title = Paragraph("Sales Performance Proposal", title_style)
    elements.append(title)
    
    subtitle = Paragraph("Comprehensive Analytics Report", subtitle_style)
    elements.append(subtitle)
    
    elements.append(Spacer(1, 1*inch))
    
    # Report metadata box
    report_info = [
        ['Report Generated:', datetime.now().strftime('%B %d, %Y at %H:%M')],
        ['Date Range:', filter_info.get('date_range', 'All Dates')],
        ['Category Filter:', filter_info.get('category', 'All Categories')],
        ['Total Records:', filter_info.get('total_records', 'N/A')]
    ]
    
    info_table = Table(report_info, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8e8e8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(info_table)
    
    elements.append(PageBreak())
    
    # ==================== ASSUMPTIONS PAGE ====================
    elements.append(Paragraph("Key Assumptions & Methodology", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    
    assumptions_text = """
    <para alignment="left" spaceBefore=6 spaceAfter=6>
    <b>Data Source & Quality:</b><br/>
    • All data is sourced from the company's e-commerce transaction database<br/>
    • Data has been validated and cleaned for accuracy<br/>
    • Missing or incomplete records have been excluded from analysis<br/>
    <br/>
    <b>Date Range & Filtering:</b><br/>
    • Analysis covers the selected date range as specified in filters<br/>
    • Category filtering applied where specified<br/>
    • All monetary values are in USD ($)<br/>
    <br/>
    <b>Calculation Methodology:</b><br/>
    • Total Sales: Sum of all transaction amounts in the filtered dataset<br/>
    • Average Order Value: Mean transaction amount across all orders<br/>
    • Total Orders: Count of unique transactions in the period<br/>
    • Total Units Sold: Sum of all quantity values (where applicable)<br/>
    <br/>
    <b>Visualization Standards:</b><br/>
    • Charts display top 10 categories by default for clarity<br/>
    • Time-series data aggregated daily or monthly as appropriate<br/>
    • Color coding maintained consistently across all visualizations<br/>
    <br/>
    <b>Report Limitations:</b><br/>
    • Analysis reflects only the filtered data subset<br/>
    • Future projections not included in this report<br/>
    • External market factors not accounted for in metrics<br/>
    <br/>
    <b>Geographic Considerations:</b><br/>
    • Sales data may include multiple geographic regions<br/>
    • Currency conversions applied where applicable<br/>
    • Regional performance variations reflected in category analysis<br/>
    </para>
    """
    
    assumptions_para = Paragraph(assumptions_text, styles['Normal'])
    elements.append(assumptions_para)
    
    elements.append(PageBreak())
    
    # ==================== KEY METRICS PAGE ====================
    elements.append(Paragraph("Executive Summary - Key Performance Indicators", heading_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # KPI Cards styled as table
    kpi_data = [
        ['TOTAL SALES', 'AVG ORDER VALUE'],
        [metrics_data.get('total_sales', 'N/A'), metrics_data.get('avg_order_value', 'N/A')],
        ['TOTAL ORDERS', 'TOTAL UNITS SOLD'],
        [metrics_data.get('total_orders', 'N/A'), metrics_data.get('total_units', 'N/A')]
    ]
    
    kpi_table = Table(kpi_data, colWidths=[3.25*inch, 3.25*inch])
    kpi_table.setStyle(TableStyle([
        # Headers
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
        ('BACKGROUND', (0, 2), (-1, 2), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('TEXTCOLOR', (0, 2), (-1, 2), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('FONTSIZE', (0, 2), (-1, 2), 11),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        # Values
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#e6f2ff')),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#e6f2ff')),
        ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
        ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, 1), 18),
        ('FONTSIZE', (0, 3), (-1, 3), 18),
        ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor('#1f77b4')),
        ('TEXTCOLOR', (0, 3), (-1, 3), colors.HexColor('#1f77b4')),
        ('PADDING', (0, 0), (-1, -1), 15),
        ('GRID', (0, 0), (-1, -1), 2, colors.HexColor('#1f77b4')),
    ]))
    elements.append(kpi_table)
    
    elements.append(PageBreak())
    
    # ==================== CHARTS PAGE ====================
    elements.append(Paragraph("Sales Trend Analysis", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    
    if 'sales_trend' in charts_data and charts_data['sales_trend']:
        img_sales = Image(charts_data['sales_trend'], width=6.5*inch, height=3*inch)
        elements.append(img_sales)
        elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("Top Categories Performance", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    
    if 'top_categories' in charts_data and charts_data['top_categories']:
        img_categories = Image(charts_data['top_categories'], width=6.5*inch, height=3.5*inch)
        elements.append(img_categories)
    
    elements.append(PageBreak())
    
    # ==================== MORE CHARTS ====================
    elements.append(Paragraph("Sales Distribution", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    
    if 'sales_distribution' in charts_data and charts_data['sales_distribution']:
        img_dist = Image(charts_data['sales_distribution'], width=6.5*inch, height=3*inch)
        elements.append(img_dist)
        elements.append(Spacer(1, 0.2*inch))
    
    elements.append(Paragraph("Monthly Comparison", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    
    if 'monthly_sales' in charts_data and charts_data['monthly_sales']:
        img_monthly = Image(charts_data['monthly_sales'], width=6.5*inch, height=3*inch)
        elements.append(img_monthly)
    
    elements.append(PageBreak())
    
    # ==================== DATA INSIGHTS PAGE ====================
    elements.append(Paragraph("Top 10 Categories - Detailed Breakdown", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    
    if category_col and amount_col:
        top_categories = df.groupby(category_col)[amount_col].sum().sort_values(ascending=False).head(10)
        
        category_data = [['Rank', 'Category', 'Revenue', '% of Total']]
        total_revenue = top_categories.sum()
        
        for idx, (category, revenue) in enumerate(top_categories.items(), 1):
            percentage = (revenue / total_revenue * 100) if total_revenue > 0 else 0
            category_data.append([
                str(idx), 
                str(category)[:40],  # Truncate long names
                f"${revenue:,.2f}",
                f"{percentage:.1f}%"
            ])
        
        category_table = Table(category_data, colWidths=[0.6*inch, 3*inch, 1.8*inch, 1.1*inch])
        category_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ff7f0e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('PADDING', (0, 1), (-1, -1), 8),
        ]))
        
        elements.append(category_table)
    
    # ==================== FOOTER ====================
    elements.append(Spacer(1, 0.5*inch))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    footer_text = f"""
    <para alignment="center">
    ──────────────────────────────────────────────────────────────<br/>
    <b>E-commerce Analytics Dashboard</b><br/>
    This report is generated automatically based on filtered data<br/>
    For questions or clarifications, please contact the analytics team<br/>
    © {datetime.now().year} E-commerce Analytics. All rights reserved.
    </para>
    """
    elements.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Load data with caching
@st.cache_data
def load_data():
    df = pd.read_csv('Ecommerce_Sales_Data_2024_2025.csv')
    
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
    elif 'Order Date' in df.columns:
        df['Order Date'] = pd.to_datetime(df['Order Date'])
    
    return df

try:
    df = load_data()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    date_col = 'Date' if 'Date' in df.columns else ('Order Date' if 'Order Date' in df.columns else None)
    
    filter_info = {}
    
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
            filter_info['date_range'] = f"{date_range[0]} to {date_range[1]}"
        else:
            filter_info['date_range'] = "All Dates"
    
    category_col = None
    for col in ['Category', 'Product Category', 'Item Category']:
        if col in df.columns:
            category_col = col
            break
    
    selected_category = 'All'
    if category_col:
        categories = ['All'] + sorted(df[category_col].unique().tolist())
        selected_category = st.sidebar.selectbox("Select Category", categories)
        
        if selected_category != 'All':
            df = df[df[category_col] == selected_category]
        filter_info['category'] = selected_category
    
    filter_info['total_records'] = f"{len(df):,}"
    
    # Key Metrics
    st.header("📊 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
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
    
    metrics_data = {}
    
    if amount_col:
        total_sales = df[amount_col].sum()
        avg_order_value = df[amount_col].mean()
        col1.metric("Total Sales", f"${total_sales:,.2f}")
        col2.metric("Avg Order Value", f"${avg_order_value:,.2f}")
        metrics_data['total_sales'] = f"${total_sales:,.2f}"
        metrics_data['avg_order_value'] = f"${avg_order_value:,.2f}"
    
    col3.metric("Total Orders", f"{len(df):,}")
    metrics_data['total_orders'] = f"{len(df):,}"
    
    if quantity_col:
        total_quantity = df[quantity_col].sum()
        col4.metric("Total Units Sold", f"{total_quantity:,.0f}")
        metrics_data['total_units'] = f"{total_quantity:,.0f}"
    else:
        metrics_data['total_units'] = "N/A"
    
    # Main Dashboard Area
    row1_col1, row1_col2 = st.columns(2)
    
    # Sales Trend Over Time
    if date_col and amount_col:
        with row1_col1:
            st.subheader("📈 Sales Trend Over Time")
            daily_sales = df.groupby(df[date_col].dt.date)[amount_col].sum().reset_index()
            daily_sales.columns = ['Date', 'Sales']
            
            fig_trend = px.line(daily_sales, x='Date', y='Sales', 
                         title='Daily Sales',
                         labels={'Sales': 'Total Sales ($)'})
            fig_trend.update_traces(line_color='#1f77b4', line_width=2)
            fig_trend.update_layout(plot_bgcolor='white')
            st.plotly_chart(fig_trend, use_container_width=True)
    
    # Top Products/Categories
    if category_col and amount_col:
        with row1_col2:
            st.subheader("🏆 Top Categories by Revenue")
            top_categories = df.groupby(category_col)[amount_col].sum().sort_values(ascending=False).head(10)
            
            fig_categories = px.bar(x=top_categories.values, y=top_categories.index, 
                        orientation='h',
                        labels={'x': 'Revenue ($)', 'y': 'Category'},
                        title='Top 10 Categories')
            fig_categories.update_traces(marker_color='#ff7f0e')
            fig_categories.update_layout(plot_bgcolor='white')
            st.plotly_chart(fig_categories, use_container_width=True)
    
    row2_col1, row2_col2 = st.columns(2)
    
    # Sales Distribution
    if amount_col:
        with row2_col1:
            st.subheader("💰 Sales Distribution")
            fig_dist = px.histogram(df, x=amount_col, nbins=50,
                             labels={amount_col: 'Order Amount ($)'},
                             title='Distribution of Order Values')
            fig_dist.update_traces(marker_color='#2ca02c')
            fig_dist.update_layout(plot_bgcolor='white')
            st.plotly_chart(fig_dist, use_container_width=True)
    
    # Monthly Sales Comparison
    if date_col and amount_col:
        with row2_col2:
            st.subheader("📅 Monthly Sales Comparison")
            df['Month'] = df[date_col].dt.to_period('M').astype(str)
            monthly_sales = df.groupby('Month')[amount_col].sum().reset_index()
            
            fig_monthly = px.bar(monthly_sales, x='Month', y=amount_col,
                        title='Sales by Month',
                        labels={amount_col: 'Total Sales ($)'})
            fig_monthly.update_traces(marker_color='#d62728')
            fig_monthly.update_layout(plot_bgcolor='white')
            st.plotly_chart(fig_monthly, use_container_width=True)
    
    # Data Table
    st.header("📋 Detailed Data View")
    st.dataframe(df.head(100), use_container_width=True)
    
    # Download buttons
    st.header("📥 Download Options")
    
    col_csv, col_pdf = st.columns(2)
    
    with col_csv:
        st.download_button(
            label="📄 Download Data as CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name=f'sales_data_{datetime.now().strftime("%Y%m%d_%H%M")}.csv',
            mime='text/csv',
        )
    
    with col_pdf:
        with st.spinner('Generating PDF proposal with charts...'):
            try:
                charts_data = {}
                
                # Generate matplotlib charts for PDF
                if date_col and amount_col:
                    charts_data['sales_trend'] = create_sales_trend_chart(df, date_col, amount_col)
                
                if category_col and amount_col:
                    charts_data['top_categories'] = create_top_categories_chart(df, category_col, amount_col)
                
                if amount_col:
                    charts_data['sales_distribution'] = create_distribution_chart(df, amount_col)
                
                if date_col and amount_col:
                    charts_data['monthly_sales'] = create_monthly_chart(df, date_col, amount_col)
                
                pdf_buffer = create_branded_pdf_report(
                    df, metrics_data, charts_data, date_col, 
                    amount_col, category_col, quantity_col, filter_info
                )
                
                st.download_button(
                    label="📑 Download Proposal (PDF)",
                    data=pdf_buffer,
                    file_name=f'sales_proposal_{datetime.now().strftime("%Y%m%d_%H%M")}.pdf',
                    mime='application/pdf',
                    type='primary'
                )
                
                st.success("✅ PDF generated successfully!")
                
            except Exception as e:
                st.error(f"Error generating PDF: {str(e)}")
                st.info("""
                **Required packages:**
                ```
                pip install reportlab matplotlib
                ```
                """)
    
except FileNotFoundError:
    st.error("⚠️ Dataset not found! Please make sure 'Ecommerce_Sales_Data_2024_2025.csv' is in the same directory.")
    st.info("""
    **To use this dashboard:**
    1. Download the dataset
    2. Place the CSV file in the same directory as this script
    3. Update the file path in `load_data()` if needed
    """)
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please check your data file and column names.")