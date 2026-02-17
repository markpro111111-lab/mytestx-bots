import threading
import subprocess
import time
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

def run_main():
    time.sleep(2)
    subprocess.Popen(["python", "main_bot.py"])

def run_admin():
    time.sleep(3)
    subprocess.Popen(["python", "admin_bot.py"])

if __name__ == "__main__":
    threading.Thread(target=run_main).start()
    threading.Thread(target=run_admin).start()
    app.run(host="0.0.0.0", port=8080)
