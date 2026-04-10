import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="amazon analysis", layout="wide")

@st.cache_data
def load_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    data = df.copy()
    data['rating'] = df['rating'].str.replace('out of 5 stars', '').astype(float)
    data['number_of_reviews'] = df['number_of_reviews'].str.replace(',', '').astype(float)
    data['bought_in_last_month'] = df['bought_in_last_month'].str.replace('K', '000').str.extract(r'(\d+)').squeeze().astype(float)
    data['current/discounted_price'] = df['current/discounted_price'].str.extract(r'(\d+)').squeeze().astype(float)
    data['price_on_variant'] = df['price_on_variant'].str.extract(r'(\d+)').squeeze().astype(float)
    data['listed_price'] = df['listed_price'].str.extract(r'(\d+)').squeeze().astype(float)

    numeric_cols = data.select_dtypes(include='number').columns
    data[numeric_cols] = data[numeric_cols].fillna(data[numeric_cols].median())

    categories = {
        'Cell Phones & Accessories': [
            'phone', 'mobile', 'iphone', 'samsung', 'xiaomi', 'case', 'charger',
            'screen protector', 'smartphone', 'oppo', 'vivo', 'realme', 'oneplus',
            'huawei', 'sim', 'back cover', 'power bank', 'wireless charger'
        ],
        'Computers': [
            'laptop', 'computer', 'pc', 'macbook', 'notebook', 'dell', 'hp',
            'lenovo', 'asus', 'acer', 'desktop', 'chromebook', 'keyboard',
            'mouse', 'mousepad', 'cooling pad', 'laptop stand'
        ],
        'TV & Video': [
            'tv', 'television', 'monitor', 'display', '4k', 'hdmi', 'projector',
            'smart tv', 'oled', 'qled', 'fire stick', 'chromecast', 'streaming',
            'android tv', 'roku', 'screen'
        ],
        'Headphones': [
            'headphone', 'earphone', 'earbud', 'airpod', 'headset',
            'noise cancelling', 'wireless', 'wired', 'jbl', 'sony',
            'bose', 'sennheiser', 'anker'
        ],
        'Audio & Home Theater': [
            'speaker', 'audio', 'sound', 'bluetooth speaker', 'subwoofer',
            'soundbar', 'home theater', 'amplifier', 'receiver', 'bass'
        ],
        'Camera & Photo': [
            'camera', 'lens', 'tripod', 'gopro', 'dslr', 'mirrorless',
            'canon', 'nikon', 'fujifilm', 'action camera', 'drone',
            'camera bag', 'flash', 'filter', 'gimbal', 'stabilizer'
        ],
        'Wearable Technology': [
            'watch', 'fitbit', 'smartwatch', 'band', 'tracker', 'apple watch',
            'galaxy watch', 'garmin', 'mi band', 'fitness tracker',
            'heart rate', 'gps watch'
        ],
        'Video Games': [
            'gaming', 'game', 'xbox', 'playstation', 'ps5', 'ps4', 'controller',
            'joystick', 'nintendo', 'switch', 'gaming chair', 'gaming mouse',
            'gaming keyboard', 'gaming headset', 'rgb', 'console'
        ],
        'Office Electronics': [
            'printer', 'ink', 'toner', 'cartridge', 'scanner', 'epson',
            'laser printer', 'inkjet', 'shredder', 'calculator', 'label maker'
        ],
        'Software': [
            'software', 'antivirus', 'windows', 'microsoft office', 'adobe',
            'operating system', 'vpn', 'license'
        ],
        'Smart Home': [
            'smart', 'alexa', 'echo', 'wifi', 'router', 'bulb', 'plug',
            'google home', 'nest', 'ring', 'doorbell', 'security camera',
            'smart lock', 'thermostat', 'robot vacuum', 'smart switch', 'extender'
        ],
        'Storage & Networking': [
            'ssd', 'hard drive', 'usb', 'flash', 'memory', 'sd card', 'hdd',
            'nvme', 'pendrive', 'micro sd', 'seagate', 'sandisk', 'kingston',
            'modem', 'switch', 'access point', 'tp-link', 'netgear', 'cable',
            'adapter', 'hub', 'connector', 'hdmi cable', 'ethernet'
        ],
        'Musical Instruments': [
            'guitar', 'piano', 'keyboard instrument', 'drum', 'violin',
            'microphone', 'midi', 'studio', 'recording', 'bass guitar'
        ],
    }

    def product_categorie(title):
        title_lower = title.lower()
        for categorie, keywords in categories.items():
            if any(keyword in title_lower for keyword in keywords):
                return categorie
        return 'other'

    data['category'] = data['title'].apply(product_categorie)

    string_cols = data.select_dtypes(include='object').columns
    data[string_cols] = data[string_cols].fillna(data[string_cols].mode().iloc[0])

    return data


uploaded_file = st.file_uploader("Upload CSV", type="csv")

if uploaded_file is None:
    st.warning("ارفع الملف عشان يبدأ الداشبورد")
    st.stop()

data = load_data(uploaded_file)

strategy_products = data[
    (data["rating"] >= 4.0) &
    (data["number_of_reviews"] >= 1000) &
    (data["bought_in_last_month"] >= 100)
].sort_values("bought_in_last_month", ascending=False).head(20).copy()

page = st.sidebar.selectbox('page:', ["analysis", "Strategy"])

if page == "analysis":
    st.title("analysis")

    corr = data.select_dtypes(include='number').corr()
    fig2 = px.imshow(corr, text_auto=True)
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("rating and reviews and discount the vectors effect the sales")

    fig3 = px.bar(
        data.groupby("rating")["bought_in_last_month"].mean().reset_index(),
        x="rating",
        y="bought_in_last_month",
        title="Rating vs Bought in Last Month"
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("rating between 4 - 5 are the most bought products")

    fig4 = px.scatter(
        data,
        x="number_of_reviews",
        y="bought_in_last_month",
        title="Number of Reviews vs Bought in Last Month"
    )
    st.plotly_chart(fig4, use_container_width=True)
    st.markdown("the more number of review the more sales")

    fig5 = px.scatter(
        data,
        x="current/discounted_price",
        y="bought_in_last_month",
        title="current/discounted_price vs Bought in Last Month"
    )
    st.plotly_chart(fig5, use_container_width=True)
    st.markdown("the less discount you do the less sales you get")

    fig6 = px.bar(
        data[data["category"] != "other"]
            .groupby("category")["bought_in_last_month"].mean().reset_index(),
        x="category",
        y="bought_in_last_month",
        title="Category vs Bought in Last Month",
        height=600
    )
    st.plotly_chart(fig6, use_container_width=True)
    st.markdown("the most high Category sales")

elif page == "Strategy":
    st.title("Strategy")
    st.markdown("now you can do 10% discount on this products to increase the sales")

    fig7 = go.Figure(data=[go.Table(
        header=dict(
            values=["Product", "Rating", "Reviews", "Bought/Month", "Price"],
            fill_color="#4A90D9",
            font=dict(color="white", size=13),
            align="left"
        ),
        cells=dict(
            values=[
                strategy_products["title"].str[:60],
                strategy_products["rating"],
                strategy_products["number_of_reviews"],
                strategy_products["bought_in_last_month"],
                strategy_products["current/discounted_price"]
            ],
            fill_color=[["#f9f9f9", "#ffffff"] * 10],
            align="left"
        )
    )])
    fig7.update_layout(title="Top Strategy Products")
    st.plotly_chart(fig7, use_container_width=True)
