from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contact.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# User model for Flask-Login
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Contact model for storing contact form submissions
class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Contact {self.name}>'


# Container model for storing container products
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


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin'))
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    message = None
    if request.method == 'POST':
        name = request.form.get('name', 'Unknown')
        email = request.form.get('email', 'Unknown')
        message_content = request.form.get('message', '')

        print(f"Name: {name}")
        print(f"Email: {email}")
        print(f"Message: {message_content}")

        new_contact = Contact(name=name, email=email, message=message_content)
        db.session.add(new_contact)
        db.session.commit()

        message = "Your message has been sent! We'll get back to you soon."

    return render_template('contact.html', message=message)


@app.route('/learn')
def learn():
    return render_template('learn.html')


@app.route('/products')
def products():
    containers = Container.query.all()
    return render_template('products.html', containers=containers)


@app.route('/products/<int:container_id>')
def product_specifications(container_id):
    container = Container.query.get_or_404(container_id)
    return render_template('specifications.html', container=container)


@app.route('/admin')
@login_required
def admin():
    contacts = Contact.query.all()
    containers = Container.query.all()
    return render_template('admin_panel.html', contacts=contacts, containers=containers)


@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        images = []

        for i in range(1, 6):
            image_field = f'image{i}'
            if image_field in request.files:
                file = request.files[image_field]
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    images.append(filename)

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
        return redirect(url_for('admin'))

    return render_template('add_product.html')


@app.route('/admin/products/edit/<int:container_id>', methods=['GET', 'POST'])
@login_required
def edit_product(container_id):
    container = Container.query.get_or_404(container_id)

    if request.method == 'POST':
        images = []
        for i in range(1, 6):
            image_field = f'image{i}'
            if image_field in request.files:
                file = request.files[image_field]
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    images.append(filename)

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
        return redirect(url_for('admin'))

    return render_template('edit_product.html', container=container)


@app.route('/admin/products/delete/<int:container_id>', methods=['POST'])
@login_required
def delete_product(container_id):
    container = Container.query.get_or_404(container_id)
    db.session.delete(container)
    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/admin/contact/delete/<int:contact_id>', methods=['POST'])
@login_required
def delete_contact(contact_id):
    contact = Contact.query.get_or_404(contact_id)
    db.session.delete(contact)
    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/admin/contacts')
@login_required
def admin_contacts():
    contacts = Contact.query.all()
    return render_template('admin_contacts.html', contacts=contacts)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', message="Page not found"), 404


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
