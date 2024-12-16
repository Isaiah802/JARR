from flask import Flask, render_template, request

app = Flask(__name__)

# Sample data for containers
CONTAINERS = [
    {"id": 1, "image": "/static/images/container1.jpg", "price": "$2,000", "size": "20ft", "type": "Used", "details": "Great for storage."},
    {"id": 2, "image": "/static/images/20onetrip.jpg", "price": "$2,500", "size": "40ft", "type": "One-trip", "details": "Like new, perfect for shipping."},
    {"id": 3, "image": "/static/images/container3.jpg", "price": "$1,800", "size": "20ft", "type": "Used", "details": "Weather-resistant."},
    {"id": 4, "image": "/static/images/container4.jpg", "price": "$3,000", "size": "40ft", "type": "One-trip", "details": "Ideal for large storage needs."},
]

@app.route('/')
def home():
    return render_template('home.html')




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

        # Display a confirmation message on the page
        message = "Your message has been sent! We'll get back to you soon."

    return render_template('contact.html', message=message)




@app.route('/learn')
def learn():
    return render_template('learn.html')

@app.route('/products')
def products():
    # Pass the container data to the inventory page
    return render_template('products.html', items=CONTAINERS)

@app.route('/products/<int:container_id>')
def product_specifications(container_id):
    # Find the container with the matching ID
    container = next((item for item in CONTAINERS if item["id"] == container_id), None)

    # If the container is not found, return a 404 error
    if not container:
        return render_template('404.html', message="Container not found"), 404

    # Render the specifications page with the container data
    return render_template('specifications.html', container=container)

# 404 Page Not Found handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', message="Page not found"), 404

if __name__ == '__main__':
    app.run(debug=True)
