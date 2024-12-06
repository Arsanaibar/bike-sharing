import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import os
from matplotlib.colors import Normalize

def load_data():
    file_path_day = os.path.join(os.getcwd(), 'day.csv')
    file_path_hour = os.path.join(os.getcwd(), 'hour.csv')
    day_df = pd.read_csv(file_path_day)
    hour_df = pd.read_csv(file_path_hour)
    return day_df, hour_df

def plot_weather_rentals(day_df):
    weather_group = day_df.groupby('weathersit')['cnt'].mean()
    colors = ["#FF6347", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

    fig, ax = plt.subplots()
    sns.barplot(x=weather_group.index, y=weather_group.values, palette=colors, ax=ax)
    ax.set_title('Rata-rata Penyewaan Berdasarkan Kondisi Cuaca')
    ax.set_ylabel('Rata-rata Penyewaan')
    ax.set_xticks(ticks=[0, 1, 2])
    ax.set_xticklabels(["Cerah/Berawan", "Berkabut/Mendung", "Hujan Ringan/Salju"])
    st.pyplot(fig)

    st.markdown("### Rangkuman Cuaca:")
    max_weather = weather_group.idxmax()
    max_value = weather_group.max()
    st.markdown(f"**Cuaca {max_weather}** memiliki rata-rata penyewaan tertinggi yaitu **{max_value:.0f}** sepeda/hari.")
    
def plot_monthly_rentals(day_df):
    monthly_group = day_df.groupby('mnth')['cnt'].sum()  
    values = monthly_group.values
    labels = monthly_group.index

    bulan_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    labels = [bulan_order[int(label) - 1] for label in labels]

    sorted_indices = [bulan_order.index(label) for label in labels]
    values = np.array(values)[np.argsort(sorted_indices)]
    labels = np.array(labels)[np.argsort(sorted_indices)]

    norm = Normalize(vmin=min(values), vmax=max(values))
    colors = plt.cm.Reds(norm(values))

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(labels, values, color=colors)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5000, f'{value:,}', ha='center', fontsize=9)

    ax.set_title("Total Penyewaan Berdasarkan Bulan")
    ax.set_xlabel("Bulan")
    ax.set_ylabel("Total Penyewaan")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)

    max_month = monthly_group.idxmax()
    max_value = monthly_group.max()
    st.markdown("### Rangkuman Bulan:")
    st.markdown(f"Penyewaan tertinggi terjadi pada **bulan {bulan_order[max_month-1]}** dengan total penyewaan sebanyak **{max_value:,} sepeda**.")

def plot_hour_weekday_rentals(hour_df):
    hour_weekday_pivot = hour_df.pivot_table(values='cnt', index='hr', columns='weekday', aggfunc='sum')

    fig, ax = plt.subplots(figsize=(10, 6))
    days = ["Minggu", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
    colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink']

    for i, day in enumerate(days):
        ax.plot(hour_weekday_pivot.index, hour_weekday_pivot[hour_weekday_pivot.columns[i]],
                 label=day, color=colors[i], linewidth=2)

    ax.set_title("Total Penyewaan Berdasarkan Hari dan Jam")
    ax.set_xlabel("Jam (0-23)")
    ax.set_ylabel("Total Penyewaan")
    ax.set_xticks(range(0, 24))
    ax.legend(title="Hari", bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)

    max_hour = hour_weekday_pivot.max().max()
    st.markdown("### Rangkuman Jam dan Hari:")
    st.markdown(f"Penyewaan tertinggi terjadi pada **jam {hour_weekday_pivot.stack().idxmax()[0]}** pada **hari {days[hour_weekday_pivot.stack().idxmax()[1]]}** dengan total penyewaan sebanyak **{max_hour:,} sepeda**.")

def plot_time_weather_rentals(hour_df):
    def time_of_day(hour):
        if 6 <= hour < 10:
            return "Pagi"
        elif 10 <= hour < 16:
            return "Siang"
        elif 16 <= hour < 20:
            return "Sore"
        else:
            return "Malam"

    hour_df['time_category'] = hour_df['hr'].apply(time_of_day)

    def weather_category(weather):
        if weather == 1:
            return "Cerah/Mendung Ringan"
        elif weather == 2:
            return "Mendung Kabut Ringan"
        elif weather == 3:
            return "Hujan Ringan/Salju"
        else:
            return "Cuaca Buruk Ekstrem"

    hour_df['weather_category'] = hour_df['weathersit'].apply(weather_category)

    time_weather_group = hour_df.groupby(['time_category', 'weather_category'])['cnt'].mean().unstack()

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(time_weather_group, cmap="Reds", annot=True, fmt=".0f", cbar=True, ax=ax)
    ax.set_title("Rata-rata Penyewaan Berdasarkan Kategori Waktu dan Cuaca")
    ax.set_xlabel("Kondisi Cuaca")
    ax.set_ylabel("Kategori Waktu")
    st.pyplot(fig)

    stacked = time_weather_group.stack()
    max_value = stacked.max()  
    max_time_category, max_weather_category = stacked.idxmax() 

    st.markdown("### Rangkuman Waktu dan Cuaca:")
    st.markdown(f"Penyewaan tertinggi terjadi pada **kategori waktu {max_time_category}** dengan cuaca **{max_weather_category}**.")
    st.markdown(f"Total penyewaan tertinggi pada kategori tersebut adalah **{max_value:.0f} sepeda**.")

def main():
    day_df, hour_df = load_data()  
    st.title("Dashboard Penyewaan Sepeda")
    tab = st.selectbox("Pilih Visualisasi:", ["Kondisi Cuaca", "Penyewaan Berdasarkan Bulan", 
                                              "Penyewaan Berdasarkan Hari dan Jam", "Penyewaan Berdasarkan Waktu dan Cuaca"])

    if tab == "Kondisi Cuaca":
        plot_weather_rentals(day_df)
    elif tab == "Penyewaan Berdasarkan Bulan":
        plot_monthly_rentals(day_df)
    elif tab == "Penyewaan Berdasarkan Hari dan Jam":
        plot_hour_weekday_rentals(hour_df)
    elif tab == "Penyewaan Berdasarkan Waktu dan Cuaca":
        plot_time_weather_rentals(hour_df)

if __name__ == "__main__":
    main()
