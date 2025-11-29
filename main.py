"""AmarTakaOfficialBot - All-in-one starter
- Telegram bot (aiogram) + simple Flask admin panel in same process
- Simulated deposits/withdraws only (NO real money)
- Configure BOT_TOKEN in a .env file (see .env.example)
- Admin credentials in admin.json (pre-filled) or via environment variables
"""
import os
import asyncio
import json
from uuid import uuid4
from datetime import datetime, time
from functools import wraps
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    print('ERROR: BOT_TOKEN not set. Copy .env.example to .env and add your token.')
    raise SystemExit(1)

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Text
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from flask import Flask, render_template_string, request, redirect, url_for, session
import threading

# Simple JSON DB helpers
DB_FILE = 'database.json'
def ensure_db():
    if not os.path.exists(DB_FILE):
        data = {'users': [], 'tickets': [], 'withdraws': [], 'deposits': []}
        with open(DB_FILE, 'w') as f:
            json.dump(data, f, indent=2)
ensure_db()

def read_db():
    with open(DB_FILE, 'r') as f:
        return json.load(f)

def write_db(d):
    with open(DB_FILE, 'w') as f:
        json.dump(d, f, indent=2)

def find_user(uid):
    db = read_db()
    for u in db['users']:
        if u['user_id']==uid:
            return u
    return None

def save_user(u):
    db = read_db()
    for i,x in enumerate(db['users']):
        if x['user_id']==u['user_id']:
            db['users'][i]=u
            write_db(db)
            return
    db['users'].append(u)
    write_db(db)

# Flask admin (very simple, session-based)
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET','change_this')
ADMIN_USER = os.getenv('ADMIN_USER') or '01326477469'
ADMIN_PASS = os.getenv('ADMIN_PASS') or 'Siyam001@'

LOGIN_HTML = """<!doctype html><title>Admin Login</title>
<h2>Admin Login</h2>
{% if error %}<p style='color:red'>{{error}}</p>{% endif %}
<form method='post'><input name='username' placeholder='username'><br><input name='password' type='password' placeholder='password'><br><button type='submit'>Login</button></form>
"""

INDEX_HTML = """<!doctype html><title>AmarTaka Admin</title>
<h1>AmarTakaOfficialBot - Admin</h1>
<ul>
  <li><a href='/users'>Users</a></li>
  <li><a href='/support/deposit'>Deposit Support</a></li>
  <li><a href='/support/withdraw'>Withdraw Support</a></li>
  <li><a href='/support/user'>User Support</a></li>
  <li><a href='/support/ban'>Ban Support</a></li>
  <li><a href='/withdraws'>Withdraw Requests</a></li>
  <li><a href='/deposits'>Deposits</a></li>
  <li><a href='/logout'>Logout</a></li>
</ul>
"""

def admin_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return wrapped

@app.route('/admin-login', methods=['GET','POST'])
def admin_login():
    error=None
    if request.method=='POST':
        u=request.form.get('username','').strip()
        p=request.form.get('password','').strip()
        if u==ADMIN_USER and p==ADMIN_PASS:
            session['is_admin']=True
            return redirect(url_for('index'))
        else:
            error='Invalid credentials'
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/')
@admin_required
def index():
    db=read_db()
    stats={'users':len(db['users']),'tickets':len(db['tickets']),'withdraws':len(db['withdraws']),'deposits':len(db['deposits'])}
    return render_template_string(INDEX_HTML, stats=stats)

@app.route('/users')
@admin_required
def users():
    db=read_db()
    return render_template_string('<h2>Users</h2><pre>{{users}}</pre><p><a href="/">Back</a></p>', users=db['users'])

@app.route('/support/<cat>')
@admin_required
def support_list(cat):
    db=read_db()
    ts=[t for t in db['tickets'] if t['category']==cat]
    return render_template_string('<h2>Support {{cat}}</h2><pre>{{ts}}</pre><p><a href="/">Back</a></p>', ts=ts, cat=cat)

@app.route('/withdraws')
@admin_required
def withdraws():
    db=read_db()
    return render_template_string('<h2>Withdraws</h2><pre>{{w}}</pre><p><a href="/">Back</a></p>', w=db['withdraws'])

@app.route('/deposits')
@admin_required
def deposits():
    db=read_db()
    return render_template_string('<h2>Deposits</h2><pre>{{d}}</pre><p><a href="/">Back</a></p>', d=db['deposits'])

# aiogram bot
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

def main_kb():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton('Dashboard'),KeyboardButton('Ads')],[KeyboardButton('Deposit'),KeyboardButton('Withdraw')],[KeyboardButton('Support'),KeyboardButton('Referral')]], resize_keyboard=True)

async def ensure_user(user):
    u=find_user(user.id)
    if not u:
        u={'user_id':user.id,'username':user.username or '','balance':0.0,'banned':False,'lang':'en','referrals':0,'history':{'withdraws':[],'deposits':[]}} 
        save_user(u)
        return u
    return u

@dp.message(commands=['start'])
async def cmd_start(message: types.Message):
    u = await ensure_user(message.from_user)
    if u.get('banned'):
        await message.reply('❌ Your account is BANNED. Please contact Support Center.')
        return
    await message.reply('Welcome to AmarTakaOfficialBot (simulated).', reply_markup=main_kb())

@dp.message(Text(equals='Dashboard', ignore_case=True))
async def dashboard(message: types.Message):
    u=find_user(message.from_user.id) or await ensure_user(message.from_user)
    await message.reply(f"📊 Dashboard\nBalance: {u.get('balance',0)}\nReferrals: {u.get('referrals',0)}") 

