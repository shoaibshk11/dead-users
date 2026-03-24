from flask import Flask, request, jsonify
import requests
from concurrent.futures import ThreadPoolExecutor
import random
import threading

app = Flask(__name__)

# 🔐 Add your proxies here
proxies_list = [
    # Example:
    # "http://user:pass@ip:port",
    # "http://ip:port",
]

headers = {
    "User-Agent": "Mozilla/5.0"
}

progress = {
    "total": 0,
    "done": 0
}

lock = threading.Lock()


def check_single(user):
    global progress

    url = f"https://www.instagram.com/{user}/"

    import time
    time.sleep(random.uniform(0.3, 0.8))

    proxy = None
    if proxies_list:
        proxy = {"http": random.choice(proxies_list),
                 "https": random.choice(proxies_list)}

    try:
        r = requests.get(url, headers=headers, proxies=proxy, timeout=5)

        result = "working" if r.status_code == 200 else "dead"

    except:
        result = "dead"

    with lock:
        progress["done"] += 1

    return user, result


@app.route("/check", methods=["POST"])
def check():
    global progress

    data = request.json.get("usernames", [])
    progress["total"] = len(data)
    progress["done"] = 0

    working = []
    dead = []

    # ⚡ THREAD POOL (adjust workers)
    with ThreadPoolExecutor(max_workers=15) as executor:
        results = executor.map(check_single, data)

        for user, result in results:
            if result == "working":
                working.append(user)
            else:
                dead.append(user)

    return jsonify({
        "working": working,
        "dead": dead
    })


@app.route("/progress")
def get_progress():
    return jsonify(progress)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
]

from flask import send_from_directory

@app.route("/")
def home():
    return send_from_directory(".", "index.html")