import requests
import json
import time
import os
import random
import threading
import queue
from datetime import datetime
from bs4 import BeautifulSoup

R = "\033[0m"
B = "\033[1m"
RED = "\033[91m"
GRN = "\033[92m"
YLW = "\033[93m"
CYN = "\033[96m"
MAG = "\033[95m"
GRY = "\033[90m"

mini = lambda s: ''.join(chr(0x1D49C + ord(c) - ord('A')) if 'A' <= c <= 'Z' else c for c in s.upper())

def banner():
    print(f"""
{GRN}{B}
 ▄▄▄       ██▀███       ██████  ██▓███   ▄▄▄       ███▄ ▄███▓ ███▄ ▄███▓▓█████  ██▀███     
▒████▄    ▓██ ▒ ██▒   ▒██    ▒ ▓██░  ██▒▒████▄    ▓██▒▀█▀ ██▒▓██▒▀█▀ ██▒▓█   ▀ ▓██ ▒ ██▒   
▒██  ▀█▄  ▓██ ░▄█ ▒   ░ ▓██▄   ▓██░ ██▓▒▒██  ▀█▄  ▓██    ▓██░▓██    ▓██░▒███   ▓██ ░▄█ ▒   
░██▄▄▄▄██ ▒██▀▀█▄       ▒   ██▒▒██▄█▓▒ ▒░██▄▄▄▄██ ▒██    ▒██ ▒██    ▒██ ▒▓█  ▄ ▒██▀▀█▄     
 ▓█   ▓██▒░██▓ ▒██▒   ▒██████▒▒▒██▒ ░  ░ ▓█   ▓██▒▒██▒   ░██▒▒██▒   ░██▒░▒████▒░██▓ ▒██▒   
 ▒▒   ▓▒█░░ ▒▓ ░▒▓░   ▒ ▒▓▒ ▒ ░▒▓▒░ ░  ░ ▒▒   ▓▒█░░ ▒░   ░  ░░ ▒░   ░  ░░░ ▒░ ░░ ▒▓ ░▒▓░   
  ▒   ▒▒ ░  ░▒ ░ ▒░   ░ ░▒  ░ ░░▒ ░       ▒   ▒▒ ░░  ░      ░░  ░      ░ ░ ░  ░  ░▒ ░ ▒░   
  ░   ▒     ░░   ░    ░  ░  ░  ░░         ░   ▒   ░      ░   ░      ░      ░     ░░   ░    
      ░  ░   ░              ░                 ░  ░       ░          ░      ░  ░   ░        
                                                                                           
{YLW} dc user arian69000 • FASTEST • 2026 • dm me for paid tools
{CYN} ════════════════════════════════════════════════{R}
""")

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def validate_proxy(proxy_dict, timeout=6):
    test_url = "http://httpbin.org/ip"
    try:
        r = requests.get(test_url, proxies=proxy_dict, timeout=timeout)
        return r.status_code == 200
    except:
        return False

def validate_proxies(proxy_list, max_workers=30):
    if not proxy_list:
        return []
    print(f" {CYN}Validating {len(proxy_list)} proxies...{R}")
    valid = []
    def check(p):
        return p if validate_proxy(p) else None
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(check, proxy_list)
        valid = [p for p in results if p is not None]
    print(f" {GRN}[+] {len(valid)}/{len(proxy_list)} proxies alive{R}")
    return valid

def scrape_proxies(limit=180):
    urls = [
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=9000&country=all",
        "https://free-proxy-list.net/",
        "https://www.sslproxies.org/",
        "https://www.proxy-list.download/api/v1/get?type=http"
    ]
    proxies = set()
    ua = {"User-Agent": "Mozilla/5.0"}
    print(f" {CYN}Scraping proxies...{R}")
    for u in urls:
        try:
            r = requests.get(u, headers=ua, timeout=7)
            if r.status_code != 200: continue
            if "proxyscrape" in u or "proxy-list.download" in u:
                proxies.update(line.strip() for line in r.text.splitlines() if ':' in line)
            else:
                soup = BeautifulSoup(r.text, 'html.parser')
                for row in soup.select('table tr')[1:]:
                    tds = row.select('td')
                    if len(tds) >= 2:
                        proxies.add(f"{tds[0].text}:{tds[1].text}")
        except:
            pass
    formatted = [{"http": f"http://{p}", "https": f"http://{p}"} for p in list(proxies)[:limit]]
    return formatted

