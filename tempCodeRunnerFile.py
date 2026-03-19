

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

