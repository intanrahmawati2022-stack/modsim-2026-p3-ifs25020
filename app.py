import streamlit as st
import simpy
import numpy as np
import matplotlib.pyplot as plt

# KONFIGURASI
st.set_page_config(page_title="Simulasi Piket Ompreng", layout="wide")

st.title("Simulasi Sistem Piket Ompreng")
st.write("Simulasi untuk menghitung total waktu piket hingga semua ompreng selesai.")

# SIDEBAR
st.sidebar.header("Parameter Simulasi")

total_ompreng = st.sidebar.number_input("Jumlah Ompreng", 50, 1000, 180)

mean_lauk = st.sidebar.slider("Rata-rata Waktu Lauk (detik)", 5, 60, 15)
mean_angkat = st.sidebar.slider("Rata-rata Waktu Angkat (detik)", 5, 60, 20)
mean_nasi = st.sidebar.slider("Rata-rata Waktu Nasi (detik)", 10, 90, 40)

petugas_lauk = st.sidebar.number_input("Petugas Lauk", 1, 10, 3)
petugas_angkat = st.sidebar.number_input("Petugas Angkat", 1, 10, 2)
petugas_nasi = st.sidebar.number_input("Petugas Nasi", 1, 10, 2)

# MODEL SIMULASI
def run_simulation():
    env = simpy.Environment()

    lauk = simpy.Resource(env, capacity=petugas_lauk)
    angkat = simpy.Resource(env, capacity=petugas_angkat)
    nasi = simpy.Resource(env, capacity=petugas_nasi)

    waktu_selesai = []

    def proses():
        # Lauk
        with lauk.request() as req:
            yield req
            yield env.timeout(np.random.exponential(mean_lauk))

        # Angkat
        with angkat.request() as req:
            yield req
            yield env.timeout(np.random.exponential(mean_angkat))

        # Nasi
        with nasi.request() as req:
            yield req
            yield env.timeout(np.random.exponential(mean_nasi))

        waktu_selesai.append(env.now)

    for i in range(total_ompreng):
        env.process(proses())

    env.run()
    return np.array(waktu_selesai) / 60  # konversi ke menit

# JALANKAN SIMULASI
if st.button("🚀 Jalankan Simulasi"):

    selesai_menit = run_simulation()
    total_waktu = max(selesai_menit)

    st.divider()

    col1, col2 = st.columns(2)
    col1.metric("⏱ Total Waktu Piket", f"{total_waktu:.2f} menit")
    col2.metric("👥 Total Staff", petugas_lauk + petugas_angkat + petugas_nasi)

    st.divider()

    # VISUALISASI (PINK THEME)
    col1, col2 = st.columns(2)

    # 📈 Grafik Kumulatif
    with col1:
        st.subheader("📈 Ompreng Selesai vs Waktu")
        sorted_time = np.sort(selesai_menit)
        fig1, ax1 = plt.subplots()
        ax1.plot(
            sorted_time,
            np.arange(1, len(sorted_time)+1),
            color="#ff69b4",  # hot pink
            linewidth=2
        )
        ax1.set_xlabel("Waktu (menit)")
        ax1.set_ylabel("Jumlah Ompreng Selesai")
        ax1.grid(True)
        st.pyplot(fig1)

    # 📊 Histogram
    with col2:
        st.subheader("📊 Distribusi Waktu Penyelesaian")
        fig2, ax2 = plt.subplots()
        ax2.hist(
            selesai_menit,
            bins=20,
            color="#f8c8dc",  # soft pink
            edgecolor="black"
        )
        ax2.set_xlabel("Waktu (menit)")
        ax2.set_ylabel("Frekuensi")
        ax2.grid(True)
        st.pyplot(fig2)