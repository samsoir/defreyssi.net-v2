// Maison de Freyssinet Theme - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Add any interactive functionality here
    console.log('Maison de Freyssinet theme loaded');
    
    // Example: Add smooth scrolling to anchor links
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});