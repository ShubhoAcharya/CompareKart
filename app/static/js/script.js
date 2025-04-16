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
                <div class="link-container">
                    <a href="${data.amazon_link}" class="styled-link amazon-link" target="_blank">
                        <i class="fas fa-shopping-cart"></i> Amazon: Go to Amazon
                    </a>
                    <a href="${data.flipkart_link}" class="styled-link flipkart-link" target="_blank">
                        <i class="fas fa-shopping-cart"></i> Flipkart: Go to Flipkart
                    </a>
                </div>
            `;
        })
        .catch((error) => {
            console.error('Error:', error);
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
        console.log("Paste event triggered"); // Debug log
        setTimeout(() => {
            const productUrl = productUrlInput.value.trim();
            console.log("Pasted URL:", productUrl); // Debug log
            if (productUrl) {
                // Send the URL to the backend to process it
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
                        console.log(`URL processed successfully. Row ID: ${data.id}`);
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
        }, 100); // Delay to ensure the pasted value is available
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
