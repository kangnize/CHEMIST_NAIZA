import os
from flask import render_template, redirect, url_for, request, Blueprint
from app import mysql
from data import products_data


products_bp = Blueprint('products', __name__)

@products_bp.route('/products')
def products():
    return render_template('products.html', products=products)

# Dummy data for products and cart
products = products_data
cart = {}

@products_bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    quantity = int(request.form['quantity'])
    if product_id in products_data:
        if product_id in cart:
            cart[product_id] += quantity
        else:
            cart[product_id] = quantity
    return redirect(url_for('products.view_cart'))

@products_bp.route('/cart')
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

@products_bp.route('/update_cart', methods=['POST'])
def update_cart():
    product_id = int(request.form['product_id'])
    quantity = int(request.form['quantity'])

    if product_id in cart:
        cart[product_id] = quantity

    return redirect(url_for('products.view_cart'))

@products_bp.route('/delete_item/<int:product_id>', methods=['POST'])
def delete_item(product_id):
    # Check if the product is in the cart
    if product_id in cart:
        # Remove the item from the cart
        del cart[product_id]
    return redirect(url_for('products.view_cart'))

# Define a route to render the form
@products_bp.route('/add_product', methods=['GET'])
def add_product_form():
    return render_template('add_product.html')

# Define a route to handle form submission
@products_bp.route('/add_product', methods=['POST'])
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
