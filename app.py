from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import httpx
from google_play_scraper import app as play_scraper
from bs4 import BeautifulSoup
import re
import asyncio
import json
import os
import uvicorn

app = FastAPI()

FF_MANIA_URL = "https://www.freefiremania.com.br/free-fire-new-update.html"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def load_client_urls():
    file_path = 'clients_url.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {"error": "clients_url.json not found"}

async def get_api_update():
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, lambda: play_scraper('com.dts.freefireth', lang="bn", country='bd'))
        play_version = result['version']
        
        api_url = f'https://version.ggwhitehawk.com/live/ver.php?version={play_version}&lang=bn&device=android&channel=android&appstore=googleplay&region=BD&whitelist_version=1.3.0&whitelist_sp_version=1.0.0'
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(api_url)
            data = response.json()

        return {
            "remote_version": data.get('remote_version'),
            "server_url": data.get('server_url'),
            "latest_release_version": data.get('latest_release_version'),
            "play_store_version": play_version
        }
    except Exception as e:
        return {"error": str(e)}

async def get_scraping_update():
    try:
        async with httpx.AsyncClient(timeout=15.0, headers=HEADERS) as client:
            r = await client.get(FF_MANIA_URL)
            r.raise_for_status()
        
        s = BeautifulSoup(r.content, 'html.parser')
        t = ' '.join(s.get_text().split())
        p = r'The next Free Fire update happens on (.+?) \((GMT[^)]+)\), remaining (.+?)\.'
        m = re.search(p, t, re.IGNORECASE)
        
        v = re.findall(r'OB\d+', t)
        uv = list(dict.fromkeys(v))
        
        if m:
            return {
                "NextUpdate_Date": f"{m.group(1).strip()} ({m.group(2).strip()})",
                "countdown": m.group(3).strip(),
                "from_version": uv[0] if len(uv) > 0 else "N/A",
                "to_version": uv[1] if len(uv) > 1 else "N/A"
            }
        return {"error": "Scraping pattern not found"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/update", response_class=HTMLResponse)
async def get_combined_update():
    region_urls = load_client_urls()
    api_task, web_task = await asyncio.gather(get_api_update(), get_scraping_update())

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Free Fire Update Info</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 10px; background: #f0f0f0; }}
            .container {{ max-width: 800px; margin: auto; background: white; padding: 15px; border-radius: 10px; }}
            .section {{ margin-bottom: 15px; padding: 10px; background: #f9f9f9; border-radius: 5px; }}
            .link {{ color: #0066cc; text-decoration: none; }}
            .link:hover {{ text-decoration: underline; }}
            .telegram-link {{ display: inline-block; margin: 5px 10px 5px 0; padding: 8px 15px; background: #0088cc; color: white; border-radius: 5px; text-decoration: none; }}
            .telegram-link:hover {{ background: #006699; }}
            pre {{ background: #eee; padding: 10px; border-radius: 5px; overflow-x: auto; font-size: 12px; }}
            h1, h2 {{ color: #333; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📱 Free Fire Update Information</h1>
            
            <div class="section">
                <h2>📦 Source Update Info</h2>
                <pre>{json.dumps(api_task, indent=2, ensure_ascii=False)}</pre>
            </div>
            
            <div class="section">
                <h2>🎮 Game Update Info</h2>
                <pre>{json.dumps(web_task, indent=2, ensure_ascii=False)}</pre>
            </div>
            
            <div class="section">
                <h2>🌍 Region URLs</h2>
                <pre>{json.dumps(region_urls, indent=2, ensure_ascii=False)}</pre>
            </div>
            
            <div class="section">
                <h2>👤 Credit</h2>
                <p>Created by Flexbase | Partner: LORD MORPHEUS</p>
            </div>
            
            <div class="section">
                <h2>📢 Telegram</h2>
                <a href="https://t.me/Flexbasei" target="_blank" class="telegram-link">📱 Flexbase: @Flexbasei</a>
                <a href="https://t.me/spideerio_yt" target="_blank" class="telegram-link">📱 LORD MORPHEUS: @spideerio_yt</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html


@app.get("/")
async def api_update():
    region_urls = load_client_urls()
    api_task, web_task = await asyncio.gather(get_api_update(), get_scraping_update())

    return {
        "status": "success",
        "SourceUpdate_info": api_task,
        "GameUpdate_info": web_task,
        "Region_URLs": region_urls,
        "Credit": "Created by Gấu Ngốc Nghếch",
        "Telegram": {
            "xHenntaiiz": {
                "username": "@henntaiiz",
                "url": "https://t.me/henntaiiz"
            }
        }
    }

if __name__ == "__main__":
    # Lấy IP của máy
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print("\n" + "="*50)
    print("🚀 SERVER ĐANG CHẠY!")
    print("="*50)
    print(f"📱 Truy cập trên điện thoại: http://{local_ip}:8000")
    print(f"🏠 Truy cập local: http://127.0.0.1:8000")
    print(f"📄 Trang update: http://{local_ip}:8000/update")
    print(f"📄 Trang update local: http://127.0.0.1:8000/update")
    print(f"📡 API JSON: http://{local_ip}:8000/api/update")
    print("="*50)
    print("⚠️  Nhấn CTRL+C để dừng server")
    print("="*50 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)