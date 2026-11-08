import os
import requests

# Ambil URL Webhook dari Secrets GitHub
url = os.environ.get("MAKE_WEBHOOK_URL")

print(f"Mengirim sinyal tes ke: {url}")

if url:
    payload = {"salat": "Subuh", "tipe": "azanshubuh", "volume": 5}
    response = requests.post(url, json=payload)
    print(f"Status respon: {response.status_code}")
else:
    print("URL Webhook tidak ditemukan di Secrets!")
