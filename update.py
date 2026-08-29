import json
import requests

HOST = "http://ostvasia.xyz:80"
USERNAME = "tipu270219"
PASSWORD = "dwhtKk6Ya"
OUTPUT_LIVE_M3U = "live_only_ostvasia.m3u"

# กำหนด Category ID ที่ต้องการดึง (เช่น '1624' ตามที่คุณต้องการ)
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

        auth_status = user_info.get("user_info", {}).get("auth")
        status = user_info.get("user_info", {}).get("status")

        if auth_status == 1 and status == "Active":
            print("[+] ยืนยันตัวตนสำเร็จ!")
        else:
            print("[-] บัญชีมีปัญหา หรือหมดอายุ")
            return

        # ดึงรายชื่อหมวดหมู่เพื่อแปลง ID เป็นชื่อจริง
        print("[*] กำลังดึงข้อมูลหมวดหมู่ช่อง...")
        categories_url = f"{HOST}/player_api.php?username={USERNAME}&password={PASSWORD}&action=get_live_categories"
        res_cat = requests.get(categories_url, headers=headers, timeout=30)
        cat_data = res_cat.json()
        
        category_map = {}
        if isinstance(cat_data, list):
            for cat in cat_data:
                cat_id = str(cat.get("category_id"))
                cat_name = cat.get("category_name", "Uncategorized")
                category_map[cat_id] = cat_name

        # ดึงรายชื่อช่องสดทั้งหมด
        print("[2] กำลังดึงรายชื่อช่องสด (Live Streams) จาก API...")
        get_live_url = f"{HOST}/player_api.php?username={USERNAME}&password={PASSWORD}&action=get_live_streams"

        res_live = requests.get(get_live_url, headers=headers, timeout=60)
        live_data = res_live.json()

        if not isinstance(live_data, list) or len(live_data) == 0:
            print("[-] ไม่พบรายการช่องสดจาก API")
            return

        print(f"[+] พบช่องสดทั้งหมด {len(live_data)} ช่อง!")
        print(f"[3] กำลังกรองเฉพาะกลุ่มที่ต้องการ (ID: {TARGET_CATEGORY_IDS}) และสร้างไฟล์ {OUTPUT_LIVE_M3U}...")
        
        epg_url = f"{HOST}/xmltv.php?username={USERNAME}&password={PASSWORD}"
        count = 0

        with open(OUTPUT_LIVE_M3U, "w", encoding="utf-8") as f:
            f.write(f'#EXTM3U url-tvg="{epg_url}"\n')

            for item in live_data:
                cat_id = str(item.get("category_id", ""))
                
                # เงื่อนไขกรองเฉพาะ ID ที่อยู่ใน TARGET_CATEGORY_IDS เท่านั้น
                if cat_id in TARGET_CATEGORY_IDS:
                    name = item.get("name", "Unknown")
                    stream_id = item.get("stream_id")
                    group_title = category_map.get(cat_id, "General")
                    container_extension = item.get("container_extension", "ts")

                    stream_url = f"{HOST}/live/{USERNAME}/{PASSWORD}/{stream_id}.{container_extension}"

                    f.write(f'#EXTINF:-1 tvg-id="{stream_id}" group-title="{group_title}", {name}\n')
                    f.write(f"{stream_url}\n")
                    count += 1

        print(f"[✔] สำเร็จ! กรองมาได้ทั้งหมด {count} ช่อง และบันทึกไฟล์เรียบร้อยแล้ว")

    except Exception as e:
        print(f"[-] เกิดข้อผิดพลาด: {e}")

if __name__ == "__main__":
    get_live_via_api()
