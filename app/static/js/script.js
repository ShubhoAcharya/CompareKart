document.addEventListener("DOMContentLoaded", function() {
    var lazyloadImages = document.querySelectorAll(".lazyload");
    var imageObserver = new IntersectionObserver(function(entries, observer) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                var image = entry.target;
                image.style.backgroundImage = "url('" + image.getAttribute("data-src") + "')";
                image.classList.remove("lazyload");
                imageObserver.unobserve(image);
            }
        });
    });

    lazyloadImages.forEach(function(image) {
        imageObserver.observe(image);
    });
});

document.addEventListener("DOMContentLoaded", function() {
    var searchButton = document.getElementById("searchButton");

    searchButton.addEventListener("click", function() {
        var searchQuery = document.getElementById("searchQuery").value;
        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: searchQuery }),
        })
        .then(response => response.json())
        .then(data => {
            var resultsDiv = document.getElementById("results");
            resultsDiv.innerHTML = `
                <p>Flipkart: <a href="${data.flipkart_link}" target="_blank">${data.flipkart_link}</a></p>
                <p>Amazon: <a href="${data.amazon_link}" target="_blank">${data.amazon_link}</a></p>
            `;
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });
});

