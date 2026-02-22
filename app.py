import os
from flask import Flask, render_template, request, redirect, url_for
from config import Config
from models import db, Product, Enquiry, Admin
from flask import session
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from functools import wraps


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
mail = Mail(app)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    products = Product.query.all()
    return render_template("index.html", products=products)

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
        recipients=["gautam2002jha@gmail.com"]
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

@app.route("/admin/add-product", methods=["POST"])
def add_product():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    name = request.form.get("name")
    description = request.form.get("description")
    image_file = request.files.get("image")

    filename = None

    if image_file and image_file.filename != "":
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        image_file.save(image_path)

    new_product = Product(
        name=name,
        description=description,
        image=filename
    )

    db.session.add(new_product)
    db.session.commit()

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/delete/<int:id>")
def delete_product(id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()

    return redirect(url_for("admin_dashboard"))

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if __name__ == "__main__":
    app.run()