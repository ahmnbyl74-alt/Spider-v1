import http.server
import os
import socketserver
import json
import hashlib
from urllib.parse import parse_qs, urlparse
from http import cookies

# --- [ 1. الإعدادات والبيانات الأساسية ] ---
PORT = int(os.environ.get("PORT", 8080))
DB_FILE = "spider_master_database.json"
SITE_NAME = "Spider Store Pro"
TELEGRAM_USER = "iQSpider" # استبدله بيوزرك هنا

# تصفير قاعدة البيانات عند التشغيل لضمان تطبيق التحديثات البرمجية وكلمة السر 123
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

# --- [ 2. وظائف قاعدة البيانات ] ---
def load_db():
    if not os.path.exists(DB_FILE):
        data = {
            "users": {"admin": {"pass": hash_pass("123"), "balance": 1000.0, "is_admin": True, "phone": "000"}},
            "services": [], 
            "orders": [], 
            "announcement": "مرحباً بك في عالم الفخامة الرقمية!"
        }
        save_db(data)
        return data
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except:
            return load_db()

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- [ 3. التصميم المتكامل (UI/UX) ] ---
def get_master_style():
    return f"""
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
        :root {{ --accent: #f39c12; --glass: rgba(255, 255, 255, 0.1); --border: rgba(255, 255, 255, 0.15); }}
        * {{ box-sizing: border-box; font-family: 'Cairo', sans-serif; transition: 0.3s; }}
        body {{ 
            margin: 0; background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); 
            background-attachment: fixed; color: #fff; direction: rtl; padding-bottom: 120px; min-height: 100vh;
        }}
        .header {{ 
            height: 75px; background: rgba(0, 0, 0, 0.4); backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
            display: flex; align-items: center; justify-content: space-between; 
            padding: 0 20px; border-bottom: 1px solid var(--border); position: sticky; top:0; z-index:1000; 
        }}
        .card {{ 
            background: var(--glass); border: 1px solid var(--border); border-radius: 28px; 
            padding: 22px; margin: 15px; backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        }}
        
        /* قائمة الإعدادات المتكاملة */
        .settings-group {{ margin-bottom: 20px; }}
        .settings-title {{ font-size: 14px; color: var(--accent); margin: 0 15px 10px; font-weight: bold; opacity: 0.8; }}
        .settings-list {{ background: rgba(255,255,255,0.03); border-radius: 20px; overflow: hidden; border: 1px solid var(--border); margin: 0 15px; }}
        .settings-item {{ 
            display: flex; align-items: center; padding: 18px; text-decoration: none; 
            color: #fff; border-bottom: 1px solid var(--border); 
        }}
        .settings-item:last-child {{ border: none; }}
        .settings-item:active {{ background: rgba(255,255,255,0.1); }}
        .settings-item i {{ width: 35px; font-size: 20px; color: var(--accent); }}
        .settings-item .text {{ flex: 1; font-size: 15px; font-weight: 500; }}
        .settings-item .chevron {{ font-size: 12px; opacity: 0.3; }}

        /* المدخلات والأزرار الكبيرة */
        input, select, button {{ 
            width: 100%; padding: 18px; margin-top: 15px; border-radius: 20px; 
            border: 1px solid var(--border); background: rgba(255, 255, 255, 0.05); color: #fff; outline: none;
            font-size: 16px; font-weight: bold;
        }}
        .btn-send {{ 
            background: linear-gradient(45deg, var(--accent), #e67e22); 
            color: #000; font-weight: 900; border: none; cursor: pointer;
            box-shadow: 0 6px 20px rgba(243, 156, 18, 0.4);
        }}
        
        .floating-tg {{
            position: fixed; bottom: 125px; left: 25px; width: 65px; height: 65px;
            background: linear-gradient(45deg, #0088cc, #00aaff); border-radius: 50%; 
            display: flex; align-items: center; justify-content: center; color: white; 
            font-size: 32px; z-index: 3000; box-shadow: 0 8px 25px rgba(0,136,204,0.5); 
            text-decoration: none; animation: pulse 2s infinite;
        }}
        @keyframes pulse {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.08); }} 100% {{ transform: scale(1); }} }}

        .bottom-nav {{ 
            position: fixed; bottom: 25px; left: 20px; right: 20px; 
            height: 85px; background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(25px);
            display: flex; justify-content: space-around; align-items: center; 
            border-radius: 35px; border: 1px solid var(--border); z-index: 2000;
        }}
        .nav-item {{ color: rgba(255,255,255,0.4); text-decoration: none; font-size: 13px; text-align: center; flex:1; }}
        .nav-item.active {{ color: var(--accent); text-shadow: 0 0 10px var(--accent); }}
        .nav-item i {{ font-size: 28px; display: block; margin-bottom: 5px; }}
        
        .stats-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin: 0 15px; }}
        .stat-item {{ background: var(--glass); border: 1px solid var(--border); border-radius: 20px; padding: 15px; text-align: center; }}
        .stat-item i {{ color: var(--accent); display: block; margin-bottom: 8px; font-size: 22px; }}
        .stat-label {{ font-size: 11px; color: rgba(255,255,255,0.6); }}
        .stat-value {{ font-size: 16px; font-weight: bold; }}

        .badge {{ background: var(--accent); color: #000; padding: 4px 12px; border-radius: 12px; font-weight: bold; font-size: 13px; }}
        .order-row {{ border-bottom: 1px solid var(--border); padding: 18px 0; display: flex; justify-content: space-between; align-items: center; }}
    </style>
    <a href="https://t.me/{TELEGRAM_USER}" class="floating-tg" target="_blank"><i class="fab fa-telegram-plane"></i></a>
    """

