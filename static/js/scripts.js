// comment Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const flashMessage = document.getElementById('flash-message');

    if (flashMessage) {
        // Set how long the flash message will stay visible (in milliseconds)
        setTimeout(function() {
            // Add a class or directly hide the message after the time
            flashMessage.classList.remove('show'); // Removes the 'show' class to hide the message
            flashMessage.classList.add('fade'); // Optionally add a fade effect class (if you have CSS for fading)
        }, 5000); // Flash message duration (5000ms = 5 seconds)
    }
});
