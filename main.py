import http.server
import socketserver
import json
import os
from urllib.parse import parse_qs, urlparse
from http import cookies
from collections import Counter

# --- [ الإعدادات المركزية ] ---
PORT = int(os.environ.get("PORT", 5000))
DB_FILE = "spider_master_database.json"
SITE_NAME = "Spider iQ"

# --- [ محرك البيانات المركزي ] ---
def load_db():
    if not os.path.exists(DB_FILE):
        data = {
            "users": {
                "admin": {"pass": "iQSpiderSpidernbel3030", "balance": 10000.0, "spent": 0.0, "phone": "077", "uid": "8249124053", "is_admin": True}
            },
            "services": [], "orders": [], "providers": [], "vouchers": [], "settings": {"maintenance": False}
        }
        save_db(data)
        return data
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        try:
            db = json.load(f)
            keys = ["users", "services", "orders", "providers", "vouchers", "settings"]
            for k in keys: 
                if k not in db: db[k] = [] if k != "users" and k != "settings" else {}
            return db
        except:
            return {"users": {}, "services": [], "orders": [], "providers": [], "vouchers": [], "settings": {}}

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- [ نظام التصميم الفاخر - Ultimate UI ] ---
def get_master_style():
    return f"""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        :root {{ --gold: #f39c12; --bg: #070b14; --card: rgba(21, 31, 51, 0.85); --text: #f1f5f9; --danger: #ef4444; --green: #2ecc71; --blue: #3498db; }}
        body.light-mode {{ --bg: #f0f2f5; --card: rgba(255, 255, 255, 0.95); --text: #1e293b; }}
        * {{ box-sizing: border-box; font-family: 'Cairo', sans-serif; transition: 0.3s; }}
        body {{ margin: 0; background: var(--bg); color: var(--text); direction: rtl; min-height: 100vh; overflow-x: hidden; }}
        .header {{ height: 70px; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; background: rgba(21, 31, 51, 0.98); border-bottom: 2.5px solid var(--gold); position: sticky; top: 0; z-index: 2000; box-shadow: 0 4px 20px rgba(0,0,0,0.4); }}
        .settings-menu {{ position: absolute; top: 75px; left: 15px; background: var(--card); backdrop-filter: blur(30px); border: 1.5px solid var(--gold); border-radius: 20px; width: 280px; display: none; flex-direction: column; padding: 10px; z-index: 3000; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
        .settings-item {{ display: flex; align-items: center; gap: 14px; padding: 14px; color: var(--text); text-decoration: none; border-bottom: 1px solid rgba(255,255,255,0.05); cursor: pointer; font-size: 14px; border-radius: 12px; }}
        .settings-item i {{ color: var(--gold); width: 25px; text-align: center; font-size: 18px; }}
        .scroll-content {{ padding: 15px; display: flex; flex-direction: column; align-items: center; padding-bottom: 120px; }}
        .card {{ background: var(--card); border-radius: 28px; padding: 22px; margin-bottom: 22px; width: 100%; max-width: 680px; border: 1px solid rgba(255,255,255,0.08); backdrop-filter: blur(12px); box-shadow: 0 15px 35px rgba(0,0,0,0.4); }}
        .stat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; width: 100%; max-width: 680px; margin-bottom: 22px; }}
        .stat-box {{ background: var(--card); padding: 18px; border-radius: 22px; text-align: center; border-right: 5px solid var(--gold); box-shadow: 0 8px 15px rgba(0,0,0,0.2); }}
        input, select {{ width: 100%; padding: 16px; margin: 10px 0; border-radius: 18px; border: 1px solid var(--gold); background: rgba(0,0,0,0.4); color: white; outline: none; }}
        .btn {{ width: 100%; padding: 18px; border: none; border-radius: 18px; font-weight: 900; cursor: pointer; color: white; font-size: 16px; display: flex; align-items: center; justify-content: center; gap: 10px; text-decoration: none; }}
        .btn-gold {{ background: linear-gradient(135deg, #f39c12, #d35400); }}
        .btn-blue {{ background: #3498db; }}
        .btn-danger {{ background: #e74c3c; }}
        .cost-badge {{ background: rgba(46, 204, 113, 0.1); color: #2ecc71; padding: 12px; border-radius: 15px; text-align: center; font-weight: bold; margin-top: 10px; border: 1px dashed #2ecc71; display: none; width: 100%; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px; }}
        th, td {{ padding: 14px 10px; border-bottom: 1px solid rgba(255,255,255,0.05); text-align: center; }}
        .bottom-nav {{ position: fixed; bottom: 0; width: 100%; height: 80px; background: rgba(21, 31, 51, 0.98); border-top: 2px solid var(--gold); display: flex; justify-content: space-around; align-items: center; z-index: 2000; }}
        .nav-item {{ color: #8a99af; text-decoration: none; text-align: center; font-size: 12px; flex: 1; }}
        .nav-item i {{ font-size: 24px; display: block; margin-bottom: 5px; }}
        .nav-item.active {{ color: var(--gold); }}
        .svc-item {{ padding:15px; border-bottom:1px solid rgba(255,255,255,0.05); cursor:pointer; display: none; }}
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script>
        let selectedPrice = 0;
        function toggleMenu(id) {{
            let m = document.getElementById(id);
            if (m) {{
                m.style.display = (m.style.display === 'none' || m.style.display === '') ? 'block' : 'none';
            }}
        }}
        
        function filterServices() {{
            let cat = document.getElementById('category_select').value;
            let items = document.querySelectorAll('.svc-item');
            document.getElementById('selected_text').innerText = "-- اختر الخدمة --";
            document.getElementById('service_id').value = "";
            document.getElementById('cost_display').style.display = 'none';
            selectedPrice = 0;

            items.forEach(item => {{
                if (item.getAttribute('data-cat') === cat) {{
                    item.style.display = 'block';
                }} else {{
                    item.style.display = 'none';
                }}
            }});
        }}

        function selectService(id, name, price) {{
            selectedPrice = price;
            document.getElementById('selected_text').innerText = name + " ($" + price + ")";
            document.getElementById('service_id').value = id;
            document.getElementById('svc_list').style.display = 'none';
            calculateCost();
        }}

        function calculateCost() {{
            let qty = document.getElementById('order_qty').value;
            let badge = document.getElementById('cost_display');
            if (selectedPrice > 0 && qty > 0) {{
                let total = (qty / 1000) * selectedPrice;
                badge.style.display = 'block';
                badge.innerText = "التكلفة الإجمالية: $" + total.toFixed(4);
            }} else {{
                badge.style.display = 'none';
            }}
        }}

        function toggleTheme() {{
            document.body.classList.toggle('light-mode');
        }}

        function showAccountInfo(name, bal, spent) {{
            alert("👤 حسابي\\n----------\\nالإسم: " + name + "\\nالرصيد الحالي: $" + bal + "\\nإجمالي الإنفاق: $" + spent);
        }}
    </script>
    """

