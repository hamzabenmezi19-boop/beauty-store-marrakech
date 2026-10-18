from flask import Flask, render_template, request, redirect, url_for, session, flash
from urllib.parse import quote

app = Flask(__name__)
app.secret_key = "beauty-store-change-this-secret-key"

# رقم واتساب المتجر بصيغة دولية: المغرب 212، دون الصفر الأول
WHATSAPP_NUMBER = "212643029889"

# المنتجات والأسعار بالدرهم المغربي
PRODUCTS = [
    {
        "id": 1,
        "name": "مجموعة مكياج أنيقة",
        "category": "المكياج",
        "price": 149,
        "image": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&w=900&q=85",
        "tag": "الأكثر طلباً"
    },
    {
        "id": 2,
        "name": "أحمر شفاه",
        "category": "المكياج",
        "price": 59,
        "image": "https://images.unsplash.com/photo-1586495777744-4413f21062fa?auto=format&fit=crop&w=900&q=85",
        "tag": "جديد"
    },
    {
        "id": 3,
        "name": "عطر أنيق",
        "category": "العطور",
        "price": 179,
        "image": "https://images.unsplash.com/photo-1541643600914-78b084683601?auto=format&fit=crop&w=900&q=85",
        "tag": "اختيار مميز"
    },
    {
        "id": 4,
        "name": "منتجات العناية بالبشرة",
        "category": "العناية بالبشرة",
        "price": 119,
        "image": "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?auto=format&fit=crop&w=900&q=85",
        "tag": ""
    },
    {
        "id": 5,
        "name": "إكسسوارات أنثوية",
        "category": "الإكسسوارات",
        "price": 89,
        "image": "https://images.unsplash.com/photo-1617038220319-276d3cfab638?auto=format&fit=crop&w=900&q=85",
        "tag": "أنيق"
    },
    {
        "id": 6,
        "name": "فرش مكياج",
        "category": "المكياج",
        "price": 75,
        "image": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=900&q=85",
        "tag": ""
    },
    {
        "id": 7,
        "name": "كريم للعناية",
        "category": "العناية بالبشرة",
        "price": 99,
        "image": "https://images.unsplash.com/photo-1556229010-6c3f2c9ca5f8?auto=format&fit=crop&w=900&q=85",
        "tag": ""
    },
    {
        "id": 8,
        "name": "حقيبة صغيرة",
        "category": "الإكسسوارات",
        "price": 129,
        "image": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?auto=format&fit=crop&w=900&q=85",
        "tag": "مميز"
    },
]


# بيانات مشتركة لجميع الصفحات
@app.context_processor
def shared_data():
    cart_data = session.get("cart", {})
    count = sum(int(qty) for qty in cart_data.values())
    return {"cart_count": count}


# الصفحة الرئيسية وتصنيفات المنتجات
@app.route("/")
def index():
    category = request.args.get("category", "الكل")

    categories = [
        "الكل",
        "المكياج",
        "العناية بالبشرة",
        "العطور",
        "الإكسسوارات"
    ]

    if category not in categories:
        category = "الكل"

    products = (
        PRODUCTS
        if category == "الكل"
        else [p for p in PRODUCTS if p["category"] == category]
    )

    return render_template(
        "index.html",
        products=products,
        categories=categories,
        selected=category
    )


# إضافة منتج إلى السلة
@app.route("/add/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    product_exists = any(
        p["id"] == product_id for p in PRODUCTS
    )

    if not product_exists:
        flash("هذا المنتج غير موجود.")
        return redirect(url_for("index"))

    cart_data = session.get("cart", {})
    key = str(product_id)

    cart_data[key] = int(cart_data.get(key, 0)) + 1
    session["cart"] = cart_data

    flash("تمت إضافة المنتج إلى السلة بنجاح.")
    return redirect(request.referrer or url_for("index"))


# عرض السلة وحساب المجموع
@app.route("/cart")
def cart():
    cart_data = session.get("cart", {})
    items = []
    total = 0

    for product in PRODUCTS:
        qty = int(cart_data.get(str(product["id"]), 0))

        if qty > 0:
            subtotal = qty * product["price"]

            items.append({
                "product": product,
                "qty": qty,
                "subtotal": subtotal
            })

            total += subtotal

    return render_template(
        "cart.html",
        items=items,
        total=total
    )


# زيادة أو إنقاص الكمية
@app.route("/change/<int:product_id>", methods=["POST"])
def change_quantity(product_id):
    cart_data = session.get("cart", {})
    key = str(product_id)
    action = request.form.get("action")

    if not any(p["id"] == product_id for p in PRODUCTS):
        return redirect(url_for("cart"))

    if key in cart_data:
        if action == "plus":
            cart_data[key] = int(cart_data[key]) + 1

        elif action == "minus":
            new_qty = int(cart_data[key]) - 1

            if new_qty <= 0:
                cart_data.pop(key)
            else:
                cart_data[key] = new_qty

    session["cart"] = cart_data
    return redirect(url_for("cart"))


# إرسال الطلب إلى واتساب
@app.route("/checkout", methods=["POST"])
def checkout():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    address = request.form.get("address", "").strip()

    cart_data = session.get("cart", {})

    if not cart_data:
        flash("السلة فارغة. أضيفي المنتجات أولاً.")
        return redirect(url_for("cart"))

    if not name or not phone or not address:
        flash("يرجى ملء الاسم ورقم الهاتف والعنوان.")
        return redirect(url_for("cart"))

    lines = []
    total = 0

    for product in PRODUCTS:
        qty = int(cart_data.get(str(product["id"]), 0))

        if qty > 0:
            subtotal = product["price"] * qty
            total += subtotal

            lines.append(
                f"- {product['name']} × {qty} = {subtotal} درهم"
            )

    message_text = (
        "طلب جديد من Beauty Store Marrakech\n\n"
        f"الاسم: {name}\n"
        f"هاتف الزبون: {phone}\n"
        f"العنوان: {address}\n\n"
        "تفاصيل الطلب:\n"
        + "\n".join(lines)
        + f"\n\nالمجموع الإجمالي: {total} درهم مغربي"
    )

    # ترميز الرسالة حتى تظهر العربية بصورة صحيحة في واتساب
    message = quote(message_text)

    # الاحتفاظ بالسلة إلى أن يتأكد المتجر من الطلب
    whatsapp_url = (
        f"https://wa.me/{WHATSAPP_NUMBER}?text={message}"
    )

    return redirect(whatsapp_url)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)