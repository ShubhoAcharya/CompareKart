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


// Category handling with smooth animations
document.querySelectorAll('.category-link').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        const categoryId = this.getAttribute('data-category-id');
        const categoryName = this.querySelector('.category-name').textContent;
        
        // Show the section when a category is clicked
        document.getElementById('categoryProducts').style.display = 'block';
        loadCategoryProducts(categoryId, categoryName);
        
        // Update active state
        document.querySelectorAll('.category-link').forEach(link => {
            link.classList.remove('active');
        });
        this.classList.add('active');
    });
});

async function loadCategoryProducts(categoryId, categoryName) {
    const productsGrid = document.getElementById('productsGrid');
    const loader = document.getElementById('categoryLoader');
    const section = document.getElementById('categoryProducts');
    const header = document.querySelector('.category-products-section .modern-section-header h2');
    
    try {
        // Show section if hidden
        section.style.display = 'block';
        
        // Show loader with smooth transition
        productsGrid.style.opacity = '0.5';
        productsGrid.style.pointerEvents = 'none';
        loader.style.display = 'flex';
        loader.style.opacity = '1';
        loader.style.pointerEvents = 'auto';

        // Update header with category name
        header.innerHTML = `
            <span class="icon"><i class="fas fa-tag"></i></span>
            ${categoryName}
        `;

        // Fetch products
        const response = await fetch(`/get_products_by_category/${categoryId}`);
        const data = await response.json();
        
        // Render products with fade-in animation
        if (data.status === 'success' && data.products.length > 0) {
            productsGrid.innerHTML = data.products.map((product, index) => `
                <div class="product-card" style="animation-delay: ${index * 0.05}s">
                    <img src="${product.imageUrl || '../static/images/placeholder-product.png'}" 
                         alt="${product.name}" class="product-image">
                    <div class="product-info">
                        <h3 class="product-name">${product.name}</h3>
                        <p class="product-price">${product.price}</p>
                        <p class="product-rating">
                            <span class="stars">${'★'.repeat(Math.floor(product.rating || 0))}${'☆'.repeat(5 - Math.floor(product.rating || 0))}</span>
                            ${product.rating || 'N/A'}
                        </p>
                        <a href="/product_display?id=${product.id}" class="view-product-btn">
                            View Details <i class="fas fa-arrow-right"></i>
                        </a>
                    </div>
                </div>
            `).join('');
        } else {
            productsGrid.innerHTML = `
                <div class="no-products" style="grid-column: 1 / -1">
                    <i class="fas fa-box-open" style="font-size: 2rem; margin-bottom: 1rem;"></i>
                    <p>No products found in this category</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading category products:', error);
        productsGrid.innerHTML = `
            <div class="no-products" style="grid-column: 1 / -1">
                <i class="fas fa-exclamation-triangle" style="color: #ef4444; font-size: 2rem; margin-bottom: 1rem;"></i>
                <p>Error loading products. Please try again.</p>
                <button onclick="window.location.reload()" style="margin-top: 1rem; padding: 0.5rem 1rem; background: var(--primary); color: white; border: none; border-radius: 0.5rem; cursor: pointer;">
                    Refresh Page
                </button>
            </div>
        `;
    } finally {
        // Hide loader and restore grid
        setTimeout(() => {
            loader.style.display = 'none';
            productsGrid.style.opacity = '1';
            productsGrid.style.pointerEvents = 'auto';
            
            // Add animation to product cards
            document.querySelectorAll('.product-card').forEach(card => {
                card.style.animation = 'fadeInUp 0.5s ease-out forwards';
            });
        }, 300);
    }
}

