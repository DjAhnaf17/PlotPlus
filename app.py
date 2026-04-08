import os
import pickle
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from dotenv import load_dotenv
from models import db, User

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default_secret')
# Fallback to local SQLite if DATABASE_URL is not set or if PostgreSQL connection fails
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Load ML Model
model_path = os.path.join(os.path.dirname(__file__), 'Model', 'model.pkl')
try:
    with open(model_path, 'rb') as f:
        ml_model = pickle.load(f)
except FileNotFoundError:
    print("Warning: ML Model not found. Please run Model/train.py first.")
    ml_model = None

# Initialize Database securely within application context
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Warning: Database connection failed. Falling back to SQLite. Error: {e}")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
        db.create_all()

@app.route('/')
@login_required
def index():
    return render_template('index.html', title='House Price Predictor')

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    if ml_model is None:
        return jsonify({'error': 'Model not loaded.'}), 500
    try:
        data = request.get_json()
        area = int(data.get('area', 0))
        rooms = int(data.get('rooms', 0))
        kitchen = int(data.get('kitchen', 0))
        
        prediction = ml_model.predict([[area, rooms, kitchen]])
        predicted_price = float(prediction[0])
        return jsonify({'price': predicted_price, 'formatted': f'₹ {predicted_price:,.2f}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not email or not password:
            flash('Please fill out all fields.', 'danger')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords must match.', 'danger')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists.', 'danger')
            return redirect(url_for('register'))

        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account created! Proceed to login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
