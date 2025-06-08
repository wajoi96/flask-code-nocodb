from flask import Flask, jsonify, request
import requests
import urllib.parse  # Untuk URL encoding
import json

app = Flask(__name__)

# --- KONFIGURASI PENTING ---
BASE_URL = "https://app.nocodb.com"
TABLE_ID = "mgcg430t15let75"
VIEW_ID = "vw03jsmpyql7yd43"
NOCO_API_KEY = "8xJwzMGsZTlhm4i-PBEkvz7Z0CFdOssqSGgAr2rG"  # API token anda

HEADERS = {
    "xc-token": NOCO_API_KEY,
    "accept": "application/json",
    "Content-Type": "application/json"
}

# --- ENDPOINT ROOT ---
@app.route('/')
def index():
    return "✅ Server Flask sedang berjalan!"

# --- ENDPOINT UPDATE SENTIMEN ---
@app.route('/update-sentimen', methods=['POST'])
def webhook_sentimen():
    data = request.json
    print("=" * 80)
    print(f"[INFO] Webhook diterima: {json.dumps(data, indent=2)}")

    pair = data.get("pair")
    new_sentimen = data.get("sentimen")

    if pair and new_sentimen:
        success, message = update_sentimen_in_nocodb(pair, new_sentimen)
        if success:
            print(f"[INFO] ✅ STATUS: BERJAYA | {message}")
            print("=" * 80)
            return jsonify({"status": "Berjaya", "message": message}), 200
        else:
            print(f"[INFO] ❌ STATUS: GAGAL | {message}")
            print("=" * 80)
            return jsonify({"status": "Gagal", "error": message}), 500
    else:
        error_msg = "Data 'pair' atau 'sentimen' tidak lengkap."
        print(f"[INFO] ❌ STATUS: GAGAL | {error_msg}")
        print("=" * 80)
        return jsonify({"error": error_msg}), 400

# --- FUNGSI UTAMA ---
def update_sentimen_in_nocodb(pair, new_sentimen):
    print(f"[INFO] Proses kemas kini untuk pair='{pair}' kepada sentimen='{new_sentimen}'")

    # --- LANGKAH 1: Cari rekod ---
    encoded_pair = urllib.parse.quote(pair)
    search_url = f"{BASE_URL}/api/v2/tables/{TABLE_ID}/records?where=(pair,eq,{encoded_pair})&viewId={VIEW_ID}"
    print(f"[INFO] GET URL: {search_url}")

    try:
        response_get = requests.get(search_url, headers=HEADERS)
        response_get.raise_for_status()

        records_list = response_get.json().get("list")
        total_found = len(records_list) if records_list else 0
        print(f"[INFO] Jumlah rekod ditemui: {total_found}")

        if not records_list:
            message = f"Tiada rekod ditemui untuk pair: {pair}. Kemas kini tidak dilakukan."
            print(f"[GAGAL] {message}")
            return False, message

        # Ambil 'Id' dari rekod pertama
        row_id = records_list[0].get("Id")
        if not row_id:
            message = "Rekod ditemui tetapi tiada 'Id'. Kemas kini tidak dapat dilakukan."
            print(f"[GAGAL] {message}")
            return False, message

        print(f"[INFO] Rekod ditemui: Id={row_id} untuk pair={pair}")

        # --- LANGKAH 2: BULK-UPDATE ---
        patch_url = f"{BASE_URL}/api/v2/tables/{TABLE_ID}/records/bulk-update"
        payload = {
            "records": [{
                "Id": row_id,
                "sentimen": new_sentimen
            }]
        }

        print(f"[INFO] POST (bulk-update) ke {patch_url}")
        print(f"[INFO] Payload dihantar:\n{json.dumps(payload, indent=2)}")

        response_patch = requests.post(patch_url, headers=HEADERS, json=payload)
        response_patch.raise_for_status()

        response_data = response_patch.json()
        print(f"[INFO] Response dari NocoDB:\n{json.dumps(response_data, indent=2)}")

        message = f"Sentimen untuk {pair} berjaya dikemas kini kepada {new_sentimen}."
        print(f"[BERJAYA] {message}")
        return True, message

    except requests.exceptions.HTTPError as http_err:
        error_message = f"Ralat HTTP: {http_err} | Respons: {http_err.response.text}"
        print(f"[GAGAL] {error_message}")
        return False, error_message

    except requests.exceptions.RequestException as e:
        error_message = f"Ralat Rangkaian: {e}"
        print(f"[GAGAL] {error_message}")
        return False, error_message

# --- RUN APP ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