# --- [ الواجهة المحدثة: بوابة الدخول ] ---
def get_login_page():
    return f"""<!DOCTYPE html><html lang="ar"><head><meta charset="UTF-8">{get_master_style()}</head>
    <body style="display:flex; justify-content:center; align-items:center; min-height:100vh; padding:20px;">
        <div style="text-align:center; width:100%; max-width:450px; animation: slideUp 0.8s ease;">
            
            <div style="display:inline-flex; align-items:center; gap:10px; background:rgba(255,255,255,0.1); padding:8px 20px; border-radius:50px; border:1px solid rgba(255,255,255,0.2); margin-bottom:25px; color:#fff; font-size:13px;">
                <i class="fas fa-bolt" style="color:var(--gold);"></i> منصة خدمات السوشيال ميديا الاحترافية
            </div>

            <h1 style="font-size:38px; font-weight:900; line-height:1.3; margin-bottom:15px; color:#fff; text-shadow: 0 4px 10px rgba(0,0,0,0.3);">
                نمّي حضورك<br>على <span style="color:var(--gold);">السوشيال ميديا</span><br>بسرعة وموثوقية
            </h1>
            
            <p style="color:rgba(255,255,255,0.7); font-size:15px; margin-bottom:40px; line-height:1.6;">
                أكبر منصة عراقية لخدمات التواصل الاجتماعي - متابعين، مشاهدات، إعجابات وأكثر بأسعار تنافسية وتنفيذ فوري.
            </p>

            <div id="login_form">
                <form action="/auth_action">
                    <div style="margin-bottom:15px;">
                        <input name="user" placeholder="اسم المستخدم" required style="border-radius:50px; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.2); padding:18px 25px;">
                        <input name="pass" type="password" placeholder="كلمة المرور" required style="border-radius:50px; background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.2); padding:18px 25px;">
                    </div>
                    <button class="btn" style="background:#fff; color:#070b14; border-radius:50px; font-weight:700; margin-bottom:15px; height:60px; box-shadow:0 10px 20px rgba(0,0,0,0.2);">
                         ابدأ الآن مجاناً <i class="fas fa-rocket" style="margin-right:8px;"></i>
                    </button>
                </form>
                <button onclick="switchAuth('signup')" style="background:transparent; color:#fff; border:2px solid rgba(255,255,255,0.3); border-radius:50px; width:100%; height:60px; font-weight:600; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:10px;">
                    <i class="fas fa-sign-in-alt"></i> تسجيل حساب جديد
                </button>
            </div>

            <div id="signup_form" style="display:none;">
                <form action="/signup_action">
                    <input name="user" placeholder="اليوزر نيم" required style="border-radius:50px;">
                    <input name="pass" type="password" placeholder="كلمة المرور" required style="border-radius:50px;">
                    <input name="tele_id" placeholder="رقم ايدي تليجرام (ID)" required style="border-radius:50px;">
                    <button class="btn btn-gold" style="border-radius:50px; height:60px; margin-top:15px;">تأكيد التسجيل <i class="fas fa-user-plus"></i></button>
                </form>
                <button class="btn btn-danger" style="border-radius:50px; height:60px; margin-top:10px; background:transparent; border:1px solid var(--danger);" onclick="switchAuth('login')">رجوع للدخول</button>
            </div>

        </div>
        
        <script>
            function switchAuth(mode) {{
                document.getElementById('login_form').style.display = mode === 'login' ? 'block' : 'none';
                document.getElementById('signup_form').style.display = mode === 'signup' ? 'block' : 'none';
            }}
        </script>
    </body></html>"""


