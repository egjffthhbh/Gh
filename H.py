# -*- coding: utf-8 -*-
import os
import sys
import telebot
import subprocess
import zipfile
import tempfile
import shutil
from telebot import types
import time
from datetime import datetime, timedelta
import psutil
import sqlite3
import json
import logging
import signal
import threading
import re
import atexit
import requests
from threading import Thread
from flask import Flask

# ============ CUSTOM BANNER ============
def show_banner():
    banner = f"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║     ██████╗ ██╗████████╗██╗██╗  ██╗██╗  ██╗███████╗                         ║
║     ██╔══██╗██║╚══██╔══╝██║╚██╗██╔╝██║ ██╔╝██╔════╝                         ║
║     ██████╔╝██║   ██║   ██║ ╚███╔╝ █████╔╝ ███████╗                         ║
║     ██╔══██╗██║   ██║   ██║ ██╔██╗ ██╔═██╗ ╚════██║                         ║
║     ██║  ██║██║   ██║   ██║██╔╝ ██╗██║  ██╗███████║                         ║
║     ╚═╝  ╚═╝╚═╝   ╚═╝   ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝                         ║
║                                                                               ║
║     ██╗  ██╗ ██████╗ ███████╗████████╗██╗███╗   ██╗ ██████╗                 ║
║     ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝██║████╗  ██║██╔════╝                 ║
║     ███████║██║   ██║███████╗   ██║   ██║██╔██╗ ██║██║  ███╗                ║
║     ██╔══██║██║   ██║╚════██║   ██║   ██║██║╚██╗██║██║   ██║                ║
║     ██║  ██║╚██████╔╝███████║   ██║   ██║██║ ╚████║╚██████╔╝                ║
║     ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚═════╝                 ║
║                                                                               ║
║                    🔥 @Ritikxyz099 HOSTING 🔥                                     ║
║                    TELEGRAM BOT HOSTING SERVICE                               ║
║                    VERSION: 6.0 | STATUS: ACTIVE 🔥                          ║
║                                                                               ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║  👑 OWNER: @Ritikxyz099                                                          ║
║  🤖 BOT NAME: PY HOSTING BOT                                                 ║
║  📡 STATUS: 🟢 ONLINE & RUNNING                                              ║
║  ⏰ START TIME: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                              ║
║  🌐 PLATFORM: RENDER.COM                                                    ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

# ============ ENVIRONMENT VARIABLES ============
TOKEN = os.environ.get("8799747223:AAFSkMsJIxlVNaduayzXpBq_t1KrhakhzmE", "")
OWNER_ID = int(os.environ.get("7964730489", 0))
ADMIN_ID = int(os.environ.get("7964730489", 0))
YOUR_USERNAME = os.environ.get("YOUR_USERNAME", "@Ritikxyz099")
UPDATE_CHANNEL = os.environ.get("UPDATE_CHANNEL", "https://t.me/Xyzr4")

# ============ VALIDATE ENV ============
if not TOKEN or OWNER_ID == 0 or ADMIN_ID == 0:
    print("\n❌ ERROR: Please set environment variables!")
    print("   BOT_TOKEN, OWNER_ID, ADMIN_ID are required!\n")
    sys.exit(1)

# ============ FLASK KEEP ALIVE ============
flask_app = Flask('')

@flask_app.route('/')
def home():
    return """
    <html>
    <head><title>@Ritikxyz099 HOSTING</title></head>
    <body style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-align: center; padding: 50px;">
        <h1>🔥 @Ritikxyz099 HOSTING 🔥</h1>
        <h2>🤖 Telegram Bot Hosting Service</h2>
        <p>Status: 🟢 ACTIVE & RUNNING</p>
        <p>Bot: PY HOSTING BOT</p>
        <p>Owner: @Ritikxyz099</p>
        <hr>
        <p>Powered by Render.com</p>
    </body>
    </html>
    """

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("✅ Flask Keep-Alive server started on port " + os.environ.get("PORT", "8080"))

# ============ FOLDER SETUP ============
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_BOTS_DIR = os.path.join(BASE_DIR, 'upload_bots')
IROTECH_DIR = os.path.join(BASE_DIR, 'inf')
DATABASE_PATH = os.path.join(IROTECH_DIR, 'bot_data.db')

