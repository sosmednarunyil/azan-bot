import os
import requests
from datetime import datetime, timedelta
import pytz

# 1. Setting Zona Waktu & Koordinat (Bandung / Cileunyi)
WIB = pytz.timezone('Asia/Jakarta')
now = datetime.now(WIB)
jam_sekarang = now.strftime("%H:%M")

# 2. Ambil Jadwal Salat dari API Aladhan (Kota Bandung)
url_api = "http://api.aladhan.com/v1/timings?latitude=-6.9175&longitude=107.6191&method=11"
response = requests.get(url_api).json()
timings = response['data']['timings']

jadwal_salat = {
    'Subuh': timings['Fajr'],
    'Zuhur': timings['Dhuhr'],
    'Asar': timings['Asr'],
    'Magrib': timings['Maghrib'],
    'Isya': timings['Isha']
}

WEBHOOK_MAKE_URL = os.environ.get("MAKE_WEBHOOK_URL")

for nama_salat, jam_salat in jadwal_salat.items():
    waktu_salat_dt = datetime.strptime(jam_salat, "%H:%M")
    
    # Atur menit sholawat: Subuh = 5 menit, Salat lain = 10 menit
    menit_sholawat = 5 if nama_salat == "Subuh" else 10
    waktu_sholawat = (waktu_salat_dt - timedelta(minutes=menit_sholawat)).strftime("%H:%M")
    
    # Atur menit iqomah: 7 menit setelah azan untuk semua salat
    waktu_iqomah = (waktu_salat_dt + timedelta(minutes=7)).strftime("%H:%M")
    
    # 1. Cek Waktu Sholawat
    if jam_sekarang == waktu_sholawat:
        print(f"Saatnya Sholawat Tarbiyah menjelang {nama_salat} (Volume 5)")
        requests.post(WEBHOOK_MAKE_URL, json={
            "tipe": "sholawat", 
            "salat": nama_salat,
            "volume": 5
        })
        break
        
    # 2. Cek Waktu Azan
    elif jam_sekarang == jam_salat:
        tipe_azan = "azanshubuh" if nama_salat == "Subuh" else "azan"
        print(f"Masuk waktu {nama_salat} -> Tipe: {tipe_azan} (Volume 5)")
        requests.post(WEBHOOK_MAKE_URL, json={
            "tipe": tipe_azan, 
            "salat": nama_salat,
            "volume": 5
        })
        break
        
    # 3. Cek Waktu Iqomah (H+7)
    elif jam_sekarang == waktu_iqomah:
        print(f"Masuk waktu Iqomah {nama_salat} (Volume 5)")
        requests.post(WEBHOOK_MAKE_URL, json={
            "tipe": "iqomah", 
            "salat": nama_salat,
            "volume": 5
        })
        break