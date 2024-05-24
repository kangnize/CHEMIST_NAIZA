from flask import render_template, redirect, url_for, session, flash, Blueprint
import bcrypt
from app import mysql, app
from forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    return render_template('index.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, name, email, password FROM admin WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['user_email'] = user[2]
            flash("Login successful.", "success")
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash("Invalid email or password. Please try again.", "danger")
            return redirect(url_for('auth.login'))

    return render_template('login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO admin (name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
            mysql.connection.commit()
            cursor.close()
        except Exception as e:
            flash("An error occurred during registration. Please try again.", "danger")
            app.logger.error("Failed to register user: %s", e)
            return redirect(url_for('auth.register'))

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.pop('user_email', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.index'))
