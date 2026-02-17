from flask import Flask
import threading
import subprocess
import time
import sys
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Bot system is running"

def run_bot(script):
    try:
        time.sleep(3)
        subprocess.Popen([sys.executable, script])
    except Exception as e:
        print(f"Error starting {script}: {e}")

if __name__ == "__main__":
    threading.Thread(target=run_bot, args=("main_bot.py",)).start()
    threading.Thread(target=run_bot, args=("admin_bot.py",)).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
