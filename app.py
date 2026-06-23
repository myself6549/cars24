import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
import re
import json
from playwright.sync_api import sync_playwright
import os
import base64
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Cars24 Analysis Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- LOAD BACKGROUND IMAGE ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return ""

bg_img_base64 = get_base64_of_bin_file("car_background.png")
if bg_img_base64:
    bg_style_url = f"data:image/png;base64,{bg_img_base64}"
else:
    # High-quality premium bright car background fallback
    bg_style_url = "https://images.unsplash.com/photo-1494976388531-d1058494cdd8?auto=format&fit=crop&q=80&w=1920"

# --- CUSTOM CSS FOR PREMIUM LOOK & FEEL ---
st.markdown(f"""
<style>
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    /* Global Typography & Background */
    html, body, [class*="css"] {{
        font-family: 'Outfit', sans-serif;
    }}
    
    /* Bright Car-Themed Background styling */
    [data-testid="stAppViewContainer"] {{
        background-image: url("{bg_style_url}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    
    [data-testid="stHeader"] {{
        background-color: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(8px);
    }}
    
    [data-testid="stAppViewBlockContainer"] {{
        background-color: rgba(255, 255, 255, 0.55);
        padding: 3rem !important;
        border-radius: 24px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(8px);
        margin-top: 1rem;
    }}
    
    [data-testid="stSidebar"] {{
        background-color: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(0, 0, 0, 0.05);
    }}
    
    /* Sidebar Headers and Labels */
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span {{
        color: #1e293b !important;
        font-weight: 600 !important;
    }}
    
    /* Force high-contrast text color on main content for readability */
    .stMarkdown, p, span, label, li, h1, h2, h3, h4, h5, h6 {{
        color: #2c3e50 !important;
    }}
    
    /* Gradient Title */
    .gradient-text {{
        background: linear-gradient(135deg, #FF4B4B, #FF8F00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0px;
    }}
    
    .subtitle-text {{
        color: #4a5568 !important;
        font-size: 1.15rem;
        margin-bottom: 25px;
        font-weight: 500;
    }}

    /* Glassmorphism Metric Cards */
    .metric-container {{
        display: flex;
        justify-content: space-between;
        gap: 15px;
        margin-bottom: 30px;
    }}
    
    .metric-card {{
        flex: 1;
        background: rgba(255, 255, 255, 0.85);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.6);
        text-align: center;
        transition: all 0.3s ease;
    }}
    
    .metric-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(255, 75, 75, 0.15);
        border-color: rgba(255, 75, 75, 0.5);
    }}
    
    .metric-label {{
        font-size: 0.9rem;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 8px;
        font-weight: 600;
    }}
    
    .metric-value {{
        font-size: 1.8rem;
        font-weight: 800;
        color: #E63946;
    }}

    /* Tab customizations */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 24px;
        background-color: rgba(255, 255, 255, 0.5);
        padding: 8px 16px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(5px);
    }}

    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 8px;
        color: #475569;
        font-weight: 600;
        font-size: 1.05rem;
        transition: all 0.2s ease;
    }}

    .stTabs [aria-selected="true"] {{
        color: #E63946 !important;
        border-bottom-color: #E63946 !important;
        background-color: rgba(255, 255, 255, 0.4) !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- DATA PATH ---
DATA_FILE = "car_data.csv"

# --- HELPER FUNCTIONS FOR CLEANING ---
def clean_prices(price_str):
    if pd.isna(price_str):
        return np.nan
    price_str = str(price_str).lower()
    if 'account' in price_str:
        return np.nan
    # Remove symbols and convert 'lakh' to numeric value
    clean_str = price_str.replace('₹', '').replace('lakh', '').strip()
    try:
        val = float(clean_str)
        return int(val * 100000) # Convert to absolute Rupees
    except ValueError:
        return np.nan

@st.cache_data(show_spinner=False)
def load_data(file_path):
    if not os.path.exists(file_path):
        return None
    
    df = pd.read_csv(file_path)
    
    # Replicate cleaning from the notebook
    # 1. Remove rows where price contains 'account'
    df = df[~df['Final Price'].astype(str).str.contains('account', case=False, na=False)]
    
    # 2. Clean final price to numerical Rupees
    df['Final Price Cleaned'] = df['Final Price'].apply(clean_prices)
    df = df.dropna(subset=['Final Price Cleaned'])
    df['Final Price Cleaned'] = df['Final Price Cleaned'].astype(int)
    
    # 3. Clean Kilometer values (ensure numeric)
    df['Kilometers'] = pd.to_numeric(df['Kilometers'], errors='coerce')
    df = df.dropna(subset=['Kilometers'])
    df['Kilometers'] = df['Kilometers'].astype(int)
    
    # 4. Extract Brand & Year
    df['Brand'] = df['Car Name'].str.split().str[1]
    df['Year'] = df['Car Name'].str.split().str[0].astype(int)
    
    # 5. Extract State Registration Code prefix (first 2 chars)
    df['State'] = df['Registration'].str[:2]
    
    return df

# Initialize session state for holding dynamic DataFrame
if "df" not in st.session_state:
    st.session_state.df = load_data(DATA_FILE)

# --- RE-LOAD DATA CONTEXT ---
def reload_dataset():
    st.session_state.df = load_data(DATA_FILE)

# --- APP LAYOUT ---
st.markdown('<p class="gradient-text">🚗 Cars24 Analytics Hub</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Explore used car market insights, analyze prices, distributions, and fetch live listings.</p>', unsafe_allow_html=True)

df = st.session_state.df

if df is None:
    st.warning("⚠️ `car_data.csv` was not found in the root directory. Please upload the file or use the Live Scraper tab to compile a new dataset.")
    # Initialize an empty dataframe structure for the UI to not break
    df = pd.DataFrame(columns=["Car Name", "Kilometers", "Fuel", "Transmission", "Registration", "EMI", "Final Price", "Location", "Final Price Cleaned", "Brand", "Year", "State"])

# --- SIDEBAR FILTERS ---
st.sidebar.header("🎯 Filter Options")

# Sidebar - Brand filter
all_brands = sorted(df['Brand'].unique().tolist()) if not df.empty else []
selected_brands = st.sidebar.multiselect("Select Brands", all_brands, default=all_brands[:10] if len(all_brands) > 10 else all_brands)

# Sidebar - Fuel filter
all_fuels = sorted(df['Fuel'].unique().tolist()) if not df.empty else []
selected_fuels = st.sidebar.multiselect("Select Fuel Type", all_fuels, default=all_fuels)

# Sidebar - Transmission filter
all_trans = sorted(df['Transmission'].unique().tolist()) if not df.empty else []
selected_trans = st.sidebar.multiselect("Select Transmission", all_trans, default=all_trans)

# Sidebar - Year filter
min_year, max_year = (int(df['Year'].min()), int(df['Year'].max())) if not df.empty else (2010, 2026)
selected_years = st.sidebar.slider("Manufacturing Year Range", min_year, max_year, (min_year, max_year))

# Sidebar - Budget slider (in Lakhs for user friendliness)
max_price_lakhs = float(df['Final Price Cleaned'].max() / 100000) if not df.empty else 25.0
min_price_lakhs = float(df['Final Price Cleaned'].min() / 100000) if not df.empty else 0.5
selected_budget = st.sidebar.slider("Budget (₹ in Lakhs)", min_price_lakhs, max_price_lakhs, (min_price_lakhs, max_price_lakhs))

# Sidebar - Reset button
if st.sidebar.button("🔄 Reset Filters"):
    st.rerun()

# Apply filters
if not df.empty:
    filtered_df = df[
        (df['Brand'].isin(selected_brands if selected_brands else all_brands)) &
        (df['Fuel'].isin(selected_fuels if selected_fuels else all_fuels)) &
        (df['Transmission'].isin(selected_trans if selected_trans else all_trans)) &
        (df['Year'].between(selected_years[0], selected_years[1])) &
        ((df['Final Price Cleaned'] / 100000).between(selected_budget[0], selected_budget[1]))
    ]
else:
    filtered_df = df.copy()

# --- TABS LAYOUT ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Dashboard Overview", 
    "🔍 Explore Dataset", 
    "📈 Deep-Dive EDA Plots", 
    "⚡ Live Web Scraper"
])

# ================= TAB 1: DASHBOARD OVERVIEW =================
with tab1:
    if filtered_df.empty:
        st.info("No records match the current filter selection. Please adjust your filters in the sidebar.")
    else:
        # Calculate dynamic metrics
        total_cars = len(filtered_df)
        avg_price = filtered_df['Final Price Cleaned'].mean() / 100000  # in Lakhs
        avg_km = filtered_df['Kilometers'].mean()
        popular_brand = filtered_df['Brand'].mode()[0] if not filtered_df['Brand'].empty else "N/A"
        
        # Display custom metrics
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-card">
                <div class="metric-label">Total Listings</div>
                <div class="metric-value">{total_cars}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Price (Lakhs)</div>
                <div class="metric-value">₹ {avg_price:.2f}L</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Distance Driven</div>
                <div class="metric-value">{int(avg_km):,} km</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Top Brand</div>
                <div class="metric-value">{popular_brand}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏢 Top Brands by Listings")
            brand_counts = filtered_df['Brand'].value_counts().head(10).reset_index()
            brand_counts.columns = ['Brand', 'Listings']
            fig_brands = px.bar(
                brand_counts, 
                x='Listings', 
                y='Brand', 
                orientation='h',
                color='Listings',
                color_continuous_scale='Sunsetdark',
                text='Listings'
            )
            fig_brands.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False, height=350)
            st.plotly_chart(fig_brands, use_container_width=True)
            
        with col2:
            st.subheader("⛽ Fuel Type Distribution")
            fuel_counts = filtered_df['Fuel'].value_counts().reset_index()
            fuel_counts.columns = ['Fuel Type', 'Count']
            fig_fuel = px.pie(
                fuel_counts, 
                values='Count', 
                names='Fuel Type', 
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Sunsetdark
            )
            fig_fuel.update_layout(height=350)
            st.plotly_chart(fig_fuel, use_container_width=True)
            
        # Recent listings block
        st.subheader("📋 Preview Filtered Listings")
        st.dataframe(
            filtered_df[['Car Name', 'Year', 'Brand', 'Kilometers', 'Fuel', 'Transmission', 'Final Price', 'Location']].head(10),
            use_container_width=True
        )

# ================= TAB 2: EXPLORE DATASET =================
with tab2:
    st.subheader("🕵️ Search and Filter Car Database")
    
    # Search box
    search_query = st.text_input("🔍 Search model name (e.g. Swift, Grand i10, Wagon R)", "")
    
    search_df = filtered_df
    if search_query:
        search_df = filtered_df[filtered_df['Car Name'].str.contains(search_query, case=False, na=False)]
        
    st.markdown(f"Showing **{len(search_df)}** match(es) of total **{len(df)}** listings.")
    
    # Display table
    st.dataframe(
        search_df.drop(columns=['Final PriceCleaned'], errors='ignore'),
        use_container_width=True
    )
    
    # Download Button
    csv_data = search_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download current selection as CSV",
        data=csv_data,
        file_name="cars24_filtered_data.csv",
        mime="text/csv"
    )

# ================= TAB 3: DEEP-DIVE EDA VISUALIZATIONS =================
with tab3:
    if filtered_df.empty:
        st.info("Please select filter options to render analysis plots.")
    else:
        st.subheader("📊 Interactive Exploratory Analysis Plots")
        
        viz_opt = st.selectbox("Select Plot to View", [
            "Price Distribution",
            "Odometer Mileage vs Price Relationship",
            "Average Selling Price over Manufacture Years",
            "Top 10 Car Models by Resale Median Price"
        ])
        
        if viz_opt == "Price Distribution":
            st.markdown("#### Distribution of Used Car Prices")
            num_bins = st.slider("Select number of bins", 5, 50, 20)
            fig = px.histogram(
                filtered_df, 
                x=filtered_df['Final Price Cleaned'] / 100000, 
                nbins=num_bins,
                labels={'x': 'Price (in ₹ Lakhs)'},
                color_discrete_sequence=['#FF4B4B'],
                opacity=0.85,
                marginal='box'
            )
            fig.update_layout(
                xaxis_title="Price (in ₹ Lakhs)",
                yaxis_title="Count of Listings",
                bargap=0.05
            )
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_opt == "Odometer Mileage vs Price Relationship":
            st.markdown("#### Mileage (km) vs Price Relationship")
            fig = px.scatter(
                filtered_df,
                x='Kilometers',
                y=filtered_df['Final Price Cleaned'] / 100000,
                color='Fuel',
                size='Year',
                hover_name='Car Name',
                labels={'y': 'Price (in ₹ Lakhs)', 'Kilometers': 'Odometer Mileage (km)'},
                color_discrete_sequence=px.colors.qualitative.Prism,
                opacity=0.75
            )
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_opt == "Average Selling Price over Manufacture Years":
            st.markdown("#### Average Resale Price Trend by Vehicle Age")
            year_trend = filtered_df.groupby('Year')['Final Price Cleaned'].mean().reset_index()
            year_trend['Price (Lakhs)'] = year_trend['Final Price Cleaned'] / 100000
            
            fig = px.line(
                year_trend,
                x='Year',
                y='Price (Lakhs)',
                markers=True,
                labels={'Year': 'Manufacture Year', 'Price (Lakhs)': 'Mean Price (₹ Lakhs)'},
                color_discrete_sequence=['#FF8F00']
            )
            fig.update_layout(xaxis=dict(tickmode='linear', tick0=min_year, dtick=1))
            st.plotly_chart(fig, use_container_width=True)
            
        elif viz_opt == "Top 10 Car Models by Resale Median Price":
            st.markdown("#### High-Value Car Configurations (Top 10 Models by Median Price)")
            top_models = filtered_df.groupby('Car Name')['Final Price Cleaned'].median().reset_index()
            top_models['Price (Lakhs)'] = top_models['Final Price Cleaned'] / 100000
            top_models = top_models.sort_values(by='Price (Lakhs)', ascending=False).head(10)
            
            fig = px.bar(
                top_models,
                x='Price (Lakhs)',
                y='Car Name',
                orientation='h',
                color='Price (Lakhs)',
                color_continuous_scale='Viridis',
                text='Price (Lakhs)'
            )
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

# ================= TAB 4: LIVE WEB SCRAPER =================

with tab4:

    st.subheader("⚡ Cars24 Browser Scraper")


    city_mapping = {
        "Delhi NCR":2,
        "Mumbai":100,
        "Bangalore":470,
        "Chennai":570,
        "Hyderabad":360,
        "Pune":242,
        "Kolkata":132,
        "Ahmedabad":5
    }


    city = st.selectbox(
        "City",
        list(city_mapping.keys())
    )


    pages = st.slider(
        "Pages",
        1,
        5,
        2
    )


    if st.button("🚀 Start Scraper"):


        scraped=[]


        progress=st.progress(0)


        with sync_playwright() as p:


            browser=p.chromium.launch(
                headless=True
                args=[
                     "--no-sandbox",
                     "--disable-dev-shm-usage",
                    "--disable-gpu"
                ]
            )


            page=browser.new_page(
                user_agent=
                "Mozilla/5.0 Chrome/120"
            )


            for pg in range(1,pages+1):


                url=(

                "https://www.cars24.com/buy-used-car/"

                f"?sort=bestmatch"
                f"&storeCityId={city_mapping[city]}"
                f"&page={pg}"

                )


                st.write(
                "Loading page",
                pg
                )


                page.goto(
                    url,
                    wait_until="networkidle",
                    timeout=60000
                )


                page.wait_for_timeout(
                    5000
                )


                cards=page.locator(
                    "a"
                ).all()



                for c in cards:


                    try:

                        txt=c.inner_text()


                        if (
                        "₹" in txt
                        and
                        "km" in txt.lower()
                        ):


                            lines=txt.split("\n")


                            scraped.append({

                            "Car Name":
                            lines[0],


                            "Kilometers":

                            next(
                            (
                            x for x in lines
                            if "km" in x.lower()
                            ),
                            "N/A"
                            ),


                            "Fuel":

                            next(
                            (
                            x for x in lines
                            if x in
                            [
                            "Petrol",
                            "Diesel",
                            "CNG"
                            ]
                            ),
                            "N/A"
                            ),


                            "Transmission":

                            next(
                            (
                            x for x in lines
                            if x in
                            [
                            "Manual",
                            "Automatic"
                            ]
                            ),
                            "N/A"
                            ),


                            "Registration":
                            "N/A",


                            "EMI":
                            "N/A",


                            "Final Price":

                            next(
                            (
                            x for x in lines
                            if "₹" in x
                            ),
                            "N/A"
                            ),


                            "Location":
                            city

                            })


                    except:

                        pass



                progress.progress(
                    pg/pages
                )


            browser.close()



        if scraped:


            st.session_state.scraped_df=pd.DataFrame(
                scraped
            )


            st.success(
            f"{len(scraped)} cars scraped"
            )


        else:


            st.error(
            "No cars found. Cars24 changed UI."
            )



    if "scraped_df" in st.session_state:


        st.dataframe(
            st.session_state.scraped_df,
            use_container_width=True
        )
