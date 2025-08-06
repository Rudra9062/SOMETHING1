import time
import random
from instagrapi import Client

# --- Load File Safely ---
def load_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"[❌] File not found: {filename}")
        return []

# --- Load Data ---
groups = load_file("groups.txt")
messages = load_file("messages.txt")
delays = [int(x) for x in load_file("delays.txt") if x.isdigit()]
haters_data = load_file("haters.txt")

# --- Haters Dictionary ---
haters_dict = {}
for line in haters_data:
    if "::" in line:
        user, msg = line.split("::", 1)
        haters_dict[user.strip().lower()] = msg.strip()

# --- Login using saved session ---
cl = Client()
try:
    cl.load_settings("session.json")
    cl.login("p4nda_hu", "Oggy420")
    print("[✅] Logged in using saved session.")
except Exception as e:
    print(f"[❌] Login failed: {e}")
    exit()

# --- Auto-fetch groups if file is empty ---
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
    print("[⚠️] Exiting: Missing groups or messages.")
    exit()

# --- Message Sending Loop ---
while True:
    try:
        group_id = random.choice(groups)
        thread = cl.direct_thread(group_id)
        usernames = [u.username.lower() for u in thread.users]

        # Check for haters
        message = random.choice(messages)
        for user in usernames:
            if user in haters_dict:
                message = haters_dict[user]
                print(f"[⚠️] Hater detected: {user}, sending custom message.")
                break

        print(f"[➡️] Sending to group {group_id}")
        cl.direct_send(message, thread_ids=[group_id])
        print(f"[✅] Sent: {message}")

        delay = random.choice(delays) if delays else random.randint(300, 600)
        print(f"[⏳] Waiting {delay // 60}m {delay % 60}s...\n")
        time.sleep(delay)

    except Exception as e:
        print(f"[❌] Error: {e}")
        print("[⏸️] Waiting 60s before retrying...\n")
        time.sleep(60)