os.makedirs(UPLOAD_BOTS_DIR, exist_ok=True)
os.makedirs(IROTECH_DIR, exist_ok=True)

# ============ BOT INIT ============
bot = telebot.TeleBot(TOKEN)

# ============ DATA STRUCTURES ============
bot_scripts = {}
user_subscriptions = {}
user_files = {}
active_users = set()
admin_ids = {ADMIN_ID, OWNER_ID}
bot_locked = False

# ============ LOGGING ============
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============ COMMAND BUTTONS ============
COMMAND_BUTTONS = [
    ["📢 Updates Channel"],
    ["📤 Upload File", "📂 Check Files"],
    ["⚡ Bot Speed", "📊 Statistics"],
    ["📞 Contact Owner"]
]

ADMIN_BUTTONS = [
    ["📢 Updates Channel"],
    ["📤 Upload File", "📂 Check Files"],
    ["⚡ Bot Speed", "📊 Statistics"],
    ["💳 Subscriptions", "📢 Broadcast"],
    ["🔒 Lock Bot", "🟢 Running All Code"],
    ["👑 Admin Panel", "📞 Contact Owner"]
]

# ============ DATABASE SETUP ============
def init_db():
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS subscriptions
                     (user_id INTEGER PRIMARY KEY, expiry TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_files
                     (user_id INTEGER, file_name TEXT, file_type TEXT,
                      PRIMARY KEY (user_id, file_name))''')
        c.execute('''CREATE TABLE IF NOT EXISTS active_users
                     (user_id INTEGER PRIMARY KEY)''')
        c.execute('''CREATE TABLE IF NOT EXISTS admins
                     (user_id INTEGER PRIMARY KEY)''')
        c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (OWNER_ID,))
        if ADMIN_ID != OWNER_ID:
            c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (ADMIN_ID,))
        conn.commit()
        conn.close()
        print("✅ Database initialized")
    except Exception as e:
        print(f"❌ DB init error: {e}")

def load_data():
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        
        c.execute('SELECT user_id, expiry FROM subscriptions')
        for uid, expiry in c.fetchall():
            try:
                user_subscriptions[uid] = {'expiry': datetime.fromisoformat(expiry)}
            except:
                pass
        
        c.execute('SELECT user_id, file_name, file_type FROM user_files')
        for uid, fname, ftype in c.fetchall():
            if uid not in user_files:
                user_files[uid] = []
            user_files[uid].append((fname, ftype))
        
        c.execute('SELECT user_id FROM active_users')
        active_users.update(uid for (uid,) in c.fetchall())
        
        c.execute('SELECT user_id FROM admins')
        admin_ids.update(uid for (uid,) in c.fetchall())
        
        conn.close()
        print(f"✅ Data loaded: {len(active_users)} users, {len(admin_ids)} admins")
    except Exception as e:
        print(f"❌ Load data error: {e}")

# ============ HELPER FUNCTIONS ============
def get_user_folder(user_id):
    folder = os.path.join(UPLOAD_BOTS_DIR, str(user_id))
    os.makedirs(folder, exist_ok=True)
    return folder

def get_user_file_limit(user_id):
    if user_id == OWNER_ID:
        return float('inf')
    if user_id in admin_ids:
        return 999
    if user_id in user_subscriptions and user_subscriptions[user_id]['expiry'] > datetime.now():
        return 15
    return 3

def get_user_file_count(user_id):
    return len(user_files.get(user_id, []))

def is_bot_running(owner_id, file_name):
    script_key = f"{owner_id}_{file_name}"
    info = bot_scripts.get(script_key)
    if info and info.get('process'):
        try:
            proc = psutil.Process(info['process'].pid)
            return proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
        except:
            return False
    return False

def kill_process_tree(process_info):
    try:
        if process_info.get('log_file'):
            try:
                process_info['log_file'].close()
            except:
                pass
        process = process_info.get('process')
        if process and hasattr(process, 'pid'):
            try:
                parent = psutil.Process(process.pid)
                for child in parent.children(recursive=True):
                    try:
                        child.terminate()
                    except:
                        try:
                            child.kill()
                        except:
                            pass
                parent.terminate()
            except:
                pass
    except:
        pass

# ============ RUN SCRIPT ============
def run_script(script_path, owner_id, user_folder, file_name, msg_obj, attempt=1):
    script_key = f"{owner_id}_{file_name}"
    
    if attempt > 2:
        bot.reply_to(msg_obj, f"❌ Failed to run '{file_name}'")
        return
    
    try:
        if not os.path.exists(script_path):
            bot.reply_to(msg_obj, f"❌ Script '{file_name}' not found!")
            remove_user_file_db(owner_id, file_name)
            return
        
        if attempt == 1:
            check = subprocess.Popen([sys.executable, script_path], cwd=user_folder,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                _, stderr = check.communicate(timeout=5)
                if stderr:
                    match = re.search(r"ModuleNotFoundError: No module named '(.+?)'", stderr)
                    if match:
                        module = match.group(1)
                        bot.reply_to(msg_obj, f"📦 Installing missing module: {module}")
                        subprocess.run([sys.executable, '-m', 'pip', 'install', module], capture_output=True)
                        time.sleep(1)
                        threading.Thread(target=run_script, args=(script_path, owner_id, user_folder, file_name, msg_obj, attempt+1)).start()
                        return
            except subprocess.TimeoutExpired:
                check.kill()
        
        log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        log_file = open(log_path, 'w', encoding='utf-8', errors='ignore')
        
        process = subprocess.Popen([sys.executable, script_path], cwd=user_folder,
                                   stdout=log_file, stderr=log_file, stdin=subprocess.PIPE)
        
        bot_scripts[script_key] = {
            'process': process,
            'log_file': log_file,
            'file_name': file_name,
            'owner_id': owner_id,
            'start_time': datetime.now()
        }
        
        bot.reply_to(msg_obj, f"✅ Script '{file_name}' started! (PID: {process.pid})")
        
    except Exception as e:
        bot.reply_to(msg_obj, f"❌ Error: {str(e)}")

# ============ DATABASE OPERATIONS ============
DB_LOCK = threading.Lock()

def save_user_file(user_id, file_name, file_type='py'):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO user_files VALUES (?, ?, ?)', (user_id, file_name, file_type))
        conn.commit()
        conn.close()
        if user_id not in user_files:
            user_files[user_id] = []
        user_files[user_id] = [(fn, ft) for fn, ft in user_files[user_id] if fn != file_name]
        user_files[user_id].append((file_name, file_type))

def remove_user_file_db(user_id, file_name):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM user_files WHERE user_id = ? AND file_name = ?', (user_id, file_name))
        conn.commit()
        conn.close()
        if user_id in user_files:
            user_files[user_id] = [f for f in user_files[user_id] if f[0] != file_name]
            if not user_files[user_id]:
                del user_files[user_id]

def add_active_user(user_id):
    active_users.add(user_id)
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('INSERT OR IGNORE INTO active_users VALUES (?)', (user_id,))
        conn.commit()
        conn.close()

def save_subscription(user_id, expiry):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO subscriptions VALUES (?, ?)', (user_id, expiry.isoformat()))
        conn.commit()
        conn.close()
        user_subscriptions[user_id] = {'expiry': expiry}

def remove_subscription_db(user_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH)
        c = conn.cursor()
        c.execute('DELETE FROM subscriptions WHERE user_id = ?', (user_id,))
        conn.commit()
        conn.close()
        if user_id in user_subscriptions:
            del user_subscriptions[user_id]

# ============ BOT COMMANDS ============
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    user_id = message.from_user.id
    
    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, "🔒 Bot is locked. Try later.")
        return
    
    if user_id not in active_users:
        add_active_user(user_id)
        try:
            bot.send_message(OWNER_ID, f"🎉 New user: {message.from_user.first_name}\nID: {user_id}")
        except:
            pass
    
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    limit_str = "∞" if file_limit == float('inf') else str(file_limit)
    
    if user_id == OWNER_ID:
        status = "👑 OWNER"
    elif user_id in admin_ids:
        status = "🛡️ ADMIN"
    elif user_id in user_subscriptions and user_subscriptions[user_id]['expiry'] > datetime.now():
        days = (user_subscriptions[user_id]['expiry'] - datetime.now()).days
        status = f"⭐ PREMIUM ({days} days left)"
    else:
        status = "🆓 FREE USER"
    
    welcome_text = f"""
🔥 **@Ritikxyz099 HOSTING** 🔥

👋 Welcome, {message.from_user.first_name}!

📊 **Your Stats:**
├ 🆔 ID: `{user_id}`
├ 🔰 Status: {status}
├ 📁 Files: {current_files}/{limit_str}
└ 🤖 Active Bots: {len([k for k in bot_scripts.keys() if k.startswith(str(user_id))])}

📌 **Commands:**
├ /start - Show this menu
├ /upload - Upload Python/JS/zip file
├ /files - Check your files
├ /speed - Bot speed test
└ /stats - Bot statistics

💡 **Upload your bot files and run them 24/7!**

👑 **Developer:** @Ritikxyz099
    """
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if user_id in admin_ids:
        for row in ADMIN_BUTTONS:
            markup.add(*[types.KeyboardButton(btn) for btn in row])
    else:
        for row in COMMAND_BUTTONS:
            markup.add(*[types.KeyboardButton(btn) for btn in row])
    
    bot.reply_to(message, welcome_text, parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📢 Updates Channel")
def updates_channel(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📢 Join Channel", url=UPDATE_CHANNEL))
    bot.reply_to(message, "Join our updates channel:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "📤 Upload File")
def upload_file(message):
    user_id = message.from_user.id
    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, "🔒 Bot is locked!")
        return
    
    limit = get_user_file_limit(user_id)
    current = get_user_file_count(user_id)
    
    if current >= limit and limit != float('inf'):
        bot.reply_to(message, f"⚠️ File limit reached! ({current}/{limit})\nDelete old files first.")
        return
    
    bot.reply_to(message, "📤 Send me your `.py`, `.js`, or `.zip` file.")

@bot.message_handler(func=lambda m: m.text == "📂 Check Files")
def check_files(message):
    user_id = message.from_user.id
    files = user_files.get(user_id, [])
    
    if not files:
        bot.reply_to(message, "📂 No files uploaded yet!")
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for fname, ftype in files:
        running = is_bot_running(user_id, fname)
        icon = "🟢" if running else "🔴"
        markup.add(types.InlineKeyboardButton(f"{icon} {fname} ({ftype})", callback_data=f"file_{user_id}_{fname}"))
    
    bot.reply_to(message, "📂 Your files:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "⚡ Bot Speed")
def bot_speed(message):
    start = time.time()
    msg = bot.reply_to(message, "🏃 Testing speed...")
    latency = round((time.time() - start) * 1000, 2)
    bot.edit_message_text(f"⚡ Bot Speed: {latency}ms\n✅ Status: Online", message.chat.id, msg.message_id)

@bot.message_handler(func=lambda m: m.text == "📊 Statistics")
def statistics(message):
    total_users = len(active_users)
    total_files = sum(len(f) for f in user_files.values())
    running_bots = len(bot_scripts)
    
    stats = f"""
📊 **@Ritikxyz099 HOSTING STATISTICS**

👥 Total Users: {total_users}
📁 Total Files: {total_files}
🟢 Running Bots: {running_bots}
👑 Owner: @Ritikxyz099
🤖 Platform: Telegram Bot Hosting
    """
    bot.reply_to(message, stats, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text == "📞 Contact Owner")
def contact_owner(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("👑 Contact Owner", url=f"https://t.me/{YOUR_USERNAME.replace('@', '')}"))
    bot.reply_to(message, "Contact the owner:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "💳 Subscriptions")
def subscriptions_panel(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin only!")
        return
    bot.reply_to(message, "💳 Subscription Management\n\nUse /addsub <user_id> <days>\n/removesub <user_id>")

@bot.message_handler(func=lambda m: m.text == "📢 Broadcast")
def broadcast_init(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin only!")
        return
    msg = bot.reply_to(message, "📢 Send message to broadcast:\n/cancel to abort")
    bot.register_next_step_handler(msg, broadcast_send)

def broadcast_send(message):
    if message.text == "/cancel":
        bot.reply_to(message, "❌ Broadcast cancelled!")
        return
    
    sent = 0
    failed = 0
    for uid in active_users:
        try:
            bot.send_message(uid, f"📢 **BROADCAST**\n\n{message.text}", parse_mode='Markdown')
            sent += 1
            time.sleep(0.05)
        except:
            failed += 1
    
    bot.reply_to(message, f"✅ Broadcast complete!\nSent: {sent}\nFailed: {failed}")

@bot.message_handler(func=lambda m: m.text == "🔒 Lock Bot")
def lock_bot(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin only!")
        return
    global bot_locked
    bot_locked = True
    bot.reply_to(message, "🔒 Bot locked! Only admins can use.")

@bot.message_handler(func=lambda m: m.text == "🟢 Running All Code")
def run_all_code(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin only!")
        return
    
    bot.reply_to(message, "🔄 Starting all user scripts...")
    started = 0
    
    for uid, files in user_files.items():
        for fname, ftype in files:
            if not is_bot_running(uid, fname):
                folder = get_user_folder(uid)
                path = os.path.join(folder, fname)
                if os.path.exists(path) and ftype == 'py':
                    threading.Thread(target=run_script, args=(path, uid, folder, fname, message)).start()
                    started += 1
                time.sleep(0.5)
    
    bot.send_message(message.chat.id, f"✅ Started {started} scripts!")

@bot.message_handler(func=lambda m: m.text == "👑 Admin Panel")
def admin_panel(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin only!")
        return
    
    panel = f"""
👑 **ADMIN PANEL** 👑

📊 **Stats:**
├ Users: {len(active_users)}
├ Files: {sum(len(f) for f in user_files.values())}
├ Running: {len(bot_scripts)}
└ Admins: {len(admin_ids)}

🔧 **Commands:**
/addsub <user_id> <days>
/removesub <user_id>
/addadmin <user_id>
/removeadmin <user_id>
/stats
/broadcast
/lock
/unlock
    """
    bot.reply_to(message, panel, parse_mode='Markdown')

@bot.message_handler(commands=['addsub'])
def add_subscription(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin only!")
        return
    
    try:
        _, uid, days = message.text.split()
        uid = int(uid)
        days = int(days)
        
        current = user_subscriptions.get(uid, {}).get('expiry')
        if current and current > datetime.now():
            new_expiry = current + timedelta(days=days)
        else:
            new_expiry = datetime.now() + timedelta(days=days)
        
        save_subscription(uid, new_expiry)
        bot.reply_to(message, f"✅ Added {days} days subscription to `{uid}`!\nExpires: {new_expiry.strftime('%Y-%m-%d')}")
        
        try:
            bot.send_message(uid, f"🎉 You have been subscribed for {days} days!\nExpires: {new_expiry.strftime('%Y-%m-%d')}")
        except:
            pass
    except:
        bot.reply_to(message, "❌ Usage: /addsub <user_id> <days>")

@bot.message_handler(commands=['removesub'])
def remove_subscription(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin only!")
        return
    
    try:
        _, uid = message.text.split()
        uid = int(uid)
        remove_subscription_db(uid)
        bot.reply_to(message, f"✅ Removed subscription for `{uid}`")
    except:
        bot.reply_to(message, "❌ Usage: /removesub <user_id>")

@bot.message_handler(commands=['addadmin'])
def add_admin(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "⚠️ Owner only!")
        return
    
    try:
        _, uid = message.text.split()
        uid = int(uid)
        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH)
            c = conn.cursor()
            c.execute('INSERT OR IGNORE INTO admins VALUES (?)', (uid,))
            conn.commit()
            conn.close()
        admin_ids.add(uid)
        bot.reply_to(message, f"✅ Added admin: `{uid}`")
    except:
        bot.reply_to(message, "❌ Usage: /addadmin <user_id>")

@bot.message_handler(commands=['removeadmin'])
def remove_admin(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "⚠️ Owner only!")
        return
    
    try:
        _, uid = message.text.split()
        uid = int(uid)
        if uid == OWNER_ID:
            bot.reply_to(message, "❌ Cannot remove owner!")
            return
        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH)
            c = conn.cursor()
            c.execute('DELETE FROM admins WHERE user_id = ?', (uid,))
            conn.commit()
            conn.close()
        admin_ids.discard(uid)
        bot.reply_to(message, f"✅ Removed admin: `{uid}`")
    except:
        bot.reply_to(message, "❌ Usage: /removeadmin <user_id>")

@bot.message_handler(commands=['unlock'])
def unlock_bot(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin only!")
        return
    global bot_locked
    bot_locked = False
    bot.reply_to(message, "🔓 Bot unlocked!")

@bot.message_handler(content_types=['document'])
def handle_file(message):
    user_id = message.from_user.id
    
    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, "🔒 Bot locked!")
        return
    
    limit = get_user_file_limit(user_id)
    current = get_user_file_count(user_id)
    
    if current >= limit and limit != float('inf'):
        bot.reply_to(message, f"⚠️ File limit reached! ({current}/{limit})")
        return
    
    doc = message.document
    fname = doc.file_name
    
    if not (fname.endswith('.py') or fname.endswith('.js') or fname.endswith('.zip')):
        bot.reply_to(message, "❌ Only .py, .js, .zip files allowed!")
        return
    
    msg = bot.reply_to(message, f"📥 Downloading `{fname}`...")
    
    try:
        file_info = bot.get_file(doc.file_id)
        content = bot.download_file(file_info.file_path)
        
        folder = get_user_folder(user_id)
        path = os.path.join(folder, fname)
        
        with open(path, 'wb') as f:
            f.write(content)
        
        if fname.endswith('.zip'):
            with zipfile.ZipFile(path, 'r') as zf:
                zf.extractall(folder)
            os.remove(path)
            
            py_files = [f for f in os.listdir(folder) if f.endswith('.py')]
            js_files = [f for f in os.listdir(folder) if f.endswith('.js')]
            
            main_file = None
            if 'main.py' in py_files:
                main_file = 'main.py'
            elif 'bot.py' in py_files:
                main_file = 'bot.py'
            elif py_files:
                main_file = py_files[0]
            elif js_files:
                main_file = js_files[0]
            
            if main_file:
                save_user_file(user_id, main_file, 'py' if main_file.endswith('.py') else 'js')
                bot.edit_message_text(f"✅ Extracted & saved: `{main_file}`", message.chat.id, msg.message_id)
                
                if main_file.endswith('.py'):
                    run_script(os.path.join(folder, main_file), user_id, folder, main_file, message)
        else:
            save_user_file(user_id, fname, 'py' if fname.endswith('.py') else 'js')
            bot.edit_message_text(f"✅ Saved: `{fname}`", message.chat.id, msg.message_id)
            
            if fname.endswith('.py'):
                run_script(path, user_id, folder, fname, message)
    
    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)}", message.chat.id, msg.message_id)

# ============ CALLBACK HANDLERS ============
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    data = call.data
    
    if data.startswith("file_"):
        _, uid, fname = data.split("_", 2)
        uid = int(uid)
        
        if call.from_user.id != uid and call.from_user.id not in admin_ids:
            bot.answer_callback_query(call.id, "❌ Not your file!")
            return
        
        running = is_bot_running(uid, fname)
        ftype = 'py'
        for fn, ft in user_files.get(uid, []):
            if fn == fname:
                ftype = ft
                break
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        
        if running:
            markup.add(types.InlineKeyboardButton("🔴 Stop", callback_data=f"stop_{uid}_{fname}"))
            markup.add(types.InlineKeyboardButton("🔄 Restart", callback_data=f"restart_{uid}_{fname}"))
        else:
            markup.add(types.InlineKeyboardButton("🟢 Start", callback_data=f"start_{uid}_{fname}"))
        
        markup.add(types.InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_{uid}_{fname}"))
        markup.add(types.InlineKeyboardButton("📜 Logs", callback_data=f"logs_{uid}_{fname}"))
        markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="back_files"))
        
        status = "🟢 RUNNING" if running else "🔴 STOPPED"
        bot.edit_message_text(f"📄 **{fname}** ({ftype})\nStatus: {status}", call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')
    
    elif data.startswith("start_"):
        _, uid, fname = data.split("_", 2)
        uid = int(uid)
        
        folder = get_user_folder(uid)
        path = os.path.join(folder, fname)
        
        if os.path.exists(path):
            threading.Thread(target=run_script, args=(path, uid, folder, fname, call.message)).start()
            bot.answer_callback_query(call.id, "✅ Starting script...")
        else:
            bot.answer_callback_query(call.id, "❌ File not found!", show_alert=True)
    
    elif data.startswith("stop_"):
        _, uid, fname = data.split("_", 2)
        uid = int(uid)
        key = f"{uid}_{fname}"
        
        if key in bot_scripts:
            kill_process_tree(bot_scripts[key])
            del bot_scripts[key]
            bot.answer_callback_query(call.id, "✅ Stopped!")
        else:
            bot.answer_callback_query(call.id, "❌ Not running!", show_alert=True)
    
    elif data.startswith("delete_"):
        _, uid, fname = data.split("_", 2)
        uid = int(uid)
        key = f"{uid}_{fname}"
        
        if key in bot_scripts:
            kill_process_tree(bot_scripts[key])
            del bot_scripts[key]
        
        folder = get_user_folder(uid)
        path = os.path.join(folder, fname)
        log_path = os.path.join(folder, f"{os.path.splitext(fname)[0]}.log")
        
        if os.path.exists(path):
            os.remove(path)
        if os.path.exists(log_path):
            os.remove(log_path)
        
        remove_user_file_db(uid, fname)
        bot.answer_callback_query(call.id, "🗑️ Deleted!")
        bot.edit_message_text(f"✅ Deleted: `{fname}`", call.message.chat.id, call.message.message_id)
    
    elif data.startswith("logs_"):
        _, uid, fname = data.split("_", 2)
        uid = int(uid)
        
        folder = get_user_folder(uid)
        log_path = os.path.join(folder, f"{os.path.splitext(fname)[0]}.log")
        
        if os.path.exists(log_path):
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()[-3000:]
            bot.send_message(call.message.chat.id, f"📜 Logs for `{fname}`:\n```\n{content}\n```", parse_mode='Markdown')
        else:
            bot.answer_callback_query(call.id, "❌ No logs found!", show_alert=True)
    
    elif data == "back_files":
        user_id = call.from_user.id
        files = user_files.get(user_id, [])
        
        if not files:
            bot.edit_message_text("📂 No files uploaded!", call.message.chat.id, call.message.message_id)
            return
        
        markup = types.InlineKeyboardMarkup(row_width=1)
        for fname, ftype in files:
            running = is_bot_running(user_id, fname)
            icon = "🟢" if running else "🔴"
            markup.add(types.InlineKeyboardButton(f"{icon} {fname} ({ftype})", callback_data=f"file_{user_id}_{fname}"))
        
        bot.edit_message_text("📂 Your files:", call.message.chat.id, call.message.message_id, reply_markup=markup)

# ============ CLEANUP ============
def cleanup():
    print("\n🧹 Cleaning up...")
    for key, info in bot_scripts.items():
        kill_process_tree(info)
    print("✅ Cleanup complete!")

atexit.register(cleanup)

# ============ MAIN ============
if __name__ == '__main__':
    show_banner()
    print("\n" + "="*70)
    print("🔧 INITIALIZING @Ritikxyz099 HOSTING...")
    print("="*70)
    
    print(f"📁 Base Directory: {BASE_DIR}")
    print(f"📁 Upload Directory: {UPLOAD_BOTS_DIR}")
    print(f"📁 Data Directory: {IROTECH_DIR}")
    print(f"🤖 Bot Token: {TOKEN[:10]}...")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"🛡️ Admin ID: {ADMIN_ID}")
    print("="*70)
    
    keep_alive()
    
    print("\n🚀 STARTING TELEGRAM BOT...")
    print("="*70)
    print("✅ BOT IS ONLINE AND READY!")
    print("="*70 + "\n")
    
    while True:
        try:
            bot.infinity_polling(timeout=60, long_polling_timeout=30)
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)