def load_proxies_txt():
    if not os.path.exists("proxies.txt"): return []
    with open("proxies.txt", encoding="utf-8", errors="ignore") as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    return [{"http": 'http://'+l if not l.startswith(('http://','https://')) else l,
             "https": 'http://'+l if not l.startswith(('http://','https://')) else l} for l in lines]


def send(webhook_url, payload, proxy=None):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Mozilla/5.0 (X11; Linux x86_64)"
        ])
    }
    s = requests.Session()
    if proxy: s.proxies = proxy
    for attempt in range(9):
        try:
            r = s.post(webhook_url, json=payload, headers=headers, timeout=4)
            if r.status_code in (200,204): return True
            if r.status_code == 429:
                wait = 0.6
                try: wait = float(r.json().get("retry_after", 0.6)) + random.uniform(0.2,1.1)
                except: pass
                if attempt < 5: wait *= random.uniform(0.25, 0.7)
                time.sleep(max(0.1, wait))
                continue
            if r.status_code == 404: return False
            return False
        except:
            time.sleep(0.2 + random.random()*0.5)
    return False

def spam_worker(webhook_url, q, proxies):
    while True:
        try:
            payload = q.get_nowait()
        except queue.Empty:
            break
        success = send(webhook_url, payload, random.choice(proxies) if proxies else None)
        if success:
            print(f" {GRN}+SPAMMED{R}")
        else:
            print(f" {RED}-FAILED{R}")
        time.sleep(random.uniform(0.03, 0.28))

def launch_spam(webhook_url, message, threads, proxies, custom_name=None, custom_avatar=None):
    if not message: return
    payload_base = {"content": message}
    if custom_name:
        payload_base["username"] = custom_name
    if custom_avatar:
        payload_base["avatar_url"] = custom_avatar
    q = queue.Queue()
    for _ in range(6000):
        q.put(payload_base)
    print(f"\n {CYN}Launching {threads} threads | Queue ~{q.qsize()}{R}")
    print(f" {GRY}Proxies: {len(proxies)} | Ctrl+C to stop{R}")
    if custom_name or custom_avatar:
        print(f" {MAG}Spoof → name: {custom_name or 'default'} | avatar: {custom_avatar or 'default'}{R}\n")
    ts = []
    for _ in range(threads):
        t = threading.Thread(target=spam_worker, args=(webhook_url, q, proxies), daemon=True)
        t.start()
        ts.append(t)
    try:
        while any(t.is_alive() for t in ts):
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n {YLW}Spam stopped.{R}")


def delete_webhook(webhook_url, proxies):
    p = random.choice(proxies) if proxies else None
    try:
        r = requests.delete(webhook_url, proxies=p, timeout=5)
        if r.status_code in (200,204):
            print(f" {GRN}Webhook deleted{R}")
        elif r.status_code == 404:
            print(f" {YLW}Already gone{R}")
        else:
            print(f" {RED}Failed {r.status_code}{R}")
    except Exception as e:
        print(f" {RED}{e}{R}")

def show_webhook_info(webhook_url, proxies):
    p = random.choice(proxies) if proxies else None
    try:
        r = requests.get(webhook_url, proxies=p, timeout=5)
        if r.status_code != 200:
            print(f" {RED}Fetch failed {r.status_code}{R}")
            return
        d = r.json()
        snow = d.get('id', '0')
        created = "???"
        if snow.isdigit():
            ts = ((int(snow) >> 22) + 1420070400000) // 1000
            created = datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S UTC")

        avatar = d.get('avatar')
        avatar_url = f"https://cdn.discordapp.com/avatars/{snow}/{avatar}.png" if avatar else "None"

        print(f"""
{GRN}══════ {("WEBHOOK INFO")} ══════{R}
  {CYN}ID              :{R} {d.get('id')}
  {CYN}Name            :{R} {d.get('name') or 'None'}
  {CYN}Avatar          :{R} {avatar or 'None'}
  {CYN}Avatar URL      :{R} {avatar_url}
  {CYN}Channel ID      :{R} {d.get('channel_id')}
  {CYN}Guild ID        :{R} {d.get('guild_id') or 'None (DM webhook?)'}
  {CYN}Application ID  :{R} {d.get('application_id') or 'None'}
  {CYN}Type            :{R} {d.get('type') or 'Unknown'} (1=Incoming, 2=Channel Follower, 3=Application)
  {CYN}Token           :{R} {d.get('token') or 'Hidden'}
  {CYN}Created         :{R} {created}
{GRN}═══════════════════════════════{R}
""")
    except Exception as e:
        print(f" {RED}{e}{R}")