def get_admin_dashboard(db):
    total_users = len(db['users'])
    total_balance = sum(u.get('balance', 0) for u in db['users'].values())
    total_orders = len(db['orders'])
    total_profit = sum(u.get('spent', 0) for u in db['users'].values())
    
    prov_rows = "".join([f"<tr><td>{p['name']}</td><td><span style='color:var(--green)'>نشط</span></td></tr>" for p in db.get('providers', [])])
    svc_rows = "".join([f"<tr><td>{s.get('cat','عام')}</td><td>{s['name']}</td><td><a href='/admin_act?act=del_svc&sid={s['id']}' style='color:var(--danger)'><i class='fas fa-trash'></i></a></td></tr>" for s in db['services']])

    return f"""<!DOCTYPE html><html lang="ar"><head><meta charset="UTF-8">{get_master_style()}</head>
    <body>
        <div class="header"><div style="font-weight:900; color:var(--gold);">لوحة الإدارة</div><a href="/" style="color:white;"><i class="fas fa-home fa-lg"></i></a></div>
        <div class="scroll-content">
            <div class="stat-grid">
                <div class="stat-box" style="border-right-color:var(--blue);"><small>المستخدمين</small><br><b>{total_users}</b></div>
                <div class="stat-box" style="border-right-color:var(--green);"><small>إجمالي الرصيد</small><br><b>${total_balance:.2f}</b></div>
                <div class="stat-box" style="border-right-color:var(--gold);"><small>إجمالي الأرباح</small><br><b>${total_profit:.2f}</b></div>
                <div class="stat-box" style="border-right-color:var(--danger);"><small>الطلبات</small><br><b>{total_orders}</b></div>
            </div>

            <div class="card">
                <h3>إدارة رصيد الأعضاء</h3>
                <form action="/admin_act">
                    <input name="target_user" placeholder="اسم المستخدم">
                    <input name="amount" placeholder="المبلغ">
                    <div style="display:flex; gap:10px;">
                        <button name="act" value="charge" class="btn btn-blue" style="flex:1;">شحن</button>
                        <button name="act" value="remove_balance" class="btn btn-danger" style="flex:1;">خصم</button>
                    </div>
                </form>
            </div>

            <div class="card">
                <h3><i class="fas fa-plug"></i> إضافة مزود (API Provider)</h3>
                <form action="/admin_act">
                    <input type="hidden" name="act" value="add_prov">
                    <input name="prov_name" placeholder="اسم المزود">
                    <input name="prov_url" placeholder="رابط الـ API">
                    <input name="prov_key" placeholder="API Key">
                    <button class="btn btn-blue">حفظ المزود</button>
                </form>
                <table><thead><tr><th>المزود</th><th>الحالة</th></tr></thead><tbody>{prov_rows or "<tr><td colspan='2'>لا يوجد مزودين</td></tr>"}</tbody></table>
            </div>

            <div class="card">
                <h3>إدارة الخدمات والفئات</h3>
                <form action="/admin_act">
                    <input type="hidden" name="act" value="add_svc">
                    <input name="cat" placeholder="الفئة (مثل: إنستقرام، تيك توك)">
                    <input name="n" placeholder="اسم الخدمة">
                    <input name="p" placeholder="السعر لكل 1000">
                    <input name="id" placeholder="ID الخدمة">
                    <button class="btn btn-gold">إضافة الخدمة للفئة</button>
                </form>
                <table><thead><tr><th>الفئة</th><th>الخدمة</th><th>حذف</th></tr></thead><tbody>{svc_rows or "<tr><td colspan='3'>لا يوجد</td></tr>"}</tbody></table>
            </div>
        </div>
    </body></html>"""

