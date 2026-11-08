import os
import requests
from datetime import datetime, timedelta
import pytz

# Konfigurasi Lokasi (Bandung / Cileunyi)
LATITUDE = "-6.93"
LONGITUDE = "107.72"
TIMEZONE = "Asia/Jakarta"

# Ambil URL Webhook dari GitHub Secrets
MAKE_WEBHOOK_URL = os.environ.get("MAKE_WEBHOOK_URL")

def get_prayer_times():
    url = f"http://api.aladhan.com/v1/timings?latitude={LATITUDE}&longitude={LONGITUDE}&method=2"
    try:
        res = requests.get(url, timeout=10).json()
        return res['data']['timings']
    except Exception as e:
        print(f"Error fetch jadwal salat: {e}")
        return None

def check_and_send():
    if not MAKE_WEBHOOK_URL:
        print("MAKE_WEBHOOK_URL tidak dikonfigurasi!")
        return

    tz = pytz.timezone(TIMEZONE)
    now = datetime.now(tz)
    current_time_str = now.strftime("%H:%M")
    
    timings = get_prayer_times()
    if not timings:
        return

    prayers = {
        "Fajr": "Subuh",
        "Dhuhr": "Zuhur",
        "Asr": "Asar",
        "Maghrib": "Magrib",
        "Isha": "Isya"
    }

    for p_eng, p_indo in prayers.items():
        p_time_str = timings[p_eng]
        p_time = datetime.strptime(p_time_str, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
        p_time = tz.localize(p_time)

        # 1. Cek Sholawat Tarbiyah (H-5 Subuh, H-10 Salat Lainnya)
        offset_sholawat = 5 if p_eng == "Fajr" else 10
        sholawat_time = p_time - timedelta(minutes=offset_sholawat)
        if sholawat_time.strftime("%H:%M") == current_time_str:
            payload = {"salat": p_indo, "tipe": "sholawat", "volume": 5}
            requests.post(MAKE_WEBHOOK_URL, json=payload)
            print(f"Sent Sholawat for {p_indo}")
            return

        # 2. Cek Waktu Azan (H-0)
        if p_time.strftime("%H:%M") == current_time_str:
            tipe_azan = "azanshubuh" if p_eng == "Fajr" else "azan"
            payload = {"salat": p_indo, "tipe": tipe_azan, "volume": 5}
            requests.post(MAKE_WEBHOOK_URL, json=payload)
            print(f"Sent Azan ({tipe_azan}) for {p_indo}")
            return

        # 3. Cek Waktu Iqomah (H+7)
        iqomah_time = p_time + timedelta(minutes=7)
        if iqomah_time.strftime("%H:%M") == current_time_str:
            payload = {"salat": p_indo, "tipe": "iqomah", "volume": 5}
            requests.post(MAKE_WEBHOOK_URL, json=payload)
            print(f"Sent Iqomah for {p_indo}")
            return

if __name__ == "__main__":
    check_and_send()
