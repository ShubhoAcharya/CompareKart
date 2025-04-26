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

    var searchButton = document.getElementById("searchButton");
    var searchQueryInput = document.getElementById("searchQuery");

    function handleSearch() {
        var searchQuery = searchQueryInput.value;
        if (!searchQuery) {
            alert("Please enter a search term");
            return;
        }
    
        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: searchQuery }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Redirect to product display page with the found product
                window.location.href = data.redirect;
            } else if (data.status === 'not_found') {
                // Show not found message
                var resultsDiv = document.getElementById("results");
                resultsDiv.innerHTML = `
                    <div class="error-message">
                        <i class="fas fa-exclamation-circle"></i>
                        <p>${data.message}</p>
                    </div>
                `;
            } else {
                throw new Error(data.message || 'Search failed');
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            var resultsDiv = document.getElementById("results");
            resultsDiv.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-circle"></i>
                    <p>Error: ${error.message}</p>
                </div>
            `;
        });
    }
    searchButton.addEventListener("click", handleSearch);

    searchQueryInput.addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            handleSearch();
        }
    });


    // Scroll to Top Button
    const scrollToTopButton = document.getElementById("scrollToTop");

    // Show or hide the button based on scroll position
    window.addEventListener("scroll", function () {
        if (window.scrollY > 300) {
            scrollToTopButton.classList.add("show");
        } else {
            scrollToTopButton.classList.remove("show");
        }
    });

    // Scroll to the top when the button is clicked
    scrollToTopButton.addEventListener("click", function () {
        window.scrollTo({
            top: 0,
            behavior: "smooth",
        });
    });

    const accordions = document.querySelectorAll(".accordion");

    accordions.forEach((accordion) => {
        const button = accordion.querySelector("button");
        const detailsWrapper = accordion.querySelector(".accordion_details_wrapper");

        button.addEventListener("click", function () {
            // Toggle the "open" class on the accordion
            accordion.classList.toggle("open");

            // Adjust the height of the details wrapper
            if (accordion.classList.contains("open")) {
                detailsWrapper.style.height = detailsWrapper.scrollHeight + "px";
            } else {
                detailsWrapper.style.height = "0";
            }
        });
    });

    const productUrlInput = document.getElementById("product-search-bar");
    if (!productUrlInput) {
        console.error("Element with ID 'product-search-bar' not found.");
    }

    // Handle paste event
    productUrlInput.addEventListener("paste", function () {
        console.log("Paste event triggered");
        setTimeout(() => {
            const productUrl = productUrlInput.value.trim();
            console.log("Pasted URL:", productUrl);
            if (productUrl) {
                fetch('/process_url', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ url: productUrl }),
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success' || data.status === 'exists') {
                        console.log(`Redirecting to /product_display for ID: ${data.id}`);
                        window.location.href = `/product_display?id=${data.id}`;
                    } else {
                        console.error("Error:", data.message);
                        alert("Error processing URL: " + data.message);
                    }
                })
                .catch((error) => {
                    console.error("Error:", error);
                    alert("Error occurred while processing the URL.");
                });
            }
        }, 100);
    });
    
    // Function to process the URL
    function processUrl(productUrl) {
        console.log("Processing URL:", productUrl); // Debug log
        fetch('/process_url', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: productUrl }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                console.log(`URL saved successfully. Row ID: ${data.id}`);
            } else if (data.status === 'exists') {
                console.log(`URL already exists in the database. Row ID: ${data.id}`);
            } else {
                console.error("Error:", data.message);
            }
        })
        .catch((error) => {
            console.error("Error:", error);
        });
    }
});