# --- [ 4. الواجهات ] ---

def get_welcome_page(error=""):
    return f"""<!DOCTYPE html><html lang="ar"><head><meta charset="UTF-8">{get_master_style()}</head>
    <body style="display:flex; flex-direction:column; align-items:center; justify-content:center;">
        <div style="text-align:center; margin: 40px 0;">
            <i class="fas fa-spider" style="font-size:80px; color:var(--accent); filter: drop-shadow(0 0 15px var(--accent));"></i>
            <h1 style="margin:10px 0; font-size:30px;">{SITE_NAME}</h1>
        </div>
        <div class="card" id="login-box" style="width:92%; max-width:400px;">
            <h3 style="text-align:center; margin-top:0;">تسجيل الدخول</h3>
            {f'<p style="color:#ff4757; text-align:center; font-size:14px; background:rgba(255,71,87,0.1); padding:10px; border-radius:15px;">{error}</p>' if error else ''}
            <form action="/auth">
                <input type="text" name="user" placeholder="اسم المستخدم" required>
                <input type="password" name="pass" placeholder="كلمة المرور" required>
                <button type="submit" class="btn-send">دخول الحساب</button>
            </form>
            <p style="text-align:center; margin-top:20px; font-size:14px;">ليس لديك حساب؟ <a href="javascript:toggleForm()" style="color:var(--accent); text-decoration:none;">سجل الآن</a></p>
        </div>
        <div class="card" id="reg-box" style="width:92%; max-width:400px; display:none;">
            <h3 style="text-align:center; margin-top:0;">حساب جديد</h3>
            <form action="/register">
                <input type="text" name="nu" placeholder="اسم المستخدم" required>
                <input type="password" name="np" placeholder="كلمة المرور" required>
                <input type="tel" name="ph" placeholder="رقم الهاتف" required>
                <button type="submit" class="btn-send">تأكيد التسجيل</button>
            </form>
            <p style="text-align:center; margin-top:20px; font-size:14px;">لديك حساب؟ <a href="javascript:toggleForm()" style="color:var(--accent); text-decoration:none;">سجل دخولك</a></p>
        </div>
        <script>function toggleForm(){{ const l=document.getElementById('login-box'), r=document.getElementById('reg-box'); l.style.display=l.style.display==='none'?'block':'none'; r.style.display=r.style.display==='none'?'block':'none'; }}</script>
    </body></html>"""