def create_single_webhook(token, guild_id, channel_id, name="x", save=True):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    payload = {"name": name}
    url = f"https://discord.com/api/v10/channels/{channel_id}/webhooks"
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=7)
        if r.status_code in (200,201):
            d = r.json()
            wh = f"https://discord.com/api/webhooks/{d['id']}/{d['token']}"
            print(f" {GRN}[+] {wh}{R}")
            if save:
                os.makedirs("Logs", exist_ok=True)
                with open("Logs/created.txt", "a", encoding="utf-8") as f:
                    f.write(f"{wh} | {guild_id}/{channel_id} | {datetime.now():%Y-%m-%d %H:%M}\n")
            return wh
        else:
            print(f" {RED}Failed {r.status_code} – {r.text[:140]}{R}")
    except Exception as e:
        print(f" {RED}{e}{R}")
    return None

def mass_create_webhooks(token, guild_id, channel_id, count=30, name_prefix="x"):
    print(f" {CYN}Mass creating {count} webhooks...{R}")
    created = 0
    for i in range(1, count+1):
        name = f"{name_prefix}-{i:03d}"
        if create_single_webhook(token, guild_id, channel_id, name, save=True):
            created += 1
        time.sleep(random.uniform(0.4, 1.3))
    print(f" {GRN}Done → {created}/{count} created{R}")


def get_proxies_if_needed():
    use = input(f" {YLW}Use proxies? (y/n) → {R}").lower().startswith('y')
    if not use: return []
    scrape = input(f" {YLW}Scrape fresh? (y/n) → {R}").lower().startswith('y')
    if scrape:
        raw = scrape_proxies()
    else:
        raw = load_proxies_txt()
        if not raw:
            print(f" {RED}No proxies.txt{R}")
            return []
    return validate_proxies(raw) if raw else []


def main():
    while True:
        cls()
        banner()

        print(f"""
{GRY}═══════════════════════════════════════════════{R}
  {GRN}1{R} Spam single message (+SPAMMED / -FAILED)
  {GRN}2{R} Webhook deleter
  {GRN}3{R} Webhook info (enhanced)
  {GRN}4{R} Create single webhook
  {GRN}5{R} Mass create webhooks
  {GRN}0{R} Exit
{GRY}═══════════════════════════════════════════════{R}
""")
        opt = input(f" {CYN}→ {R}").strip()

        if opt == "0": break

        webhook = None
        if opt in "123":
            webhook = input(f"\n {GRN}Webhook URL → {R}").strip()
            if not webhook.startswith("https://discord.com/api/webhooks/"):
                print(f" {RED}Invalid webhook{R}")
                time.sleep(1.2)
                continue

        proxies = get_proxies_if_needed() if opt in "123" else []

        if opt == "1":
            msg = input(f" {GRN}Message → {R}").strip()
            if not msg: continue
            name = input(f" {GRN}Custom name (optional) → {R}").strip() or None
            avatar = input(f" {GRN}Avatar URL (optional) → {R}").strip() or None
            try:
                th = int(input(f" {GRN}Threads (10-100) → {R}") or 60)
                th = max(5, min(150, th))
            except:
                th = 60
            launch_spam(webhook, msg, th, proxies, name, avatar)

        elif opt == "2":
            delete_webhook(webhook, proxies)

        elif opt == "3":
            show_webhook_info(webhook, proxies)

        elif opt == "4":
            token = input(f" {GRN}User token → {R}").strip()
            gid = input(f" {GRN}Guild ID → {R}").strip()
            cid = input(f" {GRN}Channel ID → {R}").strip()
            name = input(f" {GRN}Name [x] → {R}") or "x"
            create_single_webhook(token, gid, cid, name)

        elif opt == "5":
            token = input(f" {GRN}User token → {R}").strip()
            gid = input(f" {GRN}Guild ID → {R}").strip()
            cid = input(f" {GRN}Channel ID → {R}").strip()
            cnt = int(input(f" {GRN}Count (5-100) → {R}") or 40)
            pref = input(f" {GRN}Prefix [x] → {R}") or "x"
            mass_create_webhooks(token, gid, cid, cnt, pref)

        input(f"\n {GRY}ENTER to continue...{R}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{GRY}Exit.{R}")