
import streamlit as st
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import re
import os
import time

st.set_page_config(page_title="Cars24 Analytics Dashboard", page_icon="🚗", layout="wide")

DATA_FILE = "car_data.csv"


def clean_prices(x):
    if pd.isna(x):
        return np.nan
    x = str(x).lower().replace("₹","").replace("lakh","").strip()
    try:
        return int(float(x)*100000)
    except:
        return np.nan


@st.cache_data
def load_data():
    if not os.path.exists(DATA_FILE):
        return pd.DataFrame()

    df = pd.read_csv(DATA_FILE)

    df["Final Price Cleaned"] = df["Final Price"].apply(clean_prices)
    df["Kilometers"] = pd.to_numeric(df["Kilometers"], errors="coerce")

    df.dropna(inplace=True)

    df["Brand"] = df["Car Name"].str.split().str[1]
    df["Year"] = df["Car Name"].str[:4].astype(int)

    return df


def scrape_cars24(city_id, pages):

    session = requests.Session()

    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    session.headers.update(headers)

    results = []

    for page in range(1,pages+1):

        url = (
        "https://www.cars24.com/buy-used-car/"
        f"?storeCityId={city_id}&page={page}"
        )

        r = session.get(url,timeout=20)

        soup = BeautifulSoup(r.text,"html.parser")


        cards = soup.find_all(
            lambda x:
            x.name in ["div","a"]
            and "card" in " ".join(x.get("class",[])).lower()
        )


        if not cards:
            cards = soup.find_all(
                "a",
                href=re.compile("/buy-used-car")
            )


        for card in cards:

            text = card.get_text(" ",strip=True)

            year = re.search(r"\b20\d{2}\b",text)

            price = re.search(
                r"₹?\s?[\d.]+\s?lakh",
                text,
                re.I
            )


            km = re.search(
                r"[\d,]+\s?km",
                text,
                re.I
            )


            if year and price:

                results.append({

                "Car Name": text[:80],
                "Kilometers":
                km.group()
                if km else "0",

                "Fuel":"N/A",
                "Transmission":"N/A",
                "Registration":"N/A",
                "EMI":"N/A",

                "Final Price":
                price.group(),

                "Location":"Cars24"

                })


        time.sleep(1)


    return pd.DataFrame(results)



df = load_data()


st.title("🚗 Cars24 Analytics Dashboard")


if not df.empty:

    c1,c2,c3 = st.columns(3)

    c1.metric(
        "Cars",
        len(df)
    )

    c2.metric(
        "Average Price",
        f"₹{df['Final Price Cleaned'].mean()/100000:.2f} L"
    )

    c3.metric(
        "Average KM",
        int(df["Kilometers"].mean())
    )


    st.dataframe(df,use_container_width=True)

else:
    st.warning(
    "car_data.csv not found"
    )



tab1,tab2 = st.tabs(
[
"📊 Dashboard",
"⚡ Live Scraper"
]
)



with tab1:

    if not df.empty:

        st.bar_chart(
        df["Brand"].value_counts()
        )



with tab2:


    st.subheader(
    "Cars24 Live Scraper"
    )


    city = st.number_input(
    "City ID",
    value=2
    )

    pages = st.slider(
    "Pages",
    1,5,2
    )


    if st.button(
    "Start Scraping"
    ):

        data = scrape_cars24(
            city,
            pages
        )

        if data.empty:

            st.error(
            "No listings found. Cars24 may have changed or blocked requests."
            )

        else:

            st.success(
            f"{len(data)} cars scraped"
            )

            st.dataframe(data)

            if st.button("Save CSV"):

                data.to_csv(
                DATA_FILE,
                index=False
                )

                st.success(
                "Saved"
                )
