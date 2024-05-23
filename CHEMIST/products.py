from flask import Flask, render_template, redirect, url_for, session, flash, request, jsonify, Blueprint
from app import mysql, app
from data import products_data, sales_data
from .forms import EditForm


product_bp = Blueprint('products', __name__)

@product_bp.route('/products')
def products():
    return render_template('products.html', products=products)

# Dummy data for products and cart
products = products_data
cart = {}

@product_bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form['quantity'])
    if product_id in products_data:
        if product_id in cart:
            cart[product_id] += quantity
        else:
            cart[product_id] = quantity
    return redirect(url_for('view_cart'))

@product_bp.route('/cart')
def view_cart():
    cart_items = {
        product_id: {
            "quantity": quantity,
            "name": products[product_id]["name"],
            "price": products[product_id]["price"],
            "image_url": products[product_id]["image_url"]
        }
        for product_id, quantity in cart.items()
    }
    total_price = sum(item['price'] * item['quantity'] for item in cart_items.values())
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@product_bp.route('/update_cart', methods=['POST'])
def update_cart():
    product_id = int(request.form['product_id'])
    quantity = int(request.form['quantity'])

    if product_id in cart:
        cart[product_id] = quantity

    return redirect(url_for('view_cart'))

@product_bp.route('/delete_item/<int:product_id>', methods=['POST'])
def delete_item(product_id):
    # Check if the product is in the cart
    if product_id in cart:
        # Remove the item from the cart
        del cart[product_id]
    return redirect(url_for('view_cart'))

# Define a route to render the form
@product_bp.route('/add_product', methods=['GET'])
def add_product_form():
    return render_template('add_product.html')

# Define a route to handle form submission
@product_bp.route('/add_product', methods=['POST'])
def add_product():
    # Get form data
    name = request.form['name']
    price = float(request.form['price'])
    description = request.form['description']
    image = request.files['image']

    # Save image to a folder
    image_path = os.path.join('uploads', image.filename)
    image.save(image_path)

    # Insert product data into the database
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO products (name, price, description, image) VALUES (%s, %s, %s, %s)",
                (name, price, description, image_path))
    mysql.connection.commit()
    cur.close()

    return 'Product added successfully'

@product_bp.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']

        try:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT name, email FROM admin WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()

            if user:
                user_name = user[0]
                user_email = user[1]
                return render_template('dashboard.html', user_name=user_name, user_email=user_email)
            else:
                flash("User not found", "danger")
                return redirect(url_for('login'))

        except Exception as e:
            flash("An error occurred while fetching user data", "danger")
            app.logger.error(f"Error fetching user data: {e}")
            return redirect(url_for('login'))

    return redirect(url_for('login'))

@product_bp.route('/edit', methods=['GET', 'POST'])
def edit():
    form = EditForm()
    if request.method == 'GET':
        # Retrieve user data from the database and pre-fill the form fields
        user_id = session.get('user_id')
        if user_id:
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT name, email FROM admin WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            cursor.close()

            if user_data:
                form.name.data = user_data[0]
                form.email.data = user_data[1]
            else:
                flash("User data not found", "danger")
                return redirect(url_for('login'))
        else:
            flash("User not logged in", "danger")
            return redirect(url_for('login'))
    elif request.method == 'POST' and form.validate_on_submit():
        # Update user data in the database
        name = form.name.data
        email = form.email.data
        user_id = session.get('user_id')

        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE admin SET name = %s, email = %s WHERE id = %s", (name, email, user_id))
        mysql.connection.commit()
        cursor.close()

        flash("Profile updated successfully", "success")
        return redirect(url_for('dashboard'))

    return render_template('edit.html', form=form)


@product_bp.route('/fetch_sales_data', methods=['GET'])
def fetch_sales_data():
    date = request.args.get('date')
    sales = sales_data.get(date, [])
    return jsonify({"sales": sales})