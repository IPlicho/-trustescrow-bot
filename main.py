import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from collections import defaultdict

# ====================== 已填好你的信息，直接运行 ======================
BOT_TOKEN = "8279854167:AAHLrvg-i6e0M_WeG8coIljYlGg_RF8_oRM"
ADMIN_ID = 8781082053  # 你的TG ID，已填好
GUARANTEE_FEE = 10     # 每单所需保证金（可自定义）
PROFIT_RATE = 0.02     # 中间人利润比例（2%，可自定义）
# =================================================================

bot = telebot.TeleBot(BOT_TOKEN)

# 中间人数据结构
middleman = defaultdict(lambda: {
    "wallet": 0,
    "is_middle": False,
    "username": "",
    "total_earn": 0
})

# 订单数据结构
order = defaultdict(dict)
order_id = 1000

def new_oid():
    global order_id
    order_id += 1
    return order_id

# ====================== 机器人主菜单 ======================
@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(msg.chat.id, """
🛡️ TrustEscrow Pro - 专业匿名担保平台
✅ 买家100%匿名
✅ 平台强制派单
✅ 中间人保证金制度
✅ 每单利润实时可见

/order   买家发起担保订单
/bind    申请成为中间人
/my      我的钱包&收益明细
/help    平台使用教程
""")

# ====================== 买家匿名下单流程 ======================
@bot.message_handler(commands=['order'])
def buyer_order(msg):
    bot.send_message(msg.chat.id, "📝 请输入交易说明（商品/服务描述）：")
    bot.register_next_step_handler(msg, step1_set_title)

def step1_set_title(msg):
    oid = new_oid()
    order[oid] = {
        "buyer": msg.from_user.id,
        "title": msg.text,
        "money": None,
        "middle": None,
        "status": "wait_money"
    }
    bot.send_message(msg.chat.id, f"✅ 订单 #{oid} 已创建\n请输入交易金额：")
    bot.register_next_step_handler(msg, lambda m: step2_set_amount(m, oid))

def step2_set_amount(msg, oid):
    try:
        money = float(msg.text)
        order[oid]["money"] = money
        order[oid]["status"] = "wait_admin_assign"
        bot.send_message(msg.chat.id, f"✅ 下单成功！订单 #{oid}\n等待平台分配中间人...")
        # 通知管理员新订单
        bot.send_message(ADMIN_ID, f"🆕 新匿名订单待派单\n订单：#{oid}\n金额：{money} USDT\n派单指令：/pai {oid} 中间人ID")
    except:
        bot.send_message(msg.chat.id, "❌ 请输入有效的数字金额")

# ====================== 中间人申请流程 ======================
@bot.message_handler(commands=['bind'])
def apply_middleman(msg):
    u = msg.from_user.id
    middleman[u]["is_middle"] = True
    middleman[u]["username"] = msg.from_user.username or "无用户名"
    bot.send_message(u, f"✅ 已成功成为中间人\n当前钱包余额：{middleman[u]['wallet']} USDT\n请联系管理员充值保证金")

