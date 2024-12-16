from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Required for sessions
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contact.db'  # Database for contact submissions
db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirect to login page if not logged in

# Create a User model for Flask-Login
class User(UserMixin):
    id = 1
    username = 'admin'
    password = generate_password_hash('password123')  # Hashed password for admin

# Create a Contact model for storing contact form submissions
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Contact {self.name}>'

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User()

# Route for logging in
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and check_password_hash(User.password, password):
            user = User()
            login_user(user)
            return redirect(url_for('admin'))  # Redirect to admin page after login
    return render_template('login.html')  # Render login page

# Route for logging out
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))  # Redirect to login page after logout

# Route for the home page
@app.route('/')
def home():
    return render_template('home.html')

# Route for the contact page, handling GET and POST requests
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    message = None
    if request.method == 'POST':
        # Safely retrieve form data
        name = request.form.get('name', 'Unknown')
        email = request.form.get('email', 'Unknown')
        message_content = request.form.get('message', '')

        # Log form data (this could be sent to an email in production)
        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Message: {message_content}")

        # Save the contact submission to the database
        new_contact = Contact(name=name, email=email, message=message_content)
        db.session.add(new_contact)
        db.session.commit()

        # Display a confirmation message on the page
        message = "Your message has been sent! We'll get back to you soon."

    return render_template('contact.html', message=message)

# Route for the learn page
@app.route('/learn')
def learn():
    return render_template('learn.html')

# Route for the products page
@app.route('/products')
def products():
    # Sample data for containers
    CONTAINERS = [
        {"id": 1, "image": "/static/images/container1.jpg", "price": "$2,000", "size": "20ft", "type": "Used", "details": "Great for storage."},
        {"id": 2, "image": "/static/images/20onetrip.jpg", "price": "$2,500", "size": "40ft", "type": "One-trip", "details": "Like new, perfect for shipping."},
        {"id": 3, "image": "/static/images/container3.jpg", "price": "$1,800", "size": "20ft", "type": "Used", "details": "Weather-resistant."},
        {"id": 4, "image": "/static/images/container4.jpg", "price": "$3,000", "size": "40ft", "type": "One-trip", "details": "Ideal for large storage needs."},
    ]
    return render_template('products.html', items=CONTAINERS)

# Route for container specifications page
@app.route('/products/<int:container_id>')
def product_specifications(container_id):
    # Find the container with the matching ID
    container = next((item for item in CONTAINERS if item["id"] == container_id), None)
    if not container:
        return render_template('404.html', message="Container not found"), 404
    return render_template('specifications.html', container=container)

# Route for admin page
@app.route('/admin')
@login_required
def admin():
    contacts = Contact.query.all()  # Retrieve all contact submissions
    return render_template('admin.html', contacts=contacts)

# 404 Page Not Found handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', message="Page not found"), 404

if __name__ == '__main__':
    app.run(debug=True)
