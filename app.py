from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from flask_migrate import Migrate  # Import Flask-Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'  # Required for sessions
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contact.db'  # Database for contact submissions
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Folder where images will be saved
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed file types
db = SQLAlchemy(app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

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
    image1 = db.Column(db.String(200), nullable=True)
    image2 = db.Column(db.String(200), nullable=True)
    image3 = db.Column(db.String(200), nullable=True)
    image4 = db.Column(db.String(200), nullable=True)
    image5 = db.Column(db.String(200), nullable=True)
    price = db.Column(db.String(50), nullable=False)
    size = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    details = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Container {self.size} - {self.type}>'

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User()

# Helper function to check if the file has an allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

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
        # List to store the file paths for images
        images = []

        # Loop through image fields and save the uploaded files
        for i in range(1, 6):  # Check up to 5 image fields
            image_field = f'image{i}'
            if image_field in request.files:
                file = request.files[image_field]
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)  # Save the file to the folder
                    images.append(filename)  # Add the filename to the list

        # Create a new container product and save the image filenames to the database
        new_product = Container(
            image1=images[0] if len(images) > 0 else None,
            image2=images[1] if len(images) > 1 else None,
            image3=images[2] if len(images) > 2 else None,
            image4=images[3] if len(images) > 3 else None,
            image5=images[4] if len(images) > 4 else None,
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
        # Process the uploaded files for images, only if they are present in the request
        images = []
        for i in range(1, 6):  # Loop through the five image fields
            image_field = f'image{i}'
            if image_field in request.files:  # Check if the image field exists in the request
                file = request.files[image_field]
                if file and allowed_file(file.filename):  # Check if the file is valid
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)  # Save the file to the server
                    images.append(filename)  # Add the filename to the list

        # Update the product in the database
        container.image1 = images[0] if len(images) > 0 else container.image1
        container.image2 = images[1] if len(images) > 1 else container.image2
        container.image3 = images[2] if len(images) > 2 else container.image3
        container.image4 = images[3] if len(images) > 3 else container.image4
        container.image5 = images[4] if len(images) > 4 else container.image5
        container.price = request.form['price']
        container.size = request.form['size']
        container.type = request.form['type']
        container.details = request.form['details']

        db.session.commit()
        return redirect(url_for('admin'))  # Redirect to the admin panel after editing

    return render_template('edit_product.html', container=container)

# Route for deleting a product
@app.route('/admin/products/delete/<int:container_id>', methods=['POST'])
@login_required
def delete_product(container_id):
    container = Container.query.get_or_404(container_id)
    db.session.delete(container)
    db.session.commit()
    return redirect(url_for('admin'))  # Redirect to admin panel after deletion

# Route for deleting a contact message
@app.route('/admin/contact/delete/<int:contact_id>', methods=['POST'])
@login_required
def delete_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    return redirect(url_for('admin'))  # Redirect to admin page after deleting the contact message

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

# Ensure that the database is created
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database tables if they do not exist
    app.run(debug=True)