@dp.message(Text(equals='Deposit', ignore_case=True))
async def deposit_cmd(message: types.Message):
    await message.reply("To make simulated deposit, send: amount|method|trx (e.g. 100|bkash|TRX123)") 

@dp.message(lambda m: '|' in (m.text or '') and (m.text or '').count('|')>=2)
async def handle_deposit(m: types.Message):
    parts=m.text.split('|')
    try:
        amt=float(parts[0])
    except:
        await m.reply('Invalid amount')
        return
    method=parts[1]; trx='|'.join(parts[2:])
    tid=str(uuid4())[:8]
    ticket={'id':tid,'user_id':m.from_user.id,'category':'deposit','status':'pending','thread':[{'from':'user','text':f"Deposit request: {amt} via {method} trx:{trx}"}],'created_at':datetime.utcnow().isoformat()}
    db=read_db(); db['tickets'].append(ticket); db['deposits'].append({'id':tid,'user_id':m.from_user.id,'amount':amt,'method':method,'trx':trx,'status':'pending'}); write_db(db)
    await m.reply('Deposit request submitted to Deposit Support (simulated).')

@dp.message(Text(equals='Withdraw', ignore_case=True))
async def withdraw_cmd(message: types.Message):
    u=find_user(message.from_user.id)
    if u and u.get('banned'):
        await message.reply('❌ BANNED. Contact support.'); return
    now=datetime.now().time(); start=time(8,0); end=time(14,0)
    if not (start<=now<=end):
        await message.reply('Withdrawals open 08:00 - 14:00.'); return
    await message.reply('To withdraw send: amount|bkash_number (e.g. 50|017xxxxxxxx)')

@dp.message(lambda m: '|' in (m.text or '') and (m.text or '').count('|')==1 and (m.text.split('|')[0].strip().replace('.','',1).isdigit()))
async def handle_withdraw(m: types.Message):
    parts=m.text.split('|'); amt=float(parts[0]); number=parts[1].strip()
    u=find_user(m.from_user.id)
    if u.get('banned'):
        await m.reply('❌ BANNED.'); return
    if u.get('balance',0)<amt:
        await m.reply('Insufficient balance (simulated).'); return
    if amt>0.5*(u.get('balance',0)):
        await m.reply('Cannot withdraw more than 50% at once (simulated).'); return
    u['balance']=round(u.get('balance',0)-amt,2); save_user(u)
    wid=str(uuid4())[:8]; db=read_db(); db['withdraws'].append({'id':wid,'user_id':m.from_user.id,'amount':amt,'number':number,'status':'pending','created_at':datetime.utcnow().isoformat()}); db['tickets'].append({'id':wid,'user_id':m.from_user.id,'category':'withdraw','status':'pending','thread':[{'from':'user','text':f"Withdraw request: {amt} to {number}"}],'created_at':datetime.utcnow().isoformat()}); write_db(db)
    await m.reply(f"Withdraw request submitted (simulated). ID: {wid} Status: pending.")

@dp.message(Text(equals='Support', ignore_case=True))
async def support_menu(m: types.Message):
    kb=ReplyKeyboardMarkup(keyboard=[[KeyboardButton('Deposit Support'),KeyboardButton('Withdraw Support')],[KeyboardButton('User Support'),KeyboardButton('Ban Support')],[KeyboardButton('⬅ Back')]], resize_keyboard=True)
    await m.reply('Choose support category:', reply_markup=kb)

@dp.message(Text(startswith='Deposit Support', ignore_case=True))
async def s_deposit(m: types.Message):
    await m.reply('Send your deposit support message. Example: I uploaded trx but pending...')

@dp.message(Text(startswith='Withdraw Support', ignore_case=True))
async def s_withdraw(m: types.Message):
    await m.reply('Send your withdraw support message. Example: My withdraw id XYZ...')

@dp.message(Text(startswith='User Support', ignore_case=True))
async def s_user(m: types.Message):
    await m.reply('Send your message for general support.')

@dp.message(Text(startswith='Ban Support', ignore_case=True))
async def s_ban(m: types.Message):
    await m.reply('Send your message about ban. Admin will respond.')

@dp.message()
async def catch_all(m: types.Message):
    text=(m.text or '').strip()
    if not text: return
    lowered=text.lower()
    if 'deposit support' in lowered or ('deposit' in lowered and '|' not in lowered): cat='deposit'
    elif 'withdraw support' in lowered or ('withdraw' in lowered and '|' not in lowered): cat='withdraw'
    elif 'ban' in lowered: cat='ban'
    else: cat='user'
    tid=str(uuid4())[:8]
    ticket={'id':tid,'user_id':m.from_user.id,'category':cat,'status':'open','thread':[{'from':'user','text':text}],'created_at':datetime.utcnow().isoformat()}
    db=read_db(); db['tickets'].append(ticket); write_db(db)
    await m.reply(f"Support message created and sent to {cat.title()} Support. Ticket ID: {tid}")

async def notify_user(uid, text):
    try:
        await bot.send_message(uid, f"Admin reply:\n{text}")
    except Exception as e:
        print('Notify error', e)

# start Flask in thread and bot polling
def run_flask():
    app.run(host='0.0.0.0', port=int(os.getenv('PORT',5000)), debug=False)

async def main():
    loop=asyncio.get_running_loop()
    threading.Thread(target=run_flask, daemon=True).start()
    print('Admin panel available at http://127.0.0.1:5000/admin-login')
    await dp.start_polling(bot)

if __name__=='__main__':
    bot = Bot(BOT_TOKEN)
    asyncio.run(main())
