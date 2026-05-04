import http.server
import socketserver
import json
import os
import hashlib
import secrets
import re
from urllib.parse import parse_qs, urlparse
from http import cookies
from datetime import datetime, timedelta
import uuid

# --- [ 1. الإعدادات والبيانات الأساسية ] ---
PORT = int(os.environ.get("PORT", 5000))
DB_FILE = "spider_master_database.json"
SITE_NAME = "Spider Store Pro"
TELEGRAM_LINK = "https://t.me/nbel3030"
ADMIN_SECRET = "iQSpiderSpidernbel3030"

# --- [ 2. وظائف الأمان والتشفير ] ---
def hash_password(password):
    """تشفير كلمة المرور باستخدام SHA-256"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{pwd_hash}${salt}"

def verify_password(password, hashed):
    """التحقق من كلمة المرور"""
    try:
        pwd_hash, salt = hashed.split('$')
        return hashlib.sha256((password + salt).encode()).hexdigest() == pwd_hash
    except:
        return False

def validate_email(email):
    """التحقق من صحة البريد الإلكتروني"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """التحقق من صحة رقم الهاتف"""
    pattern = r'^[0-9\+\-\s]{7,20}$'
    return re.match(pattern, phone) is not None

def generate_token():
    """توليد رمز فريد"""
    return secrets.token_urlsafe(32)

# --- [ 3. وظائف قاعدة البيانات ] ---
def load_db():
    """تحميل قاعدة البيانات"""
    if not os.path.exists(DB_FILE):
        data = {
            "users": {
                "admin": {
                    "pass": hash_password("iQSpiderSpidernbel3030"),
                    "balance": 1000.0,
                    "spent": 0.0,
                    "phone": "000",
                    "email": "admin@spiderstore.com",
                    "is_admin": True,
                    "wallet": 0.0,
                    "verified": True,
                    "created_at": datetime.now().isoformat()
                }
            },
            "services": [],
            "orders": [],
            "transactions": [],
            "coupons": [],
            "notifications": {},
            "stats": {
                "total_profit": 0.0,
                "total_orders": 0,
                "total_users": 1
            },
            "settings": {
                "site_announcement": "مرحباً بكم في متجر سبايدر برو!",
                "min_balance": 1.0,
                "commission_rate": 0.1
            }
        }
        save_db(data)
        return data
    
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except:
            return load_db()

def save_db(data):
    """حفظ قاعدة البيانات"""
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# --- [ 4. وظائف المحفظة والدفع ] ---
def add_transaction(db, username, amount, transaction_type, description=""):
    """إضافة معاملة مالية"""
    transaction = {
        "id": str(uuid.uuid4()),
        "user": username,
        "amount": amount,
        "type": transaction_type,  # deposit, withdrawal, order, refund
        "description": description,
        "timestamp": datetime.now().isoformat(),
        "status": "completed"
    }
    db["transactions"].append(transaction)
    return transaction

def add_notification(db, username, title, message, notification_type="info"):
    """إضافة إشعار للمستخدم"""
    if username not in db["notifications"]:
        db["notifications"][username] = []
    
    notification = {
        "id": str(uuid.uuid4()),
        "title": title,
        "message": message,
        "type": notification_type,  # info, success, warning, error
        "timestamp": datetime.now().isoformat(),
        "read": False
    }
    db["notifications"][username].append(notification)
    return notification

def apply_coupon(db, coupon_code, user_balance):
    """تطبيق كود خصم"""
    for coupon in db.get("coupons", []):
        if coupon["code"] == coupon_code and coupon["active"]:
            if coupon["type"] == "percentage":
                discount = user_balance * (coupon["value"] / 100)
            else:
                discount = coupon["value"]
            return discount, coupon
    return 0, None

# --- [ 5. وظائف نظام الطلبات ] ---
def create_order(db, username, service_id, link, quantity, coupon_code=""):
    """إنشاء طلب جديد"""
    user = db["users"].get(username, {})
    service = next((s for s in db["services"] if s["id"] == service_id), None)
    
    if not service:
        return {"status": "error", "message": "الخدمة غير موجودة"}
    
    # التحقق من الحدود
    try:
        qty = int(quantity)
    except:
        return {"status": "error", "message": "الكمية غير صحيحة"}
    
    if qty < int(service["min"]) or qty > int(service["max"]):
        return {"status": "error", "message": f"الكمية يجب أن تكون بين {service['min']} و {service['max']}"}
    
    # حساب التكلفة
    cost = (service["price"] / 1000) * qty
    
    # تطبيق الكود
    discount = 0
    if coupon_code:
        discount, coupon = apply_coupon(db, coupon_code, cost)
    
    final_cost = cost - discount
    
    # التحقق من الرصيد
    if user.get("balance", 0) < final_cost:
        return {"status": "error", "message": "الرصيد غير كافي"}
    
    # إنشاء الطلب
    order = {
        "id": str(uuid.uuid4()),
        "user": username,
        "service_id": service_id,
        "service_name": service["name"],
        "link": link,
        "quantity": qty,
        "cost": cost,
        "discount": discount,
        "final_cost": final_cost,
        "status": "pending",  # pending, processing, completed, failed
        "progress": 0,
        "created_at": datetime.now().isoformat(),
        "completed_at": None
    }
    
    # خصم من الرصيد
    db["users"][username]["balance"] -= final_cost
    db["users"][username]["spent"] += final_cost
    
    db["orders"].append(order)
    
    # إضافة معاملة
    add_transaction(db, username, final_cost, "order", f"طلب خدمة: {service['name']}")
    
    # إضافة إشعار
    add_notification(db, username, "تم تأكيد الطلب ✅", 
                    f"تم قبول طلبك بنجاح - الكمية: {qty}",
                    "success")
    
    # تحديث الإحصائيات
    db["stats"]["total_orders"] += 1
    db["stats"]["total_profit"] += final_cost * (db["settings"].get("commission_rate", 0.1))
    
    save_db(db)
    
    return {
        "status": "success",
        "message": "تم إنشاء الطلب بنجاح",
        "order_id": order["id"],
        "order": order
    }

# --- [ 6. التنسيق والتصاميم ] ---
def get_master_style():
    """نمط CSS موحد"""
    return """
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700;900&display=swap');
        :root {
            --accent: #f39c12;
            --bg: #05080f;
            --card: rgba(25, 32, 50, 0.7);
            --border: rgba(243, 156, 18, 0.2);
            --danger: #ff4757;
            --success: #2ecc71;
            --warning: #f39c12;
            --info: #3498db;
        }
        * {
            box-sizing: border-box;
            font-family: 'Cairo', sans-serif;
        }
        body {
            margin: 0;
            background: var(--bg);
            color: #fff;
            direction: rtl;
            padding-bottom: 90px;
            overflow-x: hidden;
        }
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(125deg, #05080f 0%, #1e3c72 100%);
            z-index: -2;
        }
        .header {
            height: 70px;
            background: rgba(5, 8, 15, 0.85);
            backdrop-filter: blur(15px);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 20px;
            border-bottom: 1px solid var(--border);
            position: sticky;
            top: 0;
            z-index: 1000;
        }
        .stat-banner {
            background: rgba(243, 156, 18, 0.15);
            border: 1px solid var(--border);
            backdrop-filter: blur(10px);
            margin: 15px;
            padding: 20px;
            border-radius: 25px;
            display: flex;
            justify-content: space-around;
            flex-wrap: wrap;
        }
        .stat-item {
            text-align: center;
            flex: 1;
            min-width: 100px;
        }
        .stat-item b {
            color: var(--accent);
            display: block;
            font-size: 1.2rem;
        }
        .stat-item span {
            font-size: 0.8rem;
            opacity: 0.7;
        }
        .card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 25px;
            padding: 20px;
            margin: 15px;
            backdrop-filter: blur(10px);
        }
        input, select, textarea {
            width: 100%;
            padding: 14px;
            margin-top: 12px;
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.1);
            background: rgba(0,0,0,0.4);
            color: #fff;
            outline: none;
        }
        input::placeholder, select::placeholder {
            color: rgba(255,255,255,0.5);
        }
        .btn {
            width: 100%;
            padding: 14px;
            margin-top: 12px;
            border-radius: 15px;
            border: none;
            font-weight: 900;
            cursor: pointer;
            transition: 0.3s;
        }
        .btn-send {
            background: linear-gradient(45deg, var(--accent), #e67e22);
            color: #000;
        }
        .btn-send:hover {
            transform: scale(1.02);
            box-shadow: 0 10px 30px rgba(243, 156, 18, 0.3);
        }
        .btn-danger {
            background: var(--danger);
            color: white;
        }
        .btn-success {
            background: var(--success);
            color: white;
        }
        .bottom-nav {
            position: fixed;
            bottom: 15px;
            left: 15px;
            right: 15px;
            height: 65px;
            background: rgba(5, 8, 15, 0.95);
            backdrop-filter: blur(20px);
            display: flex;
            justify-content: space-around;
            align-items: center;
            border-radius: 20px;
            border: 1px solid var(--border);
            z-index: 999;
        }
        .nav-item {
            color: #666;
            text-decoration: none;
            font-size: 11px;
            text-align: center;
            flex: 1;
        }
        .nav-item.active {
            color: var(--accent);
        }
        .nav-item i {
            font-size: 20px;
            display: block;
        }
        .cost-badge {
            background: rgba(243, 156, 18, 0.1);
            border: 1px dashed var(--accent);
            padding: 15px;
            border-radius: 15px;
            margin-top: 10px;
            display: none;
        }
        .alert {
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .alert-success {
            background: rgba(46, 204, 113, 0.1);
            border: 1px solid var(--success);
            color: var(--success);
        }
        .alert-error {
            background: rgba(255, 71, 87, 0.1);
            border: 1px solid var(--danger);
            color: var(--danger);
        }
        .alert-info {
            background: rgba(52, 152, 219, 0.1);
            border: 1px solid var(--info);
            color: var(--info);
        }
        .notification-badge {
            position: absolute;
            top: 15px;
            left: 15px;
            background: var(--danger);
            color: white;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
        }
        .order-item {
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid var(--border);
            border-radius: 15px;
            padding: 15px;
            margin: 10px 0;
        }
        .order-status {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 10px;
            font-size: 0.8rem;
            font-weight: bold;
            margin-top: 10px;
        }
        .order-status.pending {
            background: rgba(243, 156, 18, 0.3);
            color: var(--accent);
        }
        .order-status.processing {
            background: rgba(52, 152, 219, 0.3);
            color: var(--info);
        }
        .order-status.completed {
            background: rgba(46, 204, 113, 0.3);
            color: var(--success);
        }
        .order-status.failed {
            background: rgba(255, 71, 87, 0.3);
            color: var(--danger);
        }
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            z-index: 2000;
            align-items: center;
            justify-content: center;
            backdrop-filter: blur(10px);
        }
        .modal.show {
            display: flex;
        }
        .modal-content {
            background: #0a0f1d;
            padding: 30px;
            border-radius: 25px;
            width: 90%;
            max-width: 500px;
            border: 1px solid var(--accent);
            max-height: 90vh;
            overflow-y: auto;
        }
    </style>
    """

def get_welcome_page(error="", success=""):
    """صفحة تسجيل الدخول والتسجيل"""
    error_msg = f"<div class='alert alert-error'><i class='fas fa-exclamation-circle'></i> {error}</div>" if error else ""
    success_msg = f"<div class='alert alert-success'><i class='fas fa-check-circle'></i> {success}</div>" if success else ""
    
    return f"""
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        {get_master_style()}
        <title>{SITE_NAME} | تسجيل الدخول</title>
    </head>
    <body>
        <div class="header">
            <div style="font-weight:900; color:var(--accent); font-size:20px;">
                <i class="fas fa-bolt"></i> {SITE_NAME}
            </div>
            <div></div>
        </div>
        
        <div style="display:flex; flex-direction:column; align-items:center; margin-top:40px;">
            <div class="card" style="width:90%; max-width:400px;">
                <h2 style="text-align:center; margin-bottom:25px; font-weight:900;">
                    <i class="fas fa-shield-alt"></i> الدخول للمنصة
                </h2>
                {error_msg} {success_msg}
                <form action="/auth">
                    <input type="text" name="user" placeholder="👤 اسم المستخدم" required>
                    <input type="password" name="pass" placeholder="🔐 كلمة المرور" required>
                    <button type="submit" class="btn btn-send">دخول الآمان <i class="fas fa-arrow-left"></i></button>
                </form>
                <button class="btn" style="background: rgba(243, 156, 18, 0.2); border: 1px solid var(--accent); color: var(--accent); margin-top: 15px;" onclick="openRegisterModal()">
                    ✨ إنشاء حساب جديد
                </button>
            </div>
        </div>
        
        <div id="regModal" class="modal">
            <div class="modal-content">
                <h3 style="text-align:center; color:var(--accent); margin-bottom:20px;">
                    <i class="fas fa-user-plus"></i> فتح حساب جديد
                </h3>
                <form action="/register">
                    <input type="text" name="new_user" placeholder="👤 اسم المستخدم" required>
                    <input type="email" name="email" placeholder="📧 البريد الإلكتروني" required>
                    <input type="tel" name="phone" placeholder="📱 رقم الهاتف" required>
                    <input type="password" name="new_pass" placeholder="🔐 كلمة المرور" required>
                    <input type="password" name="confirm_pass" placeholder="🔐 تأكيد كلمة المرور" required>
                    <button type="submit" class="btn btn-send">تأكيد البيانات</button>
                    <button type="button" class="btn" style="background: var(--danger);" onclick="closeRegisterModal()">إلغاء</button>
                </form>
            </div>
        </div>
        
        <script>
            function openRegisterModal() {{ document.getElementById('regModal').classList.add('show'); }}
            function closeRegisterModal() {{ document.getElementById('regModal').classList.remove('show'); }}
        </script>
    </body>
    </html>
    """

def get_user_page(db, username):
    """الصفحة الرئيسية للمستخدم"""
    u = db["users"].get(username, {})
    services = db.get("services", [])
    cats = sorted(list(set([s.get('cat', 'عام') for s in services])))
    
    unread_notif = len([n for n in db.get("notifications", {}).get(username, []) if not n.get("read")])
    notif_badge = f'<div class="notification-badge">{unread_notif}</div>' if unread_notif > 0 else ""
    
    return f"""
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        {get_master_style()}
        <title>{SITE_NAME} | الرئيسية</title>
    </head>
    <body>
        <div class="header">
            <a href="/notifications" style="color:white; position:relative; text-decoration:none; font-size:20px;">
                <i class="fas fa-bell"></i>
                {notif_badge}
            </a>
            <div style="font-weight:900; color:var(--accent); font-size:20px;">{SITE_NAME}</div>
            <a href="/logout" style="color:var(--danger); text-decoration:none; font-size:18px;">
                <i class="fas fa-power-off"></i>
            </a>
        </div>
        
        <div class="stat-banner">
            <div class="stat-item">
                <b style="color:var(--accent);">${{u.get('balance',0):.2f}}</b>
                <span>الرصيد المتاح</span>
            </div>
            <div class="stat-item">
                <b style="color:var(--success);">${{u.get('wallet',0):.2f}}</b>
                <span>المحفظة الرقمية</span>
            </div>
            <div class="stat-item">
                <b style="color:var(--info);">${{u.get('spent',0):.2f}}</b>
                <span>الإنفاق الكلي</span>
            </div>
        </div>
        
        <div class="card">
            <h4 style="margin-bottom:15px; border-right: 3px solid var(--accent); padding-right:10px;">
                📦 طلب خدمة جديدة
            </h4>
            <form action="/place_order_api">
                <select onchange="updateSvcs(this.value)" required>
                    <option value="" disabled selected>👇 اختر القسم...</option>
                    {"".join([f'<option value="{c}">{c}</option>' for c in cats])}
                </select>
                <select name="sid" id="sid_select" onchange="calculateCost()" required>
                    <option value="" disabled selected>👇 اختر الخدمة...</option>
                </select>
                <input type="text" name="link" placeholder="🔗 الرابط (Link)" required>
                <input type="number" name="qty" id="qty_input" placeholder="📊 الكمية (Quantity)" oninput="calculateCost()" required>
                <input type="text" name="coupon" id="coupon_input" placeholder="🎟️ كود الخصم (اختياري)">
  
