import http.server
import socketserver
import json
import os
import urllib.request
import urllib.parse
from urllib.parse import parse_qs, urlparse

# --- [ الإعدادات المركزية ] ---
# قراءة المنفذ تلقائياً من بيئة الاستضافة (ضروري لـ Railway)
PORT = int(os.environ.get("PORT", 5000))
DB_FILE = "spider_v83_final.json"
SITE_NAME = "Spider Store"
API_KEY = "cc1b9f1ce9c06b61773412efd4fa6af0"
API_URL = "https://kd1s.com/api/v2"

# --- [ محرك البيانات ] ---
def load_db():
    if not os.path.exists(DB_FILE):
        data = {
            "users": {
                "admin": {"pass": "nbelpppp", "balance": 10000.0, "phone": "077", "uid": "8249124053", "is_admin": True, "is_banned": False}
            },
            "services": [], "vouchers": [], "orders": [], "settings": {"maintenance": False}
        }
        save_db(data); return data
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        try: return json.load(f)
        except: return {"users": {}, "services": [], "vouchers": [], "orders": [], "settings": {"maintenance": False}}

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- [ التصميم الموحد مع الخلفية المتحركة ] ---
def get_common_style():
    return f"""
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        :root {{ --gold: #f39c12; --dark: #070b14; --card: rgba(21, 31, 51, 0.85); --text: #f1f5f9; --danger: #ef4444; --blue: #3498db; }}
        * {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; font-family: 'Cairo', sans-serif; }}
        
        body {{ 
            margin: 0; padding: 0; 
            background: linear-gradient(-45deg, #070b14, #151f33, #0b132b, #070b14);
            background-size: 400% 400%; animation: gradientBG 15s ease infinite;
            height: 100vh; width: 100vw; direction: rtl; color: var(--text); overflow-x: hidden;
        }}
        @keyframes gradientBG {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}
        
        .header {{ height: 65px; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; background: rgba(21, 31, 51, 0.95); backdrop-filter: blur(10px); border-bottom: 2px solid var(--gold); position: sticky; top: 0; z-index: 1000; }}
        .scroll-content {{ padding: 15px; display: flex; flex-direction: column; align-items: center; padding-bottom: 80px; }}
        .card {{ background: var(--card); backdrop-filter: blur(15px); border-radius: 25px; padding: 25px; margin-bottom: 20px; width: 100%; max-width: 600px; border: 1px solid rgba(255,255,255,0.05); box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
        
        /* قائمة الخدمات الجديدة */
        .custom-select {{ position: relative; width: 100%; margin-bottom: 15px; }}
        .select-trigger {{ width: 100%; padding: 15px; background: rgba(0,0,0,0.3); border: 1px solid var(--gold); border-radius: 15px; color: white; display: flex; justify-content: space-between; align-items: center; cursor: pointer; }}
        .select-options {{ display: none; position: absolute; top: 105%; left: 0; right: 0; background: #151f33; border: 1px solid var(--gold); border-radius: 15px; z-index: 2000; max-height: 250px; overflow-y: auto; box-shadow: 0 10px 20px rgba(0,0,0,0.5); }}
        .search-input {{ width: calc(100% - 20px); margin: 10px; padding: 12px; border-radius: 10px; border: 1px solid #333; background: #070b14; color: white; outline: none; }}
        .option-item {{ padding: 12px 15px; border-bottom: 1px solid rgba(255,255,255,0.05); cursor: pointer; text-align: right; }}
        .option-item:hover {{ background: rgba(243, 156, 18, 0.1); }}
        .option-item b {{ color: var(--gold); display: block; }}
        
        input, select, textarea {{ width: 100%; padding: 14px; margin-bottom: 12px; border-radius: 15px; border: 1px solid rgba(243, 156, 18, 0.3); background: rgba(0,0,0,0.2); color: white; outline: none; }}
        .btn-gold {{ width: 100%; padding: 16px; background: linear-gradient(45deg, #f39c12, #e67e22); border: none; border-radius: 15px; color: white; font-weight: 900; cursor: pointer; }}
        .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: 6000; }}
        .modal-content {{ background: #151f33; border-radius: 30px; padding: 25px; max-width: 350px; margin: 120px auto; border: 2px solid var(--gold); text-align: center; }}
        
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 12px; text-align: center; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 13px; }}
        th {{ color: var(--gold); }}
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    """