def get_user_page(db, username):
    u = db["users"].get(username, {})
    categories = sorted(list(set([s.get('cat', 'عام') for s in db['services']])))
    cat_options = "".join([f'<option value="{c}">{c}</option>' for c in categories])
    svc_items = "".join([f'<div class="svc-item" data-cat="{s.get("cat","عام")}" onclick="selectService(\'{s["id"]}\', \'{s["name"]}\', {s["price"]})">{s["name"]} (${s["price"]})</div>' for s in db['services']])
    orders_log = "".join([f'<div style="padding:15px; background:rgba(0,0,0,0.3); border-radius:15px; margin-bottom:10px; border-right:4px solid var(--gold);"><b>{o["service"]}</b><br><small>الحالة: مكتمل</small></div>' for o in db['orders'] if o['user'] == username][::-1])
    
    return f"""<!DOCTYPE html><html lang="ar"><head><meta charset="UTF-8">{get_master_style()}</head>
    <body>
        <div class="header"><div style="font-weight:900; color:var(--gold); font-size:22px;">{SITE_NAME}</div><i class="fas fa-cog fa-lg" style="color:var(--gold); cursor:pointer;" onclick="toggleMenu('quick_settings')"></i></div>
        
        <div id="quick_settings" class="settings-menu">
            <div class="settings-item" onclick="showAccountInfo('{username}', {u.get('balance',0)}, {u.get('spent',0)})"><i class="fas fa-id-card"></i> حسابي</div>
            <div class="settings-item" onclick="toggleTheme()"><i class="fas fa-moon"></i> الوضع الليلي</div>
            <a href="https://t.me/alw623" class="settings-item"><i class="fab fa-telegram-plane"></i> الدعم الفني</a>
            {f'<a href="/admin_panel" class="settings-item" style="color:var(--gold)"><i class="fas fa-user-shield"></i> لوحة الإدارة</a>' if username == "admin" else ''}
            <a href="/logout" class="settings-item" style="color:var(--danger)"><i class="fas fa-sign-out-alt"></i> خروج</a>
        </div>

        <div class="scroll-content">
            <div class="stat-grid">
                <div class="stat-box" style="border-right-color:var(--green);"><small>رصيدك</small><div style="font-size:22px; font-weight:900; color:var(--green);">${u.get('balance',0):.2f}</div></div>
                <div class="stat-box" style="border-right-color:var(--danger);"><small>إنفاقك</small><div style="font-size:22px; font-weight:900; color:var(--danger);">${u.get('spent',0):.2f}</div></div>
            </div>

            <div class="card">
                <h3>طلب خدمة جديدة</h3>
                <form action="/place_order">
           <div style="position: relative; width: 100%; margin: 15px 0;">
    <div onclick="document.getElementById('cat_opts').style.display = (document.getElementById('cat_opts').style.display === 'block' ? 'none' : 'block')" 
         style="background: rgba(255,255,255,0.05); border: 1.5px solid var(--blue); border-radius: 18px; padding: 18px 25px; color: var(--text); cursor: pointer; display: flex; justify-content: space-between; align-items: center; font-weight: 600;">
        <span id="cat_txt">-- اختر الفئة (تطبيق) --</span>
        <i class="fas fa-layer-group" style="color:var(--blue);"></i>
    </div>
    
    <div id="cat_opts" style="position: absolute; top: 110%; left: 0; right: 0; background: #0b132b; border: 1px solid var(--blue); border-radius: 20px; overflow-y: auto; max-height: 200px; display: none; z-index: 1000; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
        { "".join([f'''<div onclick="document.getElementById('cat_txt').innerText='{c}'; document.getElementById('category_select').value='{c}'; document.getElementById('cat_opts').style.display='none'; filterServices();" 
                      style="padding: 15px 25px; cursor: pointer; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 14px;">
                      <i class="fas fa-star" style="color:var(--gold); margin-left: 10px; font-size: 10px;"></i> {c}
                   </div>''' for c in categories]) }
    </div>
    <input type="hidden" name="cat" id="category_select">
</div>


                    <div onclick="toggleMenu('svc_list')" style="background:rgba(0,0,0,0.4); border:1.5px solid var(--gold); padding:16px; border-radius:18px; cursor:pointer; display:flex; justify-content:space-between; margin-top:10px;">
                        <span id="selected_text">-- اختر الخدمة --</span><i class="fas fa-chevron-down"></i>
                    </div>
                    <div id="svc_list" class="select-items" style="display:none; background:#0b132b; border:1px solid var(--gold); border-radius:20px; margin-top:5px; max-height:200px; overflow-y:auto;">
                        {svc_items or '<div style="padding:15px;">يرجى اختيار فئة أولاً</div>'}
                    </div>

                    <input type="hidden" name="sid" id="service_id" required>
                    <input name="link" placeholder="الرابط / اليوزر" required>
                    <input name="qty" id="order_qty" type="number" placeholder="الكمية المطلوبة" oninput="calculateCost()" required>
                    
                    <div id="cost_display" class="cost-badge"></div>
                    
                    <button class="btn btn-gold" style="margin-top:15px;">تأكيد الطلب</button>
                </form>
            </div>

            <div class="card"><h3>سجل طلباتي</h3>{orders_log or "لا توجد طلبات سابقة."}</div>
        </div>

        <div class="bottom-nav">
            <a href="/" class="nav-item active"><i class="fas fa-home"></i>الرئيسية</a>
            <a href="https://t.me/SmmSpider" class="nav-item"><i class="fas fa-headset"></i>مساعدة</a>
        </div>
    </body></html>"""

