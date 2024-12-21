document.addEventListener("DOMContentLoaded", function() {
    const images = document.querySelectorAll('img.lazy');

    const loadImage = (image) => {
        image.src = image.dataset.src;
        image.classList.add('loaded');
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                loadImage(entry.target);
                observer.unobserve(entry.target);
            }
        });
    }, {
        rootMargin: '50px 0px',
        threshold: 0.01
    });

    images.forEach(image => observer.observe(image));
});