def send_to_api(service_id, link, quantity):
    params = {'key': API_KEY, 'action': 'add', 'service': service_id, 'link': link, 'quantity': quantity}
    try:
        data = urllib.parse.urlencode(params).encode()
        req = urllib.request.Request(API_URL, data=data)
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode())
            return res.get('order')
    except: return None

def get_user_page(db, username):
    u = db["users"].get(username, {})
    services_json = json.dumps({s['id']: s for s in db['services']})
    svc_options = "".join([f'<div class="option-item" onclick="selectSvc(\'{s["id"]}\', \'{s["name"]}\')"><b>{s["name"]}</b><small>السعر: ${s["price"]}</small></div>' for s in db['services']])
    
    return f"""<!DOCTYPE html><html lang="ar"><head><meta charset="UTF-8">{get_common_style()}</head>
    <body>
        <div class="header">
            <div style="font-weight:900; color:var(--gold); font-size:20px;"><i class="fas fa-spider"></i> {SITE_NAME}</div>
            <div style="display:flex; gap:18px; align-items:center;">
                {f'<a href="/admin_panel" style="color:var(--gold);"><i class="fas fa-user-shield fa-lg"></i></a>' if u.get('is_admin') else ''}
                <i class="fas fa-user-circle fa-lg" style="color:var(--gold); cursor:pointer;" onclick="document.getElementById(\'user_modal\').style.display=\'block\'"></i>
                <i class="fas fa-sign-out-alt fa-lg" style="cursor:pointer;" onclick="location.href=\'/logout\'"></i>
            </div>
        </div>
        <div class="scroll-content">
            <div class="card" style="border-right:6px solid var(--gold); background:linear-gradient(to left, rgba(243,156,18,0.1), transparent);">
                <small>الرصيد المتاح</small>
                <div style="font-size:36px; font-weight:900; color:var(--gold);">${u.get('balance', 0):.3f}</div>
            </div>
            
            <div class="card">
                <h3><i class="fas fa-shopping-cart"></i> طلب جديد</h3>
                <div class="custom-select">
                    <div class="select-trigger" onclick="toggleSelect()">
                        <span id="svc_display">-- اختر الخدمة المطلوبة --</span>
                        <i class="fas fa-chevron-down"></i>
                    </div>
                    <div id="select_menu" class="select-options">
                        <input type="text" class="search-input" placeholder="🔍 ابحث عن خدمة..." onkeyup="filterSvcs(this.value)">
                        <div id="items_container">{svc_options}</div>
                    </div>
                </div>
                <input type="hidden" id="sid">
                <input id="link" placeholder="رابط الطلب">
                <input id="qty" type="number" placeholder="الكمية" oninput="calculateCost()">
                <div style="background:rgba(0,0,0,0.3); padding:15px; border-radius:15px; text-align:center; margin-bottom:15px; border:1px dashed var(--gold);">
                    <small>التكلفة الإجمالية</small><br>
                    <span id="total_cost" style="font-size:24px; font-weight:900; color:var(--gold);">$0.0000</span>
                </div>
                <button class="btn-gold" onclick="placeOrder()">تأكيد الشراء</button>
            </div>
            
            <div class="card">
                <h3>🎟️ شحن كود رصيد</h3>
                <input type="text" id="v_code" placeholder="أدخل الكود هنا">
                <button class="btn-gold" style="background:var(--blue)" onclick="redeemVoucher()">تفعيل الكود</button>
            </div>
        </div>

        <div id="user_modal" class="modal" onclick="this.style.display=\'none\'">
            <div class="modal-content" onclick="event.stopPropagation()">
                <i class="fas fa-user-circle fa-4x" style="color:var(--gold); margin-bottom:15px;"></i>
                <h4>معلومات الحساب</h4>
                <div style="text-align:right; font-size:14px; padding:10px;">
                    <p>👤 المستخدم: {username}</p>
                    <p>🆔 الآيدي: {u.get('uid', '---')}</p>
                    <p>💰 الرصيد: ${u.get('balance', 0):.3f}</p>
                </div>
                <button class="btn-gold" onclick="document.getElementById(\'user_modal\').style.display=\'none\'">إغلاق</button>
            </div>
        </div>

        <script>
            const services = {services_json};
            function toggleSelect() {{
                const m = document.getElementById('select_menu');
                m.style.display = m.style.display === 'block' ? 'none' : 'block';
            }}
            function filterSvcs(val) {{
                const items = document.querySelectorAll('.option-item');
                items.forEach(i => i.style.display = i.innerText.toLowerCase().includes(val.toLowerCase()) ? 'block' : 'none');
            }}
            function selectSvc(id, name) {{
                document.getElementById('sid').value = id;
                document.getElementById('svc_display').innerText = name;
                toggleSelect(); calculateCost();
            }}
            function calculateCost() {{
                let id = document.getElementById('sid').value; 
                let q = document.getElementById('qty').value || 0;
                if(id && services[id]) document.getElementById('total_cost').innerText = "$" + ((q / 1000) * services[id].price).toFixed(4);
            }}
            function placeOrder() {{
                let s = document.getElementById('sid').value, l = document.getElementById('link').value, q = document.getElementById('qty').value;
                if(!s || !l || !q) return alert("يرجى إكمال جميع الحقول");
                location.href = `/place_order?sid=${{s}}&link=${{l}}&qty=${{q}}`;
            }}
            function redeemVoucher() {{ 
                let c = document.getElementById('v_code').value; 
                if(c) location.href = '/redeem?c='+c; 
            }}
        </script>
    </body></html>"""