# --- [ سيرفر المعالجة ] ---
class SpiderMasterServer(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        db = load_db()
        cookie = self.headers.get('Cookie')
        user = cookies.SimpleCookie(cookie)['session_user'].value if cookie and 'session_user' in cookies.SimpleCookie(cookie) else None
        p, q = urlparse(self.path).path, parse_qs(urlparse(self.path).query)

        def send_res(content, set_c=None):
            self.send_response(200)
            self.send_header("Content-type","text/html; charset=utf-8")
            if set_c: self.send_header("Set-Cookie", set_c)
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))

        # --- [ معالجة إنشاء حساب جديد - SignUp ] ---
        if p == "/signup_action":
            u = q.get('user', [''])[0].strip()
            pw = q.get('pass', [''])[0].strip()
            tid = q.get('tele_id', [''])[0].strip()
            
            if not u or not pw:
                send_res("<script>alert('يرجى ملء كافة الحقول!');location.href='/';</script>")
                return
            
            if u in db["users"]:
                send_res("<script>alert('اسم المستخدم موجود بالفعل!');location.href='/';</script>")
            else:
                db["users"][u] = {"pass": pw, "balance": 0.0, "spent": 0.0, "uid": tid, "is_admin": False}
                save_db(db)
                send_res("<script>alert('تم إنشاء الحساب بنجاح! يمكنك الدخول الآن');location.href='/';</script>")
            return

        # --- [ معالجة تسجيل الدخول ] ---
        if p == "/auth_action":
            u, pw = q.get('user',[''])[0], q.get('pass',[''])[0]
            if u in db["users"] and db["users"][u]["pass"] == pw:
                send_res("<script>location.href='/';</script>", f"session_user={u}; Path=/;")
            else:
                send_res("<script>alert('خطأ في البيانات!');location.href='/';</script>")
            return

        if p == "/logout": 
            self.send_response(302); self.send_header("Location", "/"); self.send_header("Set-Cookie", "session_user=; Max-Age=0; Path=/;"); self.end_headers(); return

        if not user:
            send_res(get_login_page()); return

        # --- [ لوحة الإدارة والطلبات ] ---
        if p == "/admin_panel" and user == "admin": send_res(get_admin_dashboard(db)); return
        
        if p == "/admin_act" and user == "admin":
            act = q.get('act',[''])[0]
            if act == "charge": 
                target = q.get('target_user',[''])[0]; amount = float(q.get('amount',['0'])[0])
                if target in db["users"]: db["users"][target]["balance"] += amount
            elif act == "add_svc":
                db["services"].append({"id": q['id'][0], "cat": q.get('cat', ['عام'])[0], "name": q['n'][0], "price": float(q['p'][0])})
            elif act == "del_svc":
                sid = q.get('sid',[''])[0]
                db["services"] = [s for s in db["services"] if s['id'] != sid]
            save_db(db); self.send_response(302); self.send_header("Location", "/admin_panel"); self.end_headers(); return

        if p == "/place_order":
            sid, qty = q.get('sid',[''])[0], int(q.get('qty',['0'])[0])
            svc = next((s for s in db["services"] if s['id'] == sid), None)
            u_data = db["users"][user]; cost = (qty/1000)*svc['price'] if svc else 0
            if svc and u_data['balance'] >= cost:
                u_data['balance'] -= cost; u_data['spent'] += cost
                db["orders"].append({"user": user, "service": svc['name']})
                save_db(db); send_res("<script>alert('تم الطلب بنجاح!');location.href='/';</script>")
            else:
                send_res("<script>alert('فشل الطلب: رصيد غير كافٍ!');location.href='/';</script>")
            return

        send_res(get_user_page(db, user))

# --- [ تشغيل السيرفر ] ---
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), SpiderMasterServer) as httpd:
    print(f"Server started at {PORT}"); httpd.serve_forever()
