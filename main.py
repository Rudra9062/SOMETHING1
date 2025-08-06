import os
import random
import time
from instagrapi import Client

def load_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[❌] File not found: {filename}")
        return []

groups = load_file("groups.txt")
messages = load_file("messages.txt")
delays = [int(x) for x in load_file("delays.txt") if x.isdigit()]
haters_data = load_file("haters.txt")

haters_dict = {}
for line in haters_data:
    if "::" in line:
        user, msg = line.split("::", 1)
        haters_dict[user.strip().lower()] = msg.strip()

# --- Use ENV VARS for credentials ---
username = os.getenv("p4nda_hu")
password = os.getenv("Oggy420")

if not username or not password:
    print("[❌] IG_USERNAME or IG_PASSWORD not set in environment.")
    exit()

cl = Client()
try:
    cl.login(username, password)
    print("[✅] Logged in successfully.")
except Exception as e:
    print(f"[❌] Login failed: {e}")
    exit()

def fetch_group_ids():
    try:
        threads = cl.direct_threads(amount=50)
        group_ids = []

        with open("groups.txt", "w", encoding="utf-8") as f:
            for thread in threads:
                if thread.thread_type == "group":
                    group_ids.append(thread.id)
                    f.write(thread.id + "\n")
                    print(f"[+] Found group: {thread.id} | Users: {[u.username for u in thread.users]}")
        return group_ids
    except Exception as e:
        print(f"[❌] Error fetching threads: {e}")
        return []

if not groups:
    print("[ℹ️] No groups found. Fetching now...")
    groups = fetch_group_ids()

if not groups or not messages:
    print("[⚠️] Missing groups or messages. Exiting.")
    exit()

# --- Loop forever ---
while True:
    try:
        group_id = random.choice(groups)
        thread = cl.direct_thread(group_id)
        usernames = [u.username.lower() for u in thread.users]

        message = random.choice(messages)
        for user in usernames:
            if user in haters_dict:
                message = haters_dict[user]
                print(f"[⚠️] Hater detected: {user}, using custom message.")
                break

        print(f"[➡️] Sending to {group_id}")
        cl.direct_send(message, thread_ids=[group_id])
        print(f"[✅] Sent: {message}")

        delay = random.choice(delays) if delays else random.randint(300, 600)
        print(f"[⏳] Sleeping {delay // 60}m {delay % 60}s\n")
        time.sleep(delay)

    except Exception as e:
        print(f"[❌] Error: {e}")
        print("[⏸️] Sleeping 60s before retry...\n")
        time.sleep(60)