def get_admin_page(db):
    users_rows = "".join([f"<tr><td>{un}</td><td>${ud['balance']:.2f}</td><td><a href='/admin_act?act=ban&u={un}' style='color:var(--danger)'>حظر</a></td></tr>" for un, ud in db['users'].items()])
    svc_rows = "".join([f"<tr><td>{s['id']}</td><td>{s['name']}</td><td><a href='/admin_act?act=del_svc&id={s['id']}' style='color:var(--danger)'>حذف</a></td></tr>" for s in db['services']])

    return f"""<!DOCTYPE html><html lang="ar"><head><meta charset="UTF-8">{get_common_style()}</head>
    <body style="overflow-y:auto;">
        <div class="header">
            <div style="font-weight:900; color:var(--gold);">لوحة الإدارة</div>
            <a href="/" style="color:white;"><i class="fas fa-home fa-lg"></i></a>
        </div>
        <div class="scroll-content">
            <div class="card">
                <h3>➕ إضافة خدمة</h3>
                <form action="/admin_act">
                    <input type="hidden" name="act" value="add_svc">
                    <input name="id" placeholder="ID الخدمة">
                    <input name="n" placeholder="اسم الخدمة">
                    <input name="p" step="0.0001" type="number" placeholder="السعر لكل 1000">
                    <textarea name="desc" placeholder="وصف الخدمة"></textarea>
                    <button class="btn-gold">حفظ الخدمة</button>
                </form>
            </div>
            <div class="card">
                <h3>🎟️ إنشاء كود رصيد</h3>
                <form action="/admin_act">
                    <input type="hidden" name="act" value="add_v">
                    <input name="c" placeholder="اسم الكود">
                    <input name="v" type="number" step="0.01" placeholder="القيمة">
                    <input name="l" type="number" placeholder="عدد المستخدمين">
                    <button class="btn-gold" style="background:var(--blue)">إنشاء</button>
                </form>
            </div>
            <div class="card"><h3>⚙️ الخدمات</h3><table><tr><th>ID</th><th>الاسم</th><th>فعل</th></tr>{svc_rows}</table></div>
            <div class="card"><h3>👥 المستخدمين</h3><table><tr><th>يوزر</th><th>رصيد</th><th>فعل</th></tr>{users_rows}</table></div>
        </div>
    </body></html>"""

def get_auth_page(mode="login"):
    title = "دخول" if mode == "login" else "إنشاء حساب"
    fields = """<input name="user" placeholder="اسم المستخدم" required><input name="pass" type="password" placeholder="كلمة المرور" required>"""
    if mode == "signup":
        fields += """<input name="uid" placeholder="رقم الآيدي (ID)" required><input name="phone" placeholder="رقم الهاتف" required>"""
    return f"""<!DOCTYPE html><html lang="ar"><head><meta charset="UTF-8">{get_common_style()}</head><body style="display:flex;justify-content:center;align-items:center;"><div class="card" style="width:90%;max-width:380px;text-align:center;"><i class="fas fa-spider fa-4x" style="color:var(--gold);margin-bottom:20px;"></i><h2>{SITE_NAME}</h2><form action="/{'auth_action' if mode == 'login' else 'reg_action'}">{fields}<button class="btn-gold">{title}</button></form><div style="margin-top:20px;"><a href="/{ 'signup' if mode=='login' else '' }" style="color:var(--gold);text-decoration:none;font-size:13px;">{ 'إنشاء حساب جديد' if mode=='login' else 'لديك حساب؟ سجل دخول' }</a></div></div></body></html>"""

