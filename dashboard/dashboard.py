import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os


# Tentukan path relatif ke file dataset
current_dir = os.path.dirname(__file__)  # Mendapatkan direktori saat ini
orders_df = pd.read_csv(os.path.join(current_dir, "cleaned_orders.csv"))
orderReviews_df = pd.read_csv(os.path.join(current_dir, "cleaned_order_reviews.csv"))
merged_sales_df = pd.read_csv(os.path.join(current_dir, "cleaned_merged_sales.csv"))

# Data preprocessing
orders_df['order_delivered_customer_date'] = pd.to_datetime(orders_df['order_delivered_customer_date'])
orders_df['order_estimated_delivery_date'] = pd.to_datetime(orders_df['order_estimated_delivery_date'])

# Hitung keterlambatan pengiriman
orders_df['delivery_delay'] = (orders_df['order_delivered_customer_date'] - 
                                orders_df['order_estimated_delivery_date']).dt.days
orders_df['delivery_delay'] = orders_df['delivery_delay'].apply(lambda x: max(x, 0))  # Hindari nilai negatif

# Sidebar untuk input pengguna
st.sidebar.header("Opsi Filter")

# Pertanyaan 1: Kategori Produk Paling Banyak Terjual
st.sidebar.subheader("Top Product Categories")
top_n = st.sidebar.text_input("Masukkan jumlah kategori teratas yang ingin ditampilkan:", "10")
# Dropdown untuk memilih kategori pertama
category_options = merged_sales_df['product_category_name_english'].unique().tolist()
category1 = st.sidebar.selectbox("Pilih Kategori Pertama", ["Semua Kategori"] + category_options)

# Dropdown untuk memilih kategori kedua
category2 = st.sidebar.selectbox("Pilih Kategori Kedua", ["Semua Kategori"] + category_options)

# Pertanyaan 2: Pengaruh Keterlambatan Pengiriman terhadap Skor Ulasan
st.sidebar.subheader("Pengaruh Keterlambatan Pengiriman terhadap Skor Ulasan")
min_delay, max_delay = st.sidebar.slider("Pilih Rentang Keterlambatan Pengiriman (hari)", 0, 30, (0, 30))

# Visualisasi Kategori Teratas
st.header("Top Product Categories")
if top_n.isdigit():
    top_n = int(top_n)
    category_sales = merged_sales_df['product_category_name'].value_counts().head(top_n)
    fig, ax = plt.subplots()
    sns.barplot(x=category_sales.values, y=category_sales.index, ax=ax, palette='viridis')
    plt.title(f'Top {top_n} Kategori Produk')
    st.pyplot(fig)
    
st.header("Perbandingan Dua Kategori Produk")
if category1 != "Semua Kategori" and category2 != "Semua Kategori":
    data1 = merged_sales_df[merged_sales_df['product_category_name_english'] == category1]
    data2 = merged_sales_df[merged_sales_df['product_category_name_english'] == category2]

    comparison_data = pd.DataFrame({
        'Kategori': [category1, category2],
        'Jumlah Penjualan': [data1['product_id'].count(), data2['product_id'].count()]
    })

    fig, ax = plt.subplots()
    sns.barplot(x='Jumlah Penjualan', y='Kategori', data=comparison_data, ax=ax, palette='coolwarm')
    plt.title('Perbandingan Jumlah Penjualan')
    plt.xlabel('Jumlah Penjualan')
    plt.ylabel('Kategori Produk')
    st.pyplot(fig)
else:
    st.warning("Silakan pilih dua kategori untuk perbandingan.")

# Visualisasi Pengaruh Keterlambatan Pengiriman terhadap Skor Ulasan
st.header("Pengaruh Keterlambatan Pengiriman terhadap Skor Ulasan")
filtered_orders = orders_df[(orders_df['delivery_delay'] >= min_delay) & (orders_df['delivery_delay'] <= max_delay)]
merged_reviews = filtered_orders.merge(orderReviews_df, on='order_id', how='inner')

delay_by_score = merged_reviews.groupby('review_score')['delivery_delay'].mean().reset_index()

fig, ax = plt.subplots()
sns.barplot(data=delay_by_score, x='review_score', y='delivery_delay', ax=ax, palette='coolwarm')
plt.title('Rata-rata Keterlambatan Pengiriman berdasarkan Skor Ulasan')
st.pyplot(fig)
