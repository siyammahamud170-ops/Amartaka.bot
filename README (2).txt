AmarTakaOfficialBot - All-in-one starter (safe, simulated)
---------------------------------------------------------
Files in this package:
- main.py          : Telegram bot + Flask admin panel (single-file)
- database.json    : JSON data store (auto-updated)
- admin.json       : Admin username/password (copy into env or edit)
- .env.example     : Copy to .env and put your BOT_TOKEN there
- requirements.txt : Python packages required
- README.txt       : This file

How to use (recommended: Replit / Glitch / Termux / local):
1. Do NOT put your bot token in public. Copy .env.example to .env and set BOT_TOKEN there.
   Example .env content:
     BOT_TOKEN=123456:ABC...
     ADMIN_USER=01326477469
     ADMIN_PASS=Siyam001@
     FLASK_SECRET=some_secret
     PORT=5000

2. Install dependencies:
   pip install -r requirements.txt

3. Run:
   python main.py

4. Open admin panel in browser at http://127.0.0.1:5000/admin-login
   Login with ADMIN_USER and ADMIN_PASS (or use values from .env).

5. Use Telegram bot (/start) to interact.
   - Deposit: send `amount|bkash|trx` (e.g. 100|bkash|TRX123)
   - Withdraw: send `amount|017xxxxxxxx` (only allowed 08:00-14:00 server time)
   - Support: open Support menu and send messages (Deposit Support, Withdraw Support, User Support, Ban Support)

IMPORTANT SAFETY NOTES:
- This is a simulated demo. No real money transfers are implemented.
- Keep your BOT_TOKEN secret. If leaked, revoke it immediately in BotFather and generate a new token.
- If running on a public host, secure the admin panel properly before exposing.

If you want, I can deploy this to Glitch or Replit for you — but I will NOT accept your bot token. I'll guide you how to set it in secrets.
