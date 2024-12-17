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
    password_hash = generate_password_hash('password123')  # Store the hashed password

# Create a Contact model for storing contact form submissions
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Contact {self.name}>'

# Create a Container model for storing container products
class Container(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(200), nullable=False)  # Image URL or file path
    price = db.Column(db.String(50), nullable=False)   # Price string (e.g., "$2,000")
    size = db.Column(db.String(50), nullable=False)    # Size of the container (e.g., "20ft")
    type = db.Column(db.String(50), nullable=False)    # Type (e.g., "Used" or "One-trip")
    details = db.Column(db.Text, nullable=False)       # Product description

    def __repr__(self):
        return f'<Container {self.size} - {self.type}>'

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
        if username == 'admin' and check_password_hash(User.password_hash, password):
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
    containers = Container.query.all()
    return render_template('products.html', containers=containers)

# Route for container specifications page
@app.route('/products/<int:container_id>')
def product_specifications(container_id):
    container = Container.query.get_or_404(container_id)
    return render_template('specifications.html', container=container)

# Route for the admin dashboard
@app.route('/admin')
@login_required
def admin():
    contacts = Contact.query.all()  # Retrieve all contact submissions
    containers = Container.query.all()  # Retrieve all container products
    return render_template('admin_panel.html', contacts=contacts, containers=containers)

# Route for adding a new product
@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        # Create a new container product from form data
        new_product = Container(
            image=request.form['image'],
            price=request.form['price'],
            size=request.form['size'],
            type=request.form['type'],
            details=request.form['details']
        )
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for('admin'))  # Redirect to admin page after adding the product

    return render_template('add_product.html')

# Route for editing a product
@app.route('/admin/products/edit/<int:container_id>', methods=['GET', 'POST'])
@login_required
def edit_product(container_id):
    container = Container.query.get_or_404(container_id)

    if request.method == 'POST':
        container.image = request.form['image']
        container.price = request.form['price']
        container.size = request.form['size']
        container.type = request.form['type']
        container.details = request.form['details']
        db.session.commit()
        return redirect(url_for('admin'))  # Redirect to admin panel after editing

    return render_template('edit_product.html', container=container)


# Route for deleting a product
@app.route('/admin/products/delete/<int:container_id>', methods=['POST'])
@login_required
def delete_product(container_id):
    container = Container.query.get_or_404(container_id)
    db.session.delete(container)
    db.session.commit()
    return redirect(url_for('admin'))  # Redirect to admin panel after deletion


# Route for viewing contact submissions
@app.route('/admin/contacts')
@login_required
def admin_contacts():
    contacts = Contact.query.all()  # Retrieve all contact submissions
    return render_template('admin_contacts.html', contacts=contacts)

# 404 Page Not Found handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', message="Page not found"), 404

if __name__ == '__main__':
    app.run(debug=True)
