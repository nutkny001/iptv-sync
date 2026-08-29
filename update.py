import json
import requests

HOST = "http://ostvasia.xyz:80"
USERNAME = "tipu270219"
PASSWORD = "dwhtKk6Ya"
OUTPUT_LIVE_M3U = "live_only_ostvasia.m3u"

TARGET_CATEGORY_IDS = ["1624"] 

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_live_via_api():
    print("[1] กำลังยืนยันตัวตนผ่าน Xtream Codes API...")
    auth_url = f"{HOST}/player_api.php?username={USERNAME}&password={PASSWORD}"

    try:
        res = requests.get(auth_url, headers=headers, timeout=30)
        user_info = res.json()

        if user_info.get("user_info", {}).get("auth") != 1:
            print("[-] ยืนยันตัวตนไม่สำเร็จ")
            return

        # ดึงรายชื่อหมวดหมู่ทั้งหมดเพื่อแปลง ID เป็น "ชื่อหมวดหมู่"
        print("[*] กำลังดึงชื่อหมวดหมู่...")
        cat_url = f"{HOST}/player_api.php?username={USERNAME}&password={PASSWORD}&action=get_live_categories"
        cat_res = requests.get(cat_url, headers=headers, timeout=30)
        cat_data = cat_res.json()
        
        category_map = {}
        if isinstance(cat_data, list):
            for cat in cat_data:
                category_map[str(cat.get("category_id"))] = cat.get("category_name", "Sports")

        # ดึงรายชื่อช่อง
        print("[2] กำลังดึงช่องสด...")
        live_url = f"{HOST}/player_api.php?username={USERNAME}&password={PASSWORD}&action=get_live_streams"
        live_res = requests.get(live_url, headers=headers, timeout=60)
        live_data = live_res.json()

        if not isinstance(live_data, list):
            print("[-] ไม่พบข้อมูลช่อง")
            return

        epg_url = f"{HOST}/xmltv.php?username={USERNAME}&password={PASSWORD}"
        count = 0

        with open(OUTPUT_LIVE_M3U, "w", encoding="utf-8") as f:
            f.write(f'#EXTM3U url-tvg="{epg_url}"\n')

            for item in live_data:
                cat_id = str(item.get("category_id", ""))
                
                if cat_id in TARGET_CATEGORY_IDS:
                    name = item.get("name", "Unknown")
                    stream_id = item.get("stream_id")
                    
                    # ดึงชื่อหมวดหมู่ที่เป็นตัวหนังสือมาใส่ group-title
                    group_title = category_map.get(cat_id, "LIVE | MonoMax")
                    container_extension = item.get("container_extension", "ts")
                    stream_url = f"{HOST}/live/{USERNAME}/{PASSWORD}/{stream_id}.{container_extension}"

                    f.write(f'#EXTINF:-1 tvg-id="{stream_id}" group-title="{group_title}", {name}\n')
                    f.write(f"{stream_url}\n")
                    count += 1

        print(f"[✔] บันทึกสำเร็จ {count} ช่อง")

    except Exception as e:
        print(f"[-] เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    get_live_via_api()
