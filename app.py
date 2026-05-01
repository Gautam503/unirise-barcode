import os
from flask import Flask, flash, render_template, request, redirect, url_for
from config import Config
from models import db, Product, Enquiry, Admin
from flask import session
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from functools import wraps
from flask import request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask import send_from_directory
import re

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
mail = Mail(app)

with app.app_context():
    db.create_all()

@app.context_processor
def inject_products():
    products = Product.query.all()
    return dict(all_products=products)

@app.route("/")
def home():
    latest_products = Product.query.filter_by(featured=True).limit(3).all()
    return render_template("index.html", latest_products=latest_products)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/product/<int:id>")
def product_detail(id):
    product = Product.query.get_or_404(id)
    return render_template("product_detail.html", product=product)

@app.route("/enquiry", methods=["POST"])
def enquiry():
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    message_text = request.form.get("message")

    new_enquiry = Enquiry(
        name=name,
        email=email,
        phone=phone,
        message=message_text
    )
    db.session.add(new_enquiry)
    db.session.commit()

    # Send email to admin
    msg = Message(
        subject="New Enquiry - Unirise Barcode",
        recipients=["gpljha.medi@gmail.com"]
    )

    msg.body = f"""
    New enquiry received:

    Name: {name}
    Email: {email}
    Phone: {phone}

    Message:
    {message_text}
    """

    mail.send(msg)

    return redirect(url_for("home"))



@app.route("/unirise-admin-portal", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        admin = Admin.query.filter_by(username=username).first()

        if admin and admin.check_password(password):
            session["admin"] = admin.username
            return redirect(url_for("admin_dashboard"))

    return render_template("admin_login.html")

@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    products = Product.query.all()
    return render_template("admin_dashboard.html", products=products)

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("home"))

@app.route("/admin/add-product", methods=["GET","POST"])
def add_product():

    if "admin" not in session:
        return redirect(url_for("admin_login"))

    name = request.form.get("name")
    description = request.form.get("description")
    category = request.form.get("category")
    subcategory = request.form.get("subcategory")
    image_file = request.files.get("image")

    # FEATURED PRODUCT
    featured = True if request.form.get("featured") else False

    filename = None

    if image_file and image_file.filename != "":
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image_file.save(image_path)

    new_product = Product(
        name=name,
        description=description,
        category=category,
        subcategory=subcategory,
        image=filename,
        featured=featured
    )

    db.session.add(new_product)
    db.session.commit()

    return redirect(url_for("admin_dashboard"))

@app.route("/subcategory/<name>")
def subcategory_products(name):
    products = Product.query.filter_by(subcategory=name).all()
    return render_template("products.html", products=products)

@app.route("/admin/delete/<int:id>")
def delete_product(id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()

    return redirect(url_for("admin_dashboard"))

@app.route("/company-profile")
def company_profile():
    return render_template("company_profile.html")

@app.route('/change-password', methods=['GET', 'POST'])
def change_password():

    # Check if admin is logged in
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    admin = Admin.query.first()

    if request.method == "POST":

        old_password = request.form['old_password']
        new_password = request.form['new_password']

        if not admin.check_password(old_password):
            flash("Old password is incorrect", "danger")
            return redirect(url_for('change_password'))

        admin.set_password(new_password)
        db.session.commit()

        flash("Password updated successfully", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template("change_password.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/product-enquiry", methods=["POST"])
def product_enquiry():

    name = request.form.get("name")
    phone = request.form.get("phone")
    product_name = request.form.get("product_name")

    # Save to database
    new_enquiry = Enquiry(
        name=name,
        phone=phone,
        message=f"Callback request for product: {product_name}"
    )
    db.session.add(new_enquiry)
    db.session.commit()

    # Send Email
    msg = Message(
        subject="New Product Enquiry - Unirise Barcode",
        recipients=[app.config["MAIL_USERNAME"]]
    )

    msg.body = f"""
    New Callback Request

    Product: {product_name}
    Name: {name}
    Phone: {phone}
    """

    mail.send(msg)

    flash("Thank you! We will contact you shortly.", "success")

    return redirect(url_for("home"))

@app.route("/products")
def all_products():

    category = request.args.get("category")
    subcategory = request.args.get("subcategory")
    search = request.args.get("search")

    query = Product.query

    if category:
        query = query.filter(Product.category == category)

    if subcategory:
        query = query.filter(Product.subcategory == subcategory)

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    products = query.all()

    return render_template("products.html", products=products)


@app.route("/products/<category>")
def category_products(category):
    products = Product.query.filter_by(category=category).all()
    return render_template("products.html", products=products)

@app.route("/service-amc")
def service_amc():
    return render_template("service_amc.html")

@app.route("/software-solution")
def software_solution():
    return render_template("software_solution.html")


@app.route("/vision-solution")
def vision_solution():
    return render_template("vision_solution.html")

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('static', 'sitemap.xml')


UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
