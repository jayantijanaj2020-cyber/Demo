import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="Corporate Business Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. MOCK DATA GENERATOR (Simulating Company ERP/CRM Data)
@st.cache_data
def load_data():
    np.random.seed(42)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    regions = ['North America', 'Europe', 'Asia-Pacific', 'Latin America']
    departments = ['Enterprise Corporate', 'Mid-Market', 'SMB', 'Public Sector']
    products = ['Cloud Suite Pro', 'AI Analytics Core', 'CyberSecurity Edge', 'IoT Connect']
    
    data = []
    for date in date_range:
        # Generate 2-5 transactions per day
        for _ in range(np.random.randint(2, 6)):
            revenue = np.random.uniform(500, 15000)
            # COGS (Cost of Goods Sold) roughly 30-50% of revenue
            cogs = revenue * np.random.uniform(0.3, 0.5)
            
            data.append({
                "Date": date,
                "Region": np.random.choice(regions),
                "Segment": np.random.choice(departments),
                "Product": np.random.choice(products),
                "Revenue": round(revenue, 2),
                "COGS": round(cogs, 2),
                "Profit": round(revenue - cogs, 2),
                "New_Customers": np.random.randint(0, 4)
            })
            
    df = pd.DataFrame(data)
    return df

df_raw = load_data()

# 3. SIDEBAR FILTERS
st.sidebar.header("🔍 Global Dashboard Filters")

# Date Filter
min_date = df_raw['Date'].min().to_pydatetime()
max_date = df_raw['Date'].max().to_pydatetime()
start_filter, end_filter = st.sidebar.date_input(
    "Select Date Range",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Multi-select filters
regions_selected = st.sidebar.multiselect("Select Region", options=df_raw['Region'].unique(), default=df_raw['Region'].unique())
segments_selected = st.sidebar.multiselect("Select Market Segment", options=df_raw['Segment'].unique(), default=df_raw['Segment'].unique())
products_selected = st.sidebar.multiselect("Select Product Line", options=df_raw['Product'].unique(), default=df_raw['Product'].unique())

# Apply filters to data
mask = (
    (df_raw['Date'] >= pd.to_datetime(start_filter)) & 
    (df_raw['Date'] <= pd.to_datetime(end_filter)) &
    (df_raw['Region'].isin(regions_selected)) &
    (df_raw['Segment'].isin(segments_selected)) &
    (df_raw['Product'].isin(products_selected))
)
df = df_raw.loc[mask]

# 4. MAIN BODY HEADER
st.title("📊 Corporate Business Performance Dashboard")
st.markdown("Real-time executive insights into revenue, profitability, and market segments.")
st.markdown("---")

# 5. KPI METRICS ROW
if not df.empty:
    total_revenue = df['Revenue'].sum()
    total_profit = df['Profit'].sum()
    gross_margin = (total_profit / total_revenue) * 100 if total_revenue > 0 else 0
    total_customers = df['New_Customers'].sum()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Revenue", value=f"${total_revenue:,.2f}", delta=f"+5.4% vs Last Q")
    with col2:
        st.metric(label="Net Profit", value=f"${total_profit:,.2f}", delta=f"+3.2% vs Last Q")
    with col3:
        st.metric(label="Gross Margin %", value=f"{gross_margin:.1f}%", delta="0.8% MoM")
    with col4:
        st.metric(label="New Enterprise Clients", value=f"{total_customers:,}", delta="+12% YoY")
else:
    st.warning("⚠️ No data available for the selected filters. Please adjust your sidebar settings.")

st.markdown("---")

# 6. CHARTS & VISUALIZATIONS SECTION
if not df.empty:
    left_col, right_col = st.columns(2)
    
    with left_col:
        # Chart 1: Revenue & Profit Trend Over Time (Monthly)
        st.subheader("📈 Financial Performance Trend")
        df_trend = df.groupby(df['Date'].dt.to_period('M')).agg({'Revenue': 'sum', 'Profit': 'sum'}).reset_index()
        df_trend['Date'] = df_trend['Date'].astype(str)
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(x=df_trend['Date'], y=df_trend['Revenue'], name='Revenue', mode='lines+markers', line=dict(color='#00CC96', width=3)))
        fig_trend.add_trace(go.Bar(x=df_trend['Date'], y=df_trend['Profit'], name='Net Profit', marker_color='#636EFA', opacity=0.7))
        fig_trend.update_layout(xaxis_title="Month", yaxis_title="USD ($)", legend_orientation="h", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_trend, use_container_width=True)

        # Chart 2: Revenue Distribution by Market Segment
        st.subheader("🏢 Revenue Share by Market Segment")
        fig_pie = px.pie(df, values='Revenue', names='Segment', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_pie.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_pie, use_container_width=True)

    with right_col:
        # Chart 3: Product Line Performance (Horizontal Bar Chart)
        st.subheader("📦 Revenue & Profitability by Product Line")
        df_product = df.groupby('Product').agg({'Revenue': 'sum', 'Profit': 'sum'}).reset_index().sort_values(by='Revenue', ascending=True)
        
        fig_product = go.Figure()
        fig_product.add_trace(go.Bar(y=df_product['Product'], x=df_product['Revenue'], name='Total Revenue', orientation='h', marker_color='#00b4d8'))
        fig_product.add_trace(go.Bar(y=df_product['Product'], x=df_product['Profit'], name='Net Profit', orientation='h', marker_color='#0077b6'))
        fig_product.update_layout(bmode='group', xaxis_title="USD ($)", margin=dict(l=20, r=20, t=30, b=20), legend_orientation="h")
        st.plotly_chart(fig_product, use_container_width=True)

        # Chart 4: Regional Analysis Heatmap / Matrix
        st.subheader("🌍 Regional Profitability Breakdown")
        df_region = df.groupby(['Region', 'Segment']).agg({'Profit': 'sum'}).reset_index()
        df_pivot = df_region.pivot(index='Region', columns='Segment', values='Profit').fillna(0)
        
        fig_heatmap = px.imshow(df_pivot, text_auto='.2s', aspect="auto", color_continuous_scale='Viridis', labels=dict(x="Market Segment", y="Geographic Region", color="Profit ($)"))
        fig_heatmap.update_layout(margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig_heatmap, use_container_width=True)

    st.markdown("---")

    # 7. RAW DATA / DATA EXPLORER SECTION
    with st.expander("📂 View & Download Filtered Raw Transactional Data"):
        st.dataframe(df, use_container_width=True)
        # Add a download button for CSV export
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Data as CSV",
            data=csv,
            file_name=f"business_analysis_extract_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )