=====================================================
# TELEGRAM ACCOUNTING BOT FULL VERSION
# =====================================================

# تثبيت:
# pip install python-telegram-bot==21.6

# تشغيل:
# python main.py

# =====================================================

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

import json
import os
from datetime import datetime

# =====================================================
# TOKEN
# =====================================================

TOKEN = "8276706114:AAFoHNMvg3GZTWwBRy4BVwVJrUgke1r_UDs"

# =====================================================
# FILES
# =====================================================

PRODUCTS_FILE = "products.json"
SALES_FILE = "sales.json"
DEBTS_FILE = "debts.json"
PARTS_FILE = "parts.json"
REPORTS_FILE = "reports.json"

# =====================================================
# LOAD / SAVE
# =====================================================

def load_data(file_name):

    if os.path.exists(file_name):

        with open(file_name, "r", encoding="utf-8") as f:
            return json.load(f)

    return []

def save_data(file_name, data):

    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# =====================================================
# DATABASE
# =====================================================

products = load_data(PRODUCTS_FILE)
sales = load_data(SALES_FILE)
debts = load_data(DEBTS_FILE)
parts = load_data(PARTS_FILE)
reports = load_data(REPORTS_FILE)

user_state = {}

# =====================================================
# BRAND DETECTION
# =====================================================

brands_keywords = {

    "Apple / iPhone": [
        "iphone", "apple", "ايفون"
    ],

    "Samsung / Galaxy": [
        "samsung", "galaxy", "سامسونج", "جلكسي"
    ],

    "Huawei": [
        "huawei", "هواوي"
    ],

    "Xiaomi": [
        "xiaomi", "redmi", "شاومي"
    ],

    "Oppo": [
        "oppo", "اوبو"
    ],

    "Vivo": [
        "vivo", "فيفو"
    ],
}

def detect_brand(part_name):

    lower_name = part_name.lower()

    for brand, keywords in brands_keywords.items():

        for word in keywords:

            if word in lower_name:
                return brand

    return "أخرى"

# =====================================================
# KEYBOARD
# =====================================================

main_keyboard = ReplyKeyboardMarkup(
    [
        ["➕ إضافة منتج", "🛒 بيع"],
        ["✏️ تعديل سعر", "❌ حذف منتج"],
        ["↩️ ارجاع منتج", "🔧 صيانة"],
        ["📊 تسكير الحساب", "💳 دين / تسليف"],
        ["📋 عرض الديون", "🧩 إضافة قطعة"],
        ["📥 إدخال قطع كثيرة", "🔍 بحث قطعة"],
        ["📂 أقسام القطع", "📦 عرض المنتجات"],
        ["📅 التقارير"],
    ],
    resize_keyboard=True
)

# =====================================================
# START
# =====================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "👋 أهلاً بك في بوت المحاسبة",
        reply_markup=main_keyboard
    )

# =====================================================
# MAIN MESSAGES
# =====================================================

async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text
    user_id = update.message.from_user.id

    # =====================================================
    # إضافة منتج
    # =====================================================

    if text == "➕ إضافة منتج":

        user_state[user_id] = "product_name"

        await update.message.reply_text(
            "📦 اكتب اسم المنتج:"
        )

        return

    if user_state.get(user_id) == "product_name":

        context.user_data["product_name"] = text

        user_state[user_id] = "product_price"

        await update.message.reply_text(
            "💰 اكتب سعر المنتج:"
        )

        return

    if user_state.get(user_id) == "product_price":

        try:

            price = float(text)

            if products:

                last_id = max(
                    p["id"] for p in products
                )

                new_id = last_id + 1

            else:

                new_id = 1

            product = {
                "id": new_id,
                "name": context.user_data["product_name"],
                "price": price
            }

            products.append(product)

            save_data(PRODUCTS_FILE, products)

            await update.message.reply_text(
                f"✅ تمت إضافة المنتج\n\n"
                f"🔢 الرقم: {new_id}\n"
                f"📦 {product['name']}\n"
                f"💰 {price} ريال"
            )

            user_state[user_id] = None

        except:

            await update.message.reply_text(
                "❌ اكتب رقم صحيح"
            )

        return

    # =====================================================
    # عرض المنتجات
    # =====================================================

    if text == "📦 عرض المنتجات":

        if not products:

            await update.message.reply_text(
                "❌ لا توجد منتجات"
            )

            return

        msg = "📦 المنتجات:\n\n"

        for p in products:

            msg += (
                f"{p['id']}️⃣ "
                f"{p['name']} - "
                f"{p['price']} ريال\n"
            )

        await update.message.reply_text(msg)

        return

    # =====================================================
    # البيع
    # =====================================================

    if text == "🛒 بيع":

        if not products:

            await update.message.reply_text(
                "❌ لا توجد منتجات"
            )

            return

        msg = "🛒 المنتجات:\n\n"

        for p in products:

            msg += (
                f"{p['id']}️⃣ "
                f"{p['name']} - "
                f"{p['price']} ريال\n"
            )

        msg += (
            "\n━━━━━━━━━━\n"
            "📌 أمثلة:\n\n"
            "1+2+3\n"
            "شاحن+كفر\n"
            "1+شاحن\n"
        )

        user_state[user_id] = "sell"

        await update.message.reply_text(msg)

        return

    if user_state.get(user_id) == "sell":

        items = text.split("+")

        sold_items = []

        total_price = 0

        for item in items:

            item = item.strip().lower()

            found = None

            if item.isdigit():

                item_id = int(item)

                for p in products:

                    if p["id"] == item_id:
                        found = p
                        break

            else:

                for p in products:

                    if item in p["name"].lower():
                        found = p
                        break

            if found:

                sales.append(found)

                sold_items.append(found)

                total_price += found["price"]

        save_data(SALES_FILE, sales)

        if not sold_items:

            await update.message.reply_text(
                "❌ لم يتم العثور على منتجات"
            )

            user_state[user_id] = None

            return

        msg = "✅ تمت عملية البيع\n\n"

        for s in sold_items:

            msg += (
                f"📦 {s['name']}\n"
                f"💰 {s['price']} ريال\n\n"
            )

        today_total = sum(
            s["price"] for s in sales
        )

        msg += (
            f"━━━━━━━━━━\n"
            f"💵 إجمالي العملية: {total_price} ريال\n"
            f"📊 مبيعات اليوم: {today_total} ريال"
        )

        await update.message.reply_text(msg)

        user_state[user_id] = None

        return

    # =====================================================
    # تعديل سعر
    # =====================================================

    if text == "✏️ تعديل سعر":

        msg = "✏️ المنتجات:\n\n"

        for p in products:

            msg += (
                f"{p['id']}️⃣ "
                f"{p['name']} - "
                f"{p['price']} ريال\n"
            )

        msg += "\nاكتب رقم المنتج"

        user_state[user_id] = "edit_price"

        await update.message.reply_text(msg)

        return

    if user_state.get(user_id) == "edit_price":

        try:

            context.user_data["edit_id"] = int(text)

            user_state[user_id] = "new_price"

            await update.message.reply_text(
                "💰 اكتب السعر الجديد:"
            )

        except:

            await update.message.reply_text(
                "❌ اكتب رقم صحيح"
            )

        return

    if user_state.get(user_id) == "new_price":

        try:

            new_price = float(text)

            found = False

            for p in products:

                if p["id"] == context.user_data["edit_id"]:

                    p["price"] = new_price
                    found = True
                    break

            save_data(PRODUCTS_FILE, products)

            if found:

                await update.message.reply_text(
                    "✅ تم تعديل السعر"
                )

            else:

                await update.message.reply_text(
                    "❌ المنتج غير موجود"
                )

            user_state[user_id] = None

        except:

            await update.message.reply_text(
                "❌ اكتب رقم صحيح"
            )

        return

    # =====================================================
    # حذف منتج
    # =====================================================

    if text == "❌ حذف منتج":

        msg = "❌ المنتجات:\n\n"

        for p in products:

            msg += (
                f"{p['id']}️⃣ "
                f"{p['name']}\n"
            )

        msg += "\nاكتب رقم المنتج"

        user_state[user_id] = "delete_product"

        await update.message.reply_text(msg)

        return

    if user_state.get(user_id) == "delete_product":

        try:

            product_id = int(text)

            found = False

            for p in products:

                if p["id"] == product_id:

                    products.remove(p)
                    found = True
                    break

            save_data(PRODUCTS_FILE, products)

            if found:

                await update.message.reply_text(
                    "✅ تم حذف المنتج"
                )

            else:

                await update.message.reply_text(
                    "❌ المنتج غير موجود"
                )

            user_state[user_id] = None

        except:

            await update.message.reply_text(
                "❌ اكتب رقم صحيح"
            )

        return

    # =====================================================
    # ارجاع منتج
    # =====================================================

    if text == "↩️ ارجاع منتج":

        if not sales:

            await update.message.reply_text(
                "❌ لا توجد مبيعات"
            )

            return

        msg = "↩️ المبيعات:\n\n"

        for i, s in enumerate(sales):

            msg += (
                f"{i+1}️⃣ "
                f"{s['name']} - "
                f"{s['price']} ريال\n"
            )

        msg += "\nاكتب الرقم"

        user_state[user_id] = "return_product"

        await update.message.reply_text(msg)

        return

    if user_state.get(user_id) == "return_product":

        try:

            index = int(text) - 1

            if 0 <= index < len(sales):

                returned = sales.pop(index)

                save_data(SALES_FILE, sales)

                await update.message.reply_text(
                    f"✅ تم ارجاع:\n"
                    f"{returned['name']}"
                )

            else:

                await update.message.reply_text(
                    "❌ الرقم غير صحيح"
                )

            user_state[user_id] = None

        except:

            await update.message.reply_text(
                "❌ اكتب رقم صحيح"
            )

        return

    # =====================================================
    # صيانة
    # =====================================================

    if text == "🔧 صيانة":

        user_state[user_id] = "repair"

        await update.message.reply_text(
            "💰 اكتب مبلغ الصيانة:"
        )

        return

    if user_state.get(user_id) == "repair":

        try:

            price = float(text)

            sales.append({
                "name": "صيانة",
                "price": price
            })

            save_data(SALES_FILE, sales)

            await update.message.reply_text(
                f"✅ تم تسجيل الصيانة\n💰 {price} ريال"
            )

            user_state[user_id] = None

        except:

            await update.message.reply_text(
                "❌ اكتب رقم صحيح"
            )

        return

    # =====================================================
    # إضافة قطعة
    # =====================================================

    if text == "🧩 إضافة قطعة":

        user_state[user_id] = "add_part_name"

        await update.message.reply_text(
            "🧩 اكتب اسم القطعة:"
        )

        return

    if user_state.get(user_id) == "add_part_name":

        context.user_data["part_name"] = text

        user_state[user_id] = "add_part_price"

        await update.message.reply_text(
            "💰 اكتب سعر القطعة:"
        )

        return

    if user_state.get(user_id) == "add_part_price":

        try:

            price = float(text)

            part_name = context.user_data["part_name"]

            brand = detect_brand(part_name)

            part = {
                "name": part_name,
                "price": price,
                "brand": brand
            }

            parts.append(part)

            save_data(PARTS_FILE, parts)

            await update.message.reply_text(
                f"✅ تمت إضافة القطعة\n\n"
                f"🧩 {part_name}\n"
                f"🏷️ {brand}\n"
                f"💰 {price} ريال"
            )

            user_state[user_id] = None

        except:

            await update.message.reply_text(
                "❌ اكتب رقم صحيح"
            )

        return

    # =====================================================
    # إدخال قطع كثيرة
    # =====================================================

    if text == "📥 إدخال قطع كثيرة":

        user_state[user_id] = "bulk_parts"

        await update.message.reply_text(
            "📥 أرسل القطع بهذا الشكل:\n\n"
            "شاشة ايفون 13 - 250\n"
            "بطارية سامسونج A12 - 90"
        )

        return

    if user_state.get(user_id) == "bulk_parts":

        lines = text.split("\n")

        added = 0

        for line in lines:

            try:

                if "-" not in line:
                    continue

                name, price = line.split("-", 1)

                name = name.strip()

                price = float(price.strip())

                brand = detect_brand(name)

                part = {
                    "name": name,
                    "price": price,
                    "brand": brand
                }

                parts.append(part)

                added += 1

            except:
                pass

        save_data(PARTS_FILE, parts)

        await update.message.reply_text(
            f"✅ تم إضافة {added} قطعة"
        )

        user_state[user_id] = None

        return

    # =====================================================
    # بحث قطعة
    # =====================================================

    if text == "🔍 بحث قطعة":

        user_state[user_id] = "search_part"

        await update.message.reply_text(
            "🔍 اكتب اسم القطعة:"
        )

        return

    if user_state.get(user_id) == "search_part":

        keyword = text.lower().strip()

        results = []

        for p in parts:

            if keyword in p["name"].lower():
                results.append(p)

        if not results:

            await update.message.reply_text(
                "❌ لا توجد نتائج"
            )

            user_state[user_id] = None

            return

        msg = "🔍 النتائج:\n\n"

        for r in results:

            msg += (
                f"🧩 {r['name']}\n"
                f"🏷️ {r['brand']}\n"
                f"💰 {r['price']} ريال\n\n"
            )

        await update.message.reply_text(msg)

        user_state[user_id] = None

        return

    # =====================================================
    # أقسام القطع
    # =====================================================

    if text == "📂 أقسام القطع":

        if not parts:

            await update.message.reply_text(
                "❌ لا توجد قطع"
            )

            return

        sections = {}

        for p in parts:

            brand = p["brand"]

            if brand not in sections:
                sections[brand] = []

            sections[brand].append(p)

        msg = "📂 أقسام القطع:\n\n"

        for brand, items in sections.items():

            msg += f"🏷️ {brand}\n"

            for item in items:

                msg += (
                    f"• {item['name']} - "
                    f"{item['price']} ريال\n"
                )

            msg += "\n"

        await update.message.reply_text(msg)

        return

    # =====================================================
    # ديون
    # =====================================================

    if text == "💳 دين / تسليف":

        user_state[user_id] = "debt_name"

        await update.message.reply_text(
            "👤 اكتب اسم الشخص:"
        )

        return

    if user_state.get(user_id) == "debt_name":

        context.user_data["debt_name"] = text

        user_state[user_id] = "debt_amount"

        await update.message.reply_text(
            "💰 اكتب مبلغ الدين:"
        )

        return

    if user_state.get(user_id) == "debt_amount":

        try:

            amount = float(text)

            debt = {
                "name": context.user_data["debt_name"],
                "amount": amount
            }

            debts.append(debt)

            save_data(DEBTS_FILE, debts)

            await update.message.reply_text(
                f"✅ تم تسجيل الدين\n\n"
                f"👤 {debt['name']}\n"
                f"💰 {debt['amount']} ريال"
            )

            user_state[user_id] = None

        except:

            await update.message.reply_text(
                "❌ اكتب رقم صحيح"
            )

        return

    # =====================================================
    # عرض الديون
    # =====================================================

    if text == "📋 عرض الديون":

        if not debts:

            await update.message.reply_text(
                "✅ لا توجد ديون"
            )

            return

        msg = "📋 قائمة الديون:\n\n"

        for i, d in enumerate(debts):

            msg += (
                f"{i+1}️⃣ "
                f"{d['name']} - "
                f"{d['amount']} ريال\n"
            )

        msg += (
            "\nلحذف دين:\n"
            "حذف 1"
        )

        await update.message.reply_text(msg)

        return

    # =====================================================
    # حذف دين
    # =====================================================

    if text.startswith("حذف"):

        try:

            number = int(
                text.replace("حذف", "").strip()
            ) - 1

            if 0 <= number < len(debts):

                deleted = debts.pop(number)

                save_data(DEBTS_FILE, debts)

                await update.message.reply_text(
                    f"✅ تم حذف الدين\n\n"
                    f"👤 {deleted['name']}"
                )

            else:

                await update.message.reply_text(
                    "❌ الرقم غير موجود"
                )

        except:

            await update.message.reply_text(
                "❌ استخدم:\nحذف 1"
            )

        return

    # =====================================================
    # تسكير الحساب
    # =====================================================

    if text == "📊 تسكير الحساب":

        total_sales = sum(
            s["price"] for s in sales
        )

        context.user_data["total_sales"] = total_sales

        user_state[user_id] = "card"

        await update.message.reply_text(
            f"🛒 إجمالي المبيعات: {total_sales} ريال\n\n"
            f"💳 اكتب مبلغ الشبكة:"
        )

        return

    if user_state.get(user_id) == "card":

        try:

            context.user_data["card"] = float(text)

            user_state[user_id] = "expenses"

            await update.message.reply_text(
                "💸 اكتب المصاريف:"
            )

        except:

            await update.message.reply_text(
                "❌ اكتب رقم"
            )

        return

    if user_state.get(user_id) == "expenses":

        try:

            expenses = float(text)

            total_sales = context.user_data["total_sales"]
            card = context.user_data["card"]

            expected_cash = (
                total_sales
                - card
                - expenses
            )

            context.user_data["expected_cash"] = expected_cash

            user_state[user_id] = "actual"

            await update.message.reply_text(
                f"💰 المفروض بالدرج: {expected_cash}\n\n"
                f"💵 اكتب الكاش الفعلي:"
            )

        except:

            await update.message.reply_text(
                "❌ اكتب رقم"
            )

        return

    if user_state.get(user_id) == "actual":

        try:

            actual = float(text)

            expected = context.user_data["expected_cash"]

            diff = expected - actual

            msg = (
                f"📊 التقرير النهائي\n\n"
                f"💰 المفروض: {expected}\n"
                f"💵 الفعلي: {actual}\n\n"
            )

            if diff == 0:

                msg += "✅ الحساب مضبوط"

            elif diff > 0:

                msg += f"⚠️ يوجد عجز: {diff} ريال"

            else:

                msg += f"💰 يوجد زيادة: {abs(diff)} ريال"

            reports.append({
                "date": datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                ),
                "sales": context.user_data["total_sales"],
                "difference": diff
            })

            save_data(REPORTS_FILE, reports)

            await update.message.reply_text(msg)

            sales.clear()

            save_data(SALES_FILE, sales)

            user_state[user_id] = None

        except:

            await update.message.reply_text(
                "❌ اكتب رقم"
            )

        return

    # =====================================================
    # التقارير
    # =====================================================

    if text == "📅 التقارير":

        if not reports:

            await update.message.reply_text(
                "❌ لا توجد تقارير"
            )

            return

        msg = "📅 التقارير:\n\n"

        for r in reports:

            msg += (
                f"📅 {r['date']}\n"
                f"🛒 {r['sales']} ريال\n"
                f"💰 الفرق: {r['difference']} ريال\n\n"
            )

        await update.message.reply_text(msg)

        return

# =====================================================
# MAIN
# =====================================================

def main():

    app = Application.builder().token(TOKEN).build()

    app.add_handler(
        CommandHandler("start", start)
    )

    app.add_handler(
        MessageHandler(filters.TEXT, messages)
    )

    print("Bot Running...")

    app.run_polling()

# =====================================================
# RUN
# =====================================================

if __name__ == "__main__":
    main()
