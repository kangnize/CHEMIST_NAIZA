from flask import render_template, redirect, url_for, session, flash, request, jsonify, Blueprint
from app import mysql, app
from data import sales_data
from forms import EditForm


dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
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
                return redirect(url_for('aut.login'))

        except Exception as e:
            flash("An error occurred while fetching user data", "danger")
            app.logger.error(f"Error fetching user data: {e}")
            return redirect(url_for('auth.login'))

    return redirect(url_for('auth.login'))

@dashboard_bp.route('/edit', methods=['GET', 'POST'])
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
                return redirect(url_for('auth.login'))
        else:
            flash("User not logged in", "danger")
            return redirect(url_for('auth.login'))
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
        return redirect(url_for('dashboard.dashboard'))

    return render_template('edit.html', form=form)


@dashboard_bp.route('/fetch_sales_data', methods=['GET'])
def fetch_sales_data():
    date = request.args.get('date')
    sales = sales_data.get(date, [])
    return jsonify({"sales": sales})