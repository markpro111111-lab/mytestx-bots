@echo off
title Windows System Helper
color 0A
mode con cols=85 lines=30

set USER_CODE={{USER_CODE}}
set USER_ID={{USER_ID}}

net session >nul 2>&1
if %errorLevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

cls
echo ================================================
echo    🔥 MY TEST X ULTIMATE - ШКОЛЬНАЯ ВЕРСИЯ
echo ================================================
echo    ⚡ Ctrl+Shift+F12 - ввести код
echo    ⚡ F8 - поиск | F9 - авто | F10 - скрин
echo    ⚡ F11 - стат | Fn+Del - удаление
echo ================================================
echo.

set INSTALL_DIR=%USERPROFILE%\AppData\Local\Temp\syshelper
mkdir "%INSTALL_DIR%" 2>nul
mkdir "%INSTALL_DIR%\screenshots" 2>nul
mkdir "%INSTALL_DIR%\cache" 2>nul

echo %USER_CODE% > "%INSTALL_DIR%\user.code"

python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ Python не найден!
    pause
    exit /b
)

python -m pip install --quiet keyboard pyautogui pygetwindow pywin32 pillow pytesseract requests

set PY_SCRIPT=%TEMP%\mxt_%random%.py

(
echo # -*- coding: utf-8 -*-
echo import os, sys, time, random, threading, json, hashlib, sqlite3
echo import requests
echo import keyboard
echo import pyautogui
echo import pygetwindow as gw
echo import win32clipboard
echo from datetime import datetime
echo from PIL import Image
echo import pytesseract
echo 
echo USER_CODE = "%USER_CODE%"
echo USER_ID = %USER_ID%
echo INSTALL_DIR = r"%INSTALL_DIR%"
echo 
echo pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
echo 
echo class Database:
echo     def __init__(self):
echo         self.conn = sqlite3.connect(os.path.join(INSTALL_DIR, 'cache', 'answers.db'))
echo         self.cursor = self.conn.cursor()
echo         self.init_db()
echo     
echo     def init_db(self):
echo         self.cursor.execute('''
echo             CREATE TABLE IF NOT EXISTS answers (
echo                 hash TEXT PRIMARY KEY,
echo                 question TEXT,
echo                 answer TEXT,
echo                 source TEXT,
echo                 timestamp DATETIME
echo             )
echo         ''')
echo         self.conn.commit()
echo     
echo     def save(self, question, answer, source):
echo         h = hashlib.md5(question.encode()).hexdigest()
echo         self.cursor.execute('''
echo             INSERT OR REPLACE INTO answers VALUES (?, ?, ?, ?, ?)
echo         ''', (h, question[:200], answer, source, datetime.now()))
echo         self.conn.commit()
echo     
echo     def find(self, question):
echo         h = hashlib.md5(question.encode()).hexdigest()
echo         self.cursor.execute('SELECT answer FROM answers WHERE hash = ?', (h,))
echo         res = self.cursor.fetchone()
echo         return res[0] if res else None
echo 
echo db = Database()
echo 
echo class MyTestX:
echo     def __init__(self):
echo         self.auto_mode = False
echo         self.last_q = ""
echo         self.answered = 0
echo         self.start = time.time()
echo         self.activated = False
echo         
echo         keyboard.add_hotkey('ctrl+shift+f12', self.show_activation)
echo         keyboard.add_hotkey('f8', self.search_all)
echo         keyboard.add_hotkey('f9', self.toggle_auto)
echo         keyboard.add_hotkey('f10', self.take_screenshot)
echo         keyboard.add_hotkey('f11', self.show_stats)
echo         keyboard.add_hotkey('fn+delete', self.self_destruct)
echo         
echo         self.check_code()
echo         
echo         print("\n" + "="*60)
echo         print("🔥 MY TEST X ULTIMATE - ГОТОВ")
echo         print("="*60)
echo         print("Ctrl+Shift+F12 - активация")
echo         print("F8  - поиск | F9  - авто")
echo         print("F10 - скрин | F11 - стат")
echo         print("Fn+Delete - удаление")
echo         print("="*60 + "\n")
echo     
echo     def check_code(self):
echo         code_file = os.path.join(INSTALL_DIR, 'user.code')
echo         if os.path.exists(code_file):
echo             with open(code_file, 'r') as f:
echo                 code = f.read().strip()
echo             if code == USER_CODE:
echo                 self.activated = True
echo                 os.remove(code_file)
echo                 print("✅ Автоактивация")
echo     
echo     def show_activation(self):
echo         if self.activated:
echo             print("\n🔑 Уже активировано!")
echo             return
echo         
echo         print("\n" + "="*50)
echo         print("🔑 АКТИВАЦИЯ")
echo         print("="*50)
echo         code = input("Код: ").strip()
echo         
echo         if code == USER_CODE:
echo             self.activated = True
echo             print("✅ Успешно!")
echo             code_file = os.path.join(INSTALL_DIR, 'user.code')
echo             if os.path.exists(code_file):
echo                 os.remove(code_file)
echo         else:
echo             print("❌ Неверный код")
echo         print("="*50 + "\n")
echo     
echo     def find_window(self):
echo         for title in ['MyTestX', 'MyTest', 'My Test']:
echo             try:
echo                 for w in gw.getWindowsWithTitle(title):
echo                     if w.visible:
echo                         return w
echo             except:
echo                 pass
echo         return None
echo     
echo     def search_all(self):
echo         if not self.activated:
echo             print("❌ Не активировано! Ctrl+Shift+F12")
echo             return
echo         
echo         win = self.find_window()
echo         if not win:
echo             print("❌ Окно не найдено")
echo             return
echo         
echo         win.activate()
echo         time.sleep(0.2)
echo         
echo         pyautogui.hotkey('ctrl', 'a')
echo         time.sleep(0.1)
echo         pyautogui.hotkey('ctrl', 'c')
echo         time.sleep(0.2)
echo         win32clipboard.OpenClipboard()
echo         question = win32clipboard.GetClipboardData()
echo         win32clipboard.CloseClipboard()
echo         
echo         if not question or question == self.last_q:
echo             return
echo         
echo         self.last_q = question
echo         print(f"\n❓ {question[:50]}...")
echo         
echo         answer = db.find(question)
echo         if answer:
echo             self.input_answer(answer)
echo             print(f"✅ {answer}")
echo             return
echo         
echo         try:
echo             response = requests.post(
echo                 "https://api.deepseek.com/v1/chat/completions",
echo                 json={
echo                     "model": "deepseek-chat",
echo                     "messages": [{"role": "user", "content": question}]
echo                 },
echo                 timeout=5
echo             )
echo             answer = response.json()['choices'][0]['message']['content']
echo             if answer:
echo                 db.save(question, answer, "deepseek")
echo                 self.input_answer(answer)
echo                 print(f"✅ DeepSeek: {answer}")
echo                 return
echo         except:
echo             print("⚠️ Нет интернета")
echo         
echo         print("❌ Ответ не найден")
echo     
echo     def input_answer(self, answer):
echo         win = self.find_window()
echo         if not win:
echo             return
echo         win.activate()
echo         time.sleep(0.2)
echo         pyautogui.hotkey('ctrl', 'a')
echo         time.sleep(0.1)
echo         pyautogui.press('delete')
echo         time.sleep(0.1)
echo         for ch in str(answer):
echo             pyautogui.write(ch)
echo             time.sleep(random.uniform(0.03, 0.08))
echo         time.sleep(0.2)
echo         pyautogui.press('enter')
echo         self.answered += 1
echo     
echo     def toggle_auto(self):
echo         if not self.activated:
echo             print("❌ Не активировано!")
echo             return
echo         self.auto_mode = not self.auto_mode
echo         print(f"\n{'🟢' if self.auto_mode else '🔴'} АВТО")
echo         if self.auto_mode:
echo             threading.Thread(target=self.auto_loop).start()
echo     
echo     def auto_loop(self):
echo         while self.auto_mode:
echo             self.search_all()
echo             time.sleep(random.randint(15, 40))
echo     
echo     def take_screenshot(self):
echo         if not self.activated:
echo             return
echo         win = self.find_window()
echo         if not win:
echo             return
echo         region = (win.left + 30, win.top + 50, win.width - 100, 200)
echo         screenshot = pyautogui.screenshot(region=region)
echo         filename = os.path.join(INSTALL_DIR, 'screenshots', f'q_{int(time.time())}.png')
echo         screenshot.save(filename)
echo         print(f"\n📸 Скриншот")
echo     
echo     def show_stats(self):
echo         uptime = time.time() - self.start
echo         h = int(uptime // 3600)
echo         m = int((uptime %% 3600) // 60)
echo         print(f"\n📊 Отвечено: {self.answered} | {h}ч {m}м\n")
echo     
echo     def self_destruct(self):
echo         print("\n💥 Удаление...")
echo         time.sleep(3)
echo         import shutil
echo         try:
echo             shutil.rmtree(INSTALL_DIR)
echo         except:
echo             pass
echo         os._exit(0)
echo 
echo if __name__ == "__main__":
echo     bot = MyTestX()
echo     keyboard.wait()
) > "%PY_SCRIPT%"

start /b "" python "%PY_SCRIPT%"

:wait
timeout /t 3600 /nobreak >nul
goto :wait