def get_orders_page(db, user):
    orders = [o for o in db.get("orders", []) if o.get('user') == user]
    orders_html = ""
    for o in reversed(orders):
        status_color = "#2ecc71" if o['status'] == "مكتمل" else "#f39c12"
        orders_html += f"""
        <div class="order-row">
            <div>
                <div style="font-weight:bold;">{o['svc']}</div>
                <div style="font-size:12px; opacity:0.6;">الكمية: {o['qty']} | التكلفة: ${o['cost']:.2f}</div>
            </div>
            <div style="color:{status_color}; font-weight:bold; font-size:14px;">{o['status']}</div>
        </div>"""
    
    if not orders_html:
        orders_html = "<p style='text-align:center; opacity:0.5; margin-top:50px;'>ليس لديك طلبات سابقة</p>"

    return f"""<!DOCTYPE html><html lang="ar"><head><meta charset="UTF-8">{get_master_style()}</head><body>
        <div class="header">
            <div style="font-weight:900; color:var(--accent); font-size:22px;">سجل طلباتي</div>
            <a href="/" style="color:white; font-size:24px;"><i class="fas fa-times"></i></a>
        </div>
        <div class="card">
            {orders_html}
        </div>
        <div class="bottom-nav">
            <a href="/" class="nav-item"><i class="fas fa-home"></i>الرئيسية</a>
            <a href="/settings" class="nav-item"><i class="fas fa-cog"></i>الإعدادات</a>
        </div>
    </body></html>"""


def get_settings_page(db, user):
    u = db["users"][user]
    # زر الإدارة يظهر فقط للأدمن
    admin_item = f"""<a href="/admin_panel" class="settings-item"><i class="fas fa-user-shield"></i><span class="text">لوحة التحكم للإدارة</span><i class="fas fa-chevron-left chevron"></i></a>""" if u.get('is_admin') else ""
    
    return f"""<!DOCTYPE html><html lang="ar"><head><meta charset="UTF-8">{get_master_style()}</head><body>
        <div class="header">
            <div style="font-weight:900; color:var(--accent); font-size:22px;">{SITE_NAME}</div>
            <a href="/" style="color:white; font-size:24px;"><i class="fas fa-times"></i></a>
        </div>
        
        <div class="card" style="text-align:center;">
            <div style="width:80px; height:80px; background:rgba(243,156,18,0.1); border-radius:50%; display:flex; align-items:center; justify-content:center; margin:0 auto 15px; border:1px solid var(--accent);"><i class="fas fa-user" style="font-size:35px; color:var(--accent);"></i></div>
            <h2 style="margin:0;">{user}</h2>
            <div class="badge" style="margin-top:10px;">الرصيد: ${u['balance']:.2f}</div>
        </div>

        <div class="settings-group">
            <div class="settings-title">الحساب والمالية</div>
            <div class="settings-list">
                <a href="/order_history" class="settings-item"><i class="fas fa-history"></i><span class="text">سجل طلباتي</span><i class="fas fa-chevron-left chevron"></i></a>
                <a href="https://t.me/{TELEGRAM_USER}" class="settings-item"><i class="fas fa-wallet"></i><span class="text">شحن الرصيد</span><i class="fas fa-chevron-left chevron"></i></a>
                {admin_item}
            </div>
        </div>

        <div class="settings-group">
            <div class="settings-title">الدعم والمعلومات</div>
            <div class="settings-list">
                <a href="https://t.me/{TELEGRAM_USER}" target="_blank" class="settings-item"><i class="fab fa-telegram-plane"></i><span class="text">قناتنا على التليجرام</span><i class="fas fa-chevron-left chevron"></i></a>
                <a href="/terms" class="settings-item"><i class="fas fa-info-circle"></i><span class="text">شروط الاستخدام</span><i class="fas fa-chevron-left chevron"></i></a>
            </div>
        </div>

        <div class="settings-group" style="margin-bottom:120px;">
            <div class="settings-list">
                <a href="/logout" class="settings-item" style="color:#ff4757;"><i class="fas fa-sign-out-alt" style="color:#ff4757;"></i><span class="text">تسجيل الخروج</span></a>
            </div>
        </div>

        <div class="bottom-nav">
            <a href="/" class="nav-item"><i class="fas fa-home"></i>الرئيسية</a>
            <a href="https://t.me/{TELEGRAM_USER}" class="nav-item"><i class="fab fa-telegram"></i>الدعم الفني</a>
        </div>
    </body></html>"""


