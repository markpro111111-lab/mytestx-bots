from flask import Flask
import threading
import os
import time

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running"

def run_main():
    time.sleep(2)
    os.system("python main_bot.py")

def run_admin():
    time.sleep(2)
    os.system("python admin_bot.py")

if __name__ == "__main__":
    threading.Thread(target=run_main).start()
    threading.Thread(target=run_admin).start()
    app.run(host="0.0.0.0", port=8080)
