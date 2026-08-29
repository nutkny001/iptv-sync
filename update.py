import json
import requests

HOST = "http://ostvasia.xyz:80"
USERNAME = "tipu270219"
PASSWORD = "dwhtKk6Ya"
OUTPUT_LIVE_M3U = "live_only_ostvasia.m3u"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_live_via_api():
    print("[1] กำลังยืนยันตัวตนผ่าน Xtream Codes API...")
    auth_url = f"{HOST}/player_api.php?username={USERNAME}&password={PASSWORD}"

    try:
        res = requests.get(auth_url, headers=headers, timeout=30)
        user_info = res.json()

        auth_status = user_info.get("user_info", {}).get("auth")
        status = user_info.get("user_info", {}).get("status")

        if auth_status == 1 and status == "Active":
            print("[+] ยืนยันตัวตนสำเร็จ!")
        else:
            print("[-] บัญชีมีปัญหา หรือหมดอายุ")
            return

        print("[2] กำลังดึงรายชื่อช่องสด (Live Streams) จาก API...")
        get_live_url = f"{HOST}/player_api.php?username={USERNAME}&password={PASSWORD}&action=get_live_streams"

        res_live = requests.get(get_live_url, headers=headers, timeout=60)
        live_data = res_live.json()

        if not isinstance(live_data, list) or len(live_data) == 0:
            print("[-] ไม่พบรายการช่องสดจาก API")
            return

        print(f"[+] ค้นพบช่องทั้งหมด {len(live_data)} ช่อง กำลังกรองเฉพาะ 'LIVE | MonoMax (EPL)'...")
        epg_url = f"{HOST}/xmltv.php?username={USERNAME}&password={PASSWORD}"

        filtered_count = 0
        with open(OUTPUT_LIVE_M3U, "w", encoding="utf-8") as f:
            f.write(f'#EXTM3U url-tvg="{epg_url}"\n')

            for item in live_data:
                name = item.get("name", "").strip()
                
                # กรองเฉพาะชื่อที่ตรงกับ "LIVE | MonoMax (EPL)" เป๊ะๆ
                if name == "LIVE | MonoMax (EPL)":
                    stream_id = item.get("stream_id")
                    category_id = item.get("category_id", "")
                    container_extension = item.get("container_extension", "ts")

                    stream_url = f"{HOST}/live/{USERNAME}/{PASSWORD}/{stream_id}.{container_extension}"

                    f.write(f'#EXTINF:-1 tvg-id="{stream_id}" group-title="{category_id}", {name}\n')
                    f.write(f"{stream_url}\n")
                    filtered_count += 1

        print(f"[✔] บันทึกสำเร็จ เฉพาะช่องที่ตรงกันจำนวน {filtered_count} ช่อง")

    except Exception as e:
        print(f"[-] เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    get_live_via_api()