def get_admin_page(db):
    # حساب الإحصائيات
    users = db.get("users", {})
    orders = db.get("orders", [])
    services = db.get("services", [])
    providers = db.get("providers", [])
    
    # حساب الأرباح وإجمالي أرصدة المستخدمين
    total_profit = sum(float(o.get('cost', 0)) for o in orders)
    total_balances = sum(float(u.get('balance', 0)) for u in users.values())
    
    # حالة الموقع
    is_active = db.get("is_active", True)
    status_text = "✅ الموقع متصل" if is_active else "❌ وضع الصيانة"
    btn_color = "#2ecc71" if not is_active else "#e74c3c"

    return f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
            :root {{ --accent: #f39c12; --glass: rgba(255, 255, 255, 0.08); --border: rgba(255, 255, 255, 0.1); }}
            * {{ box-sizing: border-box; font-family: 'Cairo', sans-serif; }}
            body {{ margin: 0; background: #0f172a; color: #fff; padding: 20px; }}
            .card {{ background: var(--glass); border: 1px solid var(--border); border-radius: 20px; padding: 20px; margin-bottom: 20px; backdrop-filter: blur(10px); }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
            .stat {{ background: rgba(0,0,0,0.2); padding: 15px; border-radius: 15px; text-align: center; border-bottom: 3px solid var(--accent); }}
            input, select, button {{ width: 100%; padding: 12px; margin: 8px 0; border-radius: 10px; border: 1px solid var(--border); background: rgba(255,255,255,0.05); color: #fff; }}
            .btn-action {{ background: var(--accent); color: #000; font-weight: bold; border: none; cursor: pointer; }}
            .user-row {{ display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid var(--border); }}
            .search-box {{ background: #fff !important; color: #000 !important; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h2 style="text-align:center;"><i class="fas fa-user-shield"></i> لوحة الإدارة</h2>

        <div class="grid">
            <div class="stat"><i class="fas fa-wallet"></i><br>الأرباح<br><b>${total_profit:.2f}</b></div>
            <div class="stat"><i class="fas fa-users"></i><br>الأعضاء<br><b>{len(users)}</b></div>
            <div class="stat"><i class="fas fa-coins"></i><br>إجمالي الأرصدة<br><b>${total_balances:.2f}</b></div>
            <div class="stat"><i class="fas fa-shopping-bag"></i><br>الطلبات<br><b>{len(orders)}</b></div>
        </div>

        <div class="card" style="text-align:center; margin-top:20px;">
            <h4>حالة الموقع حالياً: <span style="color:var(--accent)">{status_text}</span></h4>
            <a href="/admin_action?type=toggle_site"><button style="background:{btn_color}; color:white;">تبديل حالة الموقع</button></a>
        </div>

   <div class="card">
    <h4><i class="fas fa-magic"></i> إضافة خدمة تلقائية (API)</h4>
    <form action="/admin_action" method="GET">
        <input type="hidden" name="type" value="add_full_svc">
        <input name="n" placeholder="اسم الخدمة" required>
        <input name="c" placeholder="الفئة / القسم" required>
        <input type="number" step="0.01" name="p" placeholder="السعر لكل 1000" required>
        <input name="sid" placeholder="ID الخدمة عند المزود" required>
        <input name="url" placeholder="رابط API المزود" required>
        <input name="key" placeholder="API KEY المزود" required>
        <button class="btn-action" style="background:#f39c12;">حفظ وإضافة الخدمة</button>
    </form>
</div>


        <div class="card">
            <h4><i class="fas fa-server"></i> نظام المزودين (يدوي)</h4>
            <form action="/admin_action">
                <input type="hidden" name="type" value="add_prov">
                <input name="n" placeholder="اسم المزود" required>
                <input name="u" placeholder="رابط API المزود" required>
                <input name="k" placeholder="API KEY" required>
                <button class="btn-action" style="background:#34495e; color:white;">ربط المزود</button>
            </form>
        </div>

        <div class="card">
            <h4><i class="fas fa-users-cog"></i> إدارة أرصدة الأعضاء</h4>
            <input type="text" id="userInput" class="search-box" onkeyup="searchUsers()" placeholder="🔍 ابحث عن اسم المستخدم...">
            <div id="userList" style="max-height: 250px; overflow-y: auto;">
                {"".join([f'''
                <div class="user-row" data-name="{name}">
                    <span>{name}<br><small>${u['balance']:.2f}</small></span>
                    <form action="/admin_action" style="display:flex; gap:5px;">
                        <input type="hidden" name="type" value="adj_bal">
                        <input type="hidden" name="u" value="{name}">
                        <input type="number" name="a" placeholder="المبلغ" style="width:70px; margin:0; padding:5px;">
                        <button name="mode" value="plus" style="width:35px; background:#2ecc71; margin:0;">+</button>
                        <button name="mode" value="minus" style="width:35px; background:#e74c3c; margin:0;">-</button>
                    </form>
                </div>''' for name, u in users.items()])}
            </div>
        </div>

        <div class="card">
            <h4><i class="fas fa-trash-alt"></i> حذف الخدمات</h4>
            <div style="max-height: 200px; overflow-y: auto;">
                {"".join([f'<div class="user-row"><span>{s["name"]}</span><a href="/admin_action?type=del_svc&id={s["id"]}" style="color:#ff4757; text-decoration:none;">حذف</a></div>' for s in services])}
            </div>
        </div>

        <script>
            function searchUsers() {{
                let input = document.getElementById('userInput').value.toLowerCase();
                let rows = document.querySelectorAll('.user-row[data-name]');
                rows.forEach(row => {{
                    let name = row.getAttribute('data-name').toLowerCase();
                    row.style.display = name.includes(input) ? "flex" : "none";
                }});
            }}
        </script>
    </body>
    </html>
    """


def get_user_page(db, user):
    u = db["users"][user]
    svcs, orders = db.get("services", []), db.get("orders", [])
    user_orders = [o for o in orders if o.get('user') == user]
    cats = sorted(list(set([s['cat'] for s in svcs])))

    return f"""<!DOCTYPE html><html lang="ar"><head><meta charset="UTF-8">{get_master_style()}</head><body>
        <div class="header">
            <div style="font-weight:900; color:var(--accent); font-size:22px;">{SITE_NAME}</div>
    <a href="/" style="color:white; font-size:24px;"><i class="fas fa-times"></i></a>
        </div>
        
        <div class="card" style="text-align:center;">
            <div style="width:80px; height:80px; background:rgba(243,156,18,0.1); border-radius:50%; display:flex; align-items:center; justify-content:center; margin:0 auto 15px; border:1px solid var(--accent);"><i class="fas fa-user" style="font-size:35px; color:var(--accent);"></i></div>
            <h2 style="margin:0;">{user}</h2>
            <div class="badge" style="margin-top:10px;">الرصيد: ${u['balance']:.2f}</div>
        </div>

        <div class="settings-group">
            <div class="settings-title">الحساب والمالية</div>
            <div class="settings-list">
                <a href="/order_history" class="settings-item"><i class="fas fa-history"></i><span class="text">سجل طلباتي</span><i class="fas fa-chevron-left chevron"></i></a>
                <a href="https://t.me/{TELEGRAM_USER}" class="settings-item"><i class="fas fa-wallet"></i><span class="text">شحن الرصيد</span><i class="fas fa-chevron-left chevron"></i></a>
                {admin_item}
            </div>
        </div>

        <div class="settings-group">
            <div class="settings-title">الدعم والمعلومات</div>
            <div class="settings-list">
                <a href="https://t.me/{TELEGRAM_USER}" target="_blank" class="settings-item"><i class="fab fa-telegram-plane"></i><span class="text">قناتنا على التليجرام</span><i class="fas fa-chevron-left chevron"></i></a>
                <a href="/terms" class="settings-item"><i class="fas fa-info-circle"></i><span class="text">شروط الاستخدام</span><i class="fas fa-chevron-left chevron"></i></a>
            </div>
        </div>

        <div class="settings-group" style="margin-bottom:120px;">
            <div class="settings-list">
                <a href="/logout" class="settings-item" style="color:#ff4757;"><i class="fas fa-sign-out-alt" style="color:#ff4757;"></i><span class="text">تسجيل الخروج</span></a>
            </div>
        </div>

        <div class="bottom-nav">
            <a href="/" class="nav-item"><i class="fas fa-home"></i>الرئيسية</a>
            <a href="https://t.me/{TELEGRAM_USER}" class="nav-item"><i class="fab fa-telegram"></i>الدعم الفني</a>
        </div>
    </body></html>"""


def get_admin_page(db):
    # حساب الإحصائيات
    users = db.get("users", {})
    orders = db.get("orders", [])
    services = db.get("services", [])
    providers = db.get("providers", [])
    
    # حساب الأرباح وإجمالي أرصدة المستخدمين
    total_profit = sum(float(o.get('cost', 0)) for o in orders)
    total_balances = sum(float(u.get('balance', 0)) for u in users.values())
    
    # حالة الموقع
    is_active = db.get("is_active", True)
    status_text = "✅ الموقع متصل" if is_active else "❌ وضع الصيانة"
    btn_color = "#2ecc71" if not is_active else "#e74c3c"

    return f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
            :root {{ --accent: #f39c12; --glass: rgba(255, 255, 255, 0.08); --border: rgba(255, 255, 255, 0.1); }}
            * {{ box-sizing: border-box; font-family: 'Cairo', sans-serif; }}
            body {{ margin: 0; background: #0f172a; color: #fff; padding: 20px; }}
            .card {{ background: var(--glass); border: 1px solid var(--border); border-radius: 20px; padding: 20px; margin-bottom: 20px; backdrop-filter: blur(10px); }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
            .stat {{ background: rgba(0,0,0,0.2); padding: 15px; border-radius: 15px; text-align: center; border-bottom: 3px solid var(--accent); }}
            input, select, button {{ width: 100%; padding: 12px; margin: 8px 0; border-radius: 10px; border: 1px solid var(--border); background: rgba(255,255,255,0.05); color: #fff; }}
            .btn-action {{ background: var(--accent); color: #000; font-weight: bold; border: none; cursor: pointer; }}
            .user-row {{ display: flex; justify-content: space-between; align-items: center; padding: 10px; border-bottom: 1px solid var(--border); }}
            .search-box {{ background: #fff !important; color: #000 !important; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h2 style="text-align:center;"><i class="fas fa-user-shield"></i> لوحة الإدارة</h2>

        <div class="grid">
            <div class="stat"><i class="fas fa-wallet"></i><br>الأرباح<br><b>${total_profit:.2f}</b></div>
            <div class="stat"><i class="fas fa-users"></i><br>الأعضاء<br><b>{len(users)}</b></div>
            <div class="stat"><i class="fas fa-coins"></i><br>إجمالي الأرصدة<br><b>${total_balances:.2f}</b></div>
            <div class="stat"><i class="fas fa-shopping-bag"></i><br>الطلبات<br><b>{len(orders)}</b></div>
        </div>

        <div class="card" style="text-align:center; margin-top:20px;">
            <h4>حالة الموقع حالياً: <span style="color:var(--accent)">{status_text}</span></h4>
            <a href="/admin_action?type=toggle_site"><button style="background:{btn_color}; color:white;">تبديل حالة الموقع</button></a>
        </div>

   <div class="card">
    <h4><i class="fas fa-magic"></i> إضافة خدمة تلقائية (API)</h4>
    <form action="/admin_action" method="GET">
        <input type="hidden" name="type" value="add_full_svc">
        <input name="n" placeholder="اسم الخدمة" required>
        <input name="c" placeholder="الفئة / القسم" required>
        <input type="number" step="0.01" name="p" placeholder="السعر لكل 1000" required>
        <input name="sid" placeholder="ID الخدمة عند المزود" required>
        <input name="url" placeholder="رابط API المزود" required>
        <input name="key" placeholder="API KEY المزود" required>
        <button class="btn-action" style="background:#f39c12;">حفظ وإضافة الخدمة</button>
    </form>
</div>


        <div class="card">
            <h4><i class="fas fa-server"></i> نظام المزودين (يدوي)</h4>
            <form action="/admin_action">
                <input type="hidden" name="type" value="add_prov">
                <input name="n" placeholder="اسم المزود" required>
                <input name="u" placeholder="رابط API المزود" required>
                <input name="k" placeholder="API KEY" required>
                <button class="btn-action" style="background:#34495e; color:white;">ربط المزود</button>
            </form>
        </div>

        <div class="card">
            <h4><i class="fas fa-users-cog"></i> إدارة أرصدة الأعضاء</h4>
            <input type="text" id="userInput" class="search-box" onkeyup="searchUsers()" placeholder="🔍 ابحث عن اسم المستخدم...">
            <div id="userList" style="max-height: 250px; overflow-y: auto;">
                {"".join([f'''
                <div class="user-row" data-name="{name}">
                    <span>{name}<br><small>${u['balance']:.2f}</small></span>
                    <form action="/admin_action" style="display:flex; gap:5px;">
                        <input type="hidden" name="type" value="adj_bal">
                        <input type="hidden" name="u" value="{name}">
                        <input type="number" name="a" placeholder="المبلغ" style="width:70px; margin:0; padding:5px;">
                        <button name="mode" value="plus" style="width:35px; background:#2ecc71; margin:0;">+</button>
                        <button name="mode" value="minus" style="width:35px; background:#e74c3c; margin:0;">-</button>
                    </form>
                </div>''' for name, u in users.items()])}
            </div>
        </div>

        <div class="card">
            <h4><i class="fas fa-trash-alt"></i> حذف الخدمات</h4>
            <div style="max-height: 200px; overflow-y: auto;">
                {"".join([f'<div class="user-row"><span>{s["name"]}</span><a href="/admin_action?type=del_svc&id={s["id"]}" style="color:#ff4757; text-decoration:none;">حذف</a></div>' for s in services])}
            </div>
        </div>

        <script>
            function searchUsers() {{
                let input = document.getElementById('userInput').value.toLowerCase();
                let rows = document.querySelectorAll('.user-row[data-name]');
                rows.forEach(row => {{
                    let name = row.getAttribute('data-name').toLowerCase();
                    row.style.display = name.includes(input) ? "flex" : "none";
                }});
            }}
        </script>
    </body>
    </html>
    """


def get_user_page(db, user):
    u = db["users"][user]
    svcs, orders = db.get("services", []), db.get("orders", [])
    user_orders = [o for o in orders if o.get('user') == user]
    cats = sorted(list(set([s['cat'] for s in svcs])))

    return f"""<!DOCTYPE html><html lang="ar"><head><meta charset="UTF-8">{get_master_style()}</head><body>
        <div class="header">
            <div style="font-weight:900; color:var(--accent); font-size:22px;">{SITE_NAME}</div>
            <a href="/settings" style="color:white; font-size:24px;"><i class="fas fa-cog"></i></a>
        </div>
        
        <div class="stats-grid" style="margin-top:20px;">
            <div class="stat-item"><i class="fas fa-wallet"></i><div class="stat-label">رصيدك</div><div class="stat-value">${u['balance']:.2f}</div></div>
            <div class="stat-item"><i class="fas fa-shopping-bag"></i><div class="stat-label">طلباتك</div><div class="stat-value">{len(user_orders)}</div></div>
            <div class="stat-item"><i class="fas fa-star"></i><div class="stat-label">الفئة</div><div class="stat-value">VIP</div></div>
        </div>

        <div class="card">
            <h4><i class="fas fa-shopping-cart"></i> إنشاء طلب جديد</h4>
            <input type="text" placeholder="🔍 ابحث عن خدمة..." oninput="doSearch(this.value)">
            <form action="/place_order_api" style="margin-top:10px;">
                <select id="c_sel" onchange="loadSvcs(this.value)" required><option value="">-- اختر القسم --</option>{"".join([f'<option value="{c}">{c}</option>' for c in cats])}</select>
                <select name="sid" id="s_sel" required><option value="">-- اختر الخدمة --</option></select>
                <input type="text" name="link" placeholder="رابط الحساب / المنشور" required>
                <input type="number" name="qty" placeholder="الكمية المطلوبة" required>
                <button type="submit" class="btn-send">تأكيد الطلب</button>
            </form>
        </div>

        <div class="bottom-nav">
            <a href="/" class="nav-item active"><i class="fas fa-home"></i>الرئيسية</a>
            <a href="https://t.me/{TELEGRAM_USER}" class="nav-item"><i class="fab fa-telegram"></i>الدعم الفني</a>
        </div>
        <script>
            const data = {json.dumps(svcs)};
            function doSearch(v){{
                const s = document.getElementById('s_sel'); s.innerHTML = '<option value="">نتائج البحث...</option>';
                data.filter(i => i.name.toLowerCase().includes(v.toLowerCase())).forEach(i => {{
                    let o = document.createElement('option'); o.value = i.id; o.textContent = i.name + " ($" + i.price + ")"; s.appendChild(o);
                }});
            }}
            function loadSvcs(c){{
                const s = document.getElementById('s_sel'); s.innerHTML = '<option value="">اختر الخدمة...</option>';
                data.filter(i => i.cat === c).forEach(i => {{
                    let o = document.createElement('option'); o.value = i.id; o.textContent = i.name; s.appendChild(o);
                }});
            }}
        </script>
    </body></html>"""

# --- [ 5. محرك السيرفر ] ---

class SpiderServer(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        db = load_db()
        ck = http.cookies.SimpleCookie(self.headers.get('Cookie'))
        user = ck['session_user'].value if 'session_user' in ck else None
        p, q = urlparse(self.path).path, parse_qs(urlparse(self.path).query)
        
        # دوال المساعدة للرد والتوجيه
        def res(h): 
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(h.encode('utf-8'))
            
        def go(l): 
            self.send_response(302)
            self.send_header("Location", l)
            self.end_headers()

        # 1. نظام الدخول والخروج
        if p == "/auth":
            u_in, p_in = q.get('user',[''])[0], q.get('pass',[''])[0]
            if u_in in db['users'] and db['users'][u_in]['pass'] == hash_pass(p_in):
                self.send_response(302)
                self.send_header("Set-Cookie", f"session_user={u_in}; Path=/; HttpOnly")
                self.send_header("Location", "/")
                self.end_headers()
            else: res("خطأ في بيانات الدخول!")
            return

        if p == "/logout":
            self.send_response(302)
            self.send_header("Set-Cookie", "session_user=; Max-Age=0; Path=/")
            self.send_header("Location", "/")
            self.end_headers()
            return

        if not user: res(get_welcome_page()); return

        # 2. معالجة أوامر الأزرار (Admin Action)
        if p == "/admin_action":
            # 1. تعريف المتغير t أولاً
            t = q.get('type', [''])[0]
            
            # 2. فحص نوع الأكشن
            if t == "add_full_svc":
                new_id = str(len(db.get('services', [])) + 1)
                db.setdefault('services', []).append({
                    "id": new_id,
                    "name": q.get('n', [''])[0],
                    "cat": q.get('c', [''])[0],
                    "price": float(q.get('p', ['0'])[0]),
                    "remote_id": q.get('sid', [''])[0],
                    "api_url": q.get('url', [''])[0],
                    "api_key": q.get('key', [''])[0]
                })
                save_db(db)
                go("/admin_panel")
                return

            elif t == "toggle_site":
                db['is_active'] = not db.get('is_active', True)
                save_db(db)
                go("/admin_panel")
                return

        # 3. معالجة طلبات المستخدمين (Place Order)
        if p == "/place_order_api":
            sid, qty = q.get('sid',[''])[0], int(q.get('qty',['0'])[0])
            svc = next((s for s in db.get('services', []) if s['id'] == sid), None)
            if svc and qty > 0:
                cost = (float(svc['price']) / 1000) * qty
                if db['users'][user]['balance'] >= cost:
                    db['users'][user]['balance'] -= cost
                    db['orders'].append({"user": user, "svc": svc['name'], "qty": qty, "cost": cost, "status": "قيد التنفيذ"})
                    save_db(db)
                    res("<html><script>alert('تم الطلب بنجاح!'); window.location='/';</script></html>")
                    return
            res("<html><script>alert('فشل! تأكد من الرصيد والكمية'); window.location='/';</script></html>"); return

        # --- [ 4. توجيه الصفحات - نسخة شاملة ومصلحة ] ---
        # ملاحظة: تم وضع احتمالات للمفرد والجمع (setting و settings) لضمان استجابة الأزرار
                # 4. توجيه الصفحات
        if p == "/admin_panel":
            res(get_admin_page(db))
            
        elif p == "/settings" or p == "/setting":
            res(get_settings_page(db, user))

        elif p == "/order_history" or p == "/orders":
            res(get_orders_page(db, user))

        elif p == "/logout" or p == "/exit":
            self.send_response(302)
            self.send_header("Set-Cookie", "session_user=; Max-Age=0; Path=/")
            self.send_header("Location", "/")
            self.end_headers()
            return

        elif p == "/place_order_api":
            # معالجة طلبات الخدمات
            sid, qty = q.get('sid',[''])[0], int(q.get('qty',['0'])[0])
            svc = next((s for s in db.get('services', []) if s['id'] == sid), None)
            if svc and qty > 0:
                cost = (float(svc['price']) / 1000) * qty
                if db['users'][user]['balance'] >= cost:
                    db['users'][user]['balance'] -= cost
                    db['orders'].append({"user": user, "svc": svc['name'], "qty": qty, "cost": cost, "status": "قيد التنفيذ"})
                    save_db(db)
                    res("<html><script>alert('تم الطلب بنجاح!'); window.location='/';</script></html>")
                    return
            res("<html><script>alert('فشل! تأكد من الرصيد والكمية'); window.location='/';</script></html>"); return

        else:
            # الصفحة الرئيسية الافتراضية
            res(get_user_page(db, user))

# --- [ 5. تشغيل المحرك ] ---
if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), SpiderServer) as httpd:
        print(f"🚀 السيرفر يعمل الآن على الرابط: http://localhost:{PORT}")
        httpd.serve_forever()
    