# ====================== 管理员：强制派单功能 ======================
@bot.message_handler(commands=['pai'])
def admin_assign_order(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    try:
        _, oid, mid = msg.text.split()
        oid = int(oid)
        mid = int(mid)
    except:
        bot.send_message(ADMIN_ID, "❌ 用法错误！正确格式：/pai 订单号 中间人ID")
        return

    # 订单合法性校验
    if oid not in order:
        bot.send_message(ADMIN_ID, "❌ 订单不存在")
        return
    if not middleman[mid]["is_middle"]:
        bot.send_message(ADMIN_ID, "❌ 该用户不是中间人")
        return
    if middleman[mid]["wallet"] < GUARANTEE_FEE:
        bot.send_message(ADMIN_ID, "❌ 该中间人保证金不足，无法派单！")
        return

    # 计算本单利润
    profit = order[oid]["money"] * PROFIT_RATE
    order[oid]["middle"] = mid
    order[oid]["status"] = "processing"
    order[oid]["profit"] = profit

    # 通知相关方
    bot.send_message(ADMIN_ID, f"✅ 强制派单成功\n订单 #{oid} → 中间人 {mid}")
    bot.send_message(order[oid]["buyer"], f"✅ 订单 #{oid} 已分配中间人，交易开始")
    bot.send_message(mid, f"""
🛎️ 【平台强制派单】
订单编号：#{oid}
交易金额：{order[oid]['money']} USDT
买家：匿名
本单可赚利润：{profit:.2f} USDT
⚠️ 不可拒绝，请立即处理
""")

# ====================== 中间人：钱包&收益查询 ======================
@bot.message_handler(commands=['my'])
def my_wallet_info(msg):
    u = msg.from_user.id
    if not middleman[u]["is_middle"]:
        bot.send_message(u, "❌ 你还不是中间人，请先发送 /bind 申请")
        return
    bot.send_message(u, f"""
📌 中间人信息
钱包余额：{middleman[u]['wallet']} USDT
累计总收益：{middleman[u]['total_earn']:.2f} USDT
最低保证金要求：{GUARANTEE_FEE} USDT
""")

# ====================== 管理员：中间人钱包管理 ======================
@bot.message_handler(commands=['wallet'])
def admin_manage_wallet(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    try:
        _, mid, amount = msg.text.split()
        mid = int(mid)
        amount = float(amount)
    except:
        bot.send_message(ADMIN_ID, "❌ 用法错误！正确格式：/wallet 中间人ID ±金额\n例：/wallet 123456 +50")
        return
    middleman[mid]["wallet"] += amount
    bot.send_message(ADMIN_ID, f"✅ 操作成功\n中间人ID：{mid}\n最新余额：{middleman[mid]['wallet']} USDT")
    bot.send_message(mid, f"✅ 钱包余额已更新，当前余额：{middleman[mid]['wallet']} USDT")

# ====================== 管理员：中间人列表查询 ======================
@bot.message_handler(commands=['list'])
def admin_list_middleman(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    text = "📋 全平台中间人列表：\n"
    for uid, info in middleman.items():
        if info["is_middle"]:
            text += f"\nID：{uid}\n用户名：@{info['username']}\n钱包余额：{info['wallet']} USDT\n累计收益：{info['total_earn']:.2f} USDT\n---"
    bot.send_message(ADMIN_ID, text)

# ====================== 管理员：订单完成结算 ======================
@bot.message_handler(commands=['finish'])
def admin_finish_order(msg):
    if msg.from_user.id != ADMIN_ID:
        return
    try:
        oid = int(msg.text.split()[1])
    except:
        bot.send_message(ADMIN_ID, "❌ 用法错误！正确格式：/finish 订单号")
        return
    o = order[oid]
    mid = o["middle"]
    # 给中间人结算利润
    middleman[mid]["total_earn"] += o["profit"]
    # 通知相关方
    bot.send_message(mid, f"✅ 订单 #{oid} 已完成！利润 +{o['profit']:.2f} USDT 已到账")
    bot.send_message(o["buyer"], f"✅ 订单 #{oid} 交易完成，担保结束")
    bot.send_message(o["seller"], f"✅ 订单 #{oid} 交易完成，款项已结算")
    bot.send_message(ADMIN_ID, f"✅ 订单 #{oid} 已完成结算")

# ====================== 平台帮助说明 ======================
@bot.message_handler(commands=['help'])
def help_center(msg):
    bot.send_message(msg.chat.id, """
🛡️ TrustEscrow Pro 平台使用指南
【买家】
/order - 发起匿名担保订单
等待平台派单 → 付款 → 确认收货 → 交易完成

【中间人】
/bind - 申请成为中间人
/my - 查看钱包&收益
接收平台派单 → 跟进订单 → 赚取佣金

【管理员】
/pai 订单号 中间人ID - 强制派单
/wallet 中间人ID ±金额 - 管理中间人钱包
/list - 查看所有中间人
/finish 订单号 - 完成订单结算
""")

print("✅ TrustEscrow Pro 匿名担保机器人已启动运行")
bot.infinity_polling()