class SpiderServer(http.server.BaseHTTPRequestHandler):
    session = None
    def do_GET(self):
        db = load_db()
        parsed = urlparse(self.path); p, q = parsed.path, parse_qs(parsed.query)
        def send_h(c): self.send_response(200); self.send_header("Content-type","text/html; charset=utf-8"); self.end_headers(); self.wfile.write(c.encode('utf-8'))

        if p == "/signup": send_h(get_auth_page("signup")); return
        if p == "/reg_action":
            u, pw, uid, ph = q.get('user',[''])[0], q.get('pass',[''])[0], q.get('uid',[''])[0], q.get('phone',[''])[0]
            if u and u not in db["users"]:
                db["users"][u] = {"pass": pw, "uid": uid, "phone": ph, "balance": 0.0, "is_admin": False, "is_banned": False}
                save_db(db); send_h("<script>alert('تم إنشاء الحساب!');location.href='/';</script>")
            return
        if p == "/auth_action":
            u, pw = q.get('user',[''])[0], q.get('pass',[''])[0]
            if u in db["users"] and db["users"][u]["pass"] == pw:
                if db["users"][u].get("is_banned"): send_h("<script>alert('محظور!');location.href='/';</script>")
                else: SpiderServer.session = u; self.send_response(302); self.send_header("Location", "/"); self.end_headers()
            else: send_h("<script>alert('بيانات خاطئة!');location.href='/';</script>")
            return
        if p == "/admin_act" and SpiderServer.session == "admin":
            act = q.get('act',[''])[0]
            if act == "add_svc": db["services"].append({"id": q['id'][0], "name": q['n'][0], "price": float(q['p'][0]), "desc": q.get('desc',[''])[0]})
            elif act == "add_v": db["vouchers"].append({"code": q['c'][0], "value": float(q['v'][0]), "limit": int(q['l'][0]), "used_by": []})
            elif act == "del_svc": db["services"] = [s for s in db["services"] if s['id'] != q['id'][0]]
            elif act == "ban": db["users"][q['u'][0]]["is_banned"] = True
            save_db(db); self.send_response(302); self.send_header("Location", "/admin_panel"); self.end_headers(); return
        if p == "/admin_panel" and SpiderServer.session == "admin": send_h(get_admin_page(db)); return
        if p == "/place_order" and SpiderServer.session:
            sid, qty, link = q.get('sid',[''])[0], int(q.get('qty',['0'])[0]), q.get('link',[''])[0]
            svc = next((s for s in db["services"] if s['id'] == sid), None); u = db["users"][SpiderServer.session]
            cost = (qty/1000)*svc['price'] if svc else 999999
            if svc and u['balance'] >= cost:
                oid = send_to_api(sid, link, qty)
                if oid:
                    u['balance'] -= cost
                    db["orders"].append({"id": oid, "user": SpiderServer.session, "service": svc['name']})
                    save_db(db); send_h("<script>alert('تم بنجاح!');location.href='/';</script>")
                else: send_h("<script>alert('خطأ API');location.href='/';</script>")
            return
        if p == "/redeem" and SpiderServer.session:
            code = q.get('c',[''])[0]; found = False
            for v in db["vouchers"]:
                if v["code"] == code and len(v["used_by"]) < v["limit"] and SpiderServer.session not in v["used_by"]:
                    db["users"][SpiderServer.session]["balance"] += v["value"]
                    v["used_by"].append(SpiderServer.session); found = True; break
            save_db(db); send_h(f"<script>alert('{'تم الشحن!' if found else 'كود غير صالح'}');location.href='/';</script>")
            return
        if p == "/logout": SpiderServer.session = None; self.send_response(302); self.send_header("Location", "/"); self.end_headers(); return
        if SpiderServer.session: send_h(get_user_page(db, SpiderServer.session))
        else: send_h(get_auth_page("login"))

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), SpiderServer) as httpd:
    print(f"🚀 SERVER READY ON PORT {PORT}"); httpd.serve_forever()
                                                       
