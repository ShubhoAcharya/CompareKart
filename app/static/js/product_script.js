document.addEventListener("DOMContentLoaded", function () {
    const productDetailsDiv = document.getElementById("productDetails");
    const compareButton = document.getElementById("compareButton");
    const loader = document.getElementById("loader");
    const resultsDiv = document.getElementById("results");
    const comparisonTable = document.getElementById("comparisonTable");

    // Simulate fetching product details (replace with actual API call if needed)
    function fetchProductDetails() {
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    name: "Sample Product",
                    price: "₹999",
                    description: "This is a sample product description.",
                    rating: "4.5/5",
                    availability: "In Stock",
                });
            }, 1000);
        });
    }

    // Load product details
    fetchProductDetails()
        .then((product) => {
            productDetailsDiv.innerHTML = `
                <div class="product-card">
                    <h3>${product.name}</h3>
                    <p><strong>Price:</strong> ${product.price}</p>
                    <p><strong>Description:</strong> ${product.description}</p>
                    <p><strong>Rating:</strong> ${product.rating}</p>
                    <p><strong>Availability:</strong> ${product.availability}</p>
                </div>
            `;
        })
        .catch((error) => {
            console.error("Error fetching product details:", error);
            productDetailsDiv.innerHTML = `<p>Failed to load product details. Please try again later.</p>`;
        });

    // Scroll to top functionality
    const scrollToTopButton = document.getElementById("scrollToTop");

    window.addEventListener("scroll", function () {
        if (window.scrollY > 300) {
            scrollToTopButton.classList.add("show");
        } else {
            scrollToTopButton.classList.remove("show");
        }
    });

    scrollToTopButton.addEventListener("click", function () {
        window.scrollTo({
            top: 0,
            behavior: "smooth",
        });
    });

    // Compare button functionality
    compareButton.addEventListener("click", function () {
        // Show loader and hide results and comparison table
        loader.style.display = "block";
        resultsDiv.style.display = "none";
        comparisonTable.style.display = "none";

        setTimeout(function () {
            fetch('/compare')
                .then(response => response.json())
                .then(data => {
                    // Hide loader and show results and comparison table
                    loader.style.display = "none";
                    resultsDiv.style.display = "block";
                    comparisonTable.style.display = "block";

                    comparisonTable.innerHTML = generateTable(data);

                    resultsDiv.innerHTML = `
                        <div class="link-container">
                            <a href="${data.product_urls.amazon_link}" class="styled-link amazon-link" target="_blank">
                                <i class="fas fa-shopping-cart"></i> Amazon: Go to Amazon
                            </a>
                            <a href="${data.product_urls.flipkart_link}" class="styled-link flipkart-link" target="_blank">
                                <i class="fas fa-shopping-cart"></i> Flipkart: Go to Flipkart
                            </a>
                        </div>
                    `;
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
        }, 1500);
    });

    function generateTable(data) {
        let table = '<table><thead><tr>';
        // Create table headers
        data.headers.forEach(header => {
            table += `<th>${header}</th>`;
        });
        table += '</tr></thead><tbody>';
        // Create table rows
        data.rows.forEach(row => {
            table += '<tr>';
            row.forEach(cell => {
                table += `<td>${cell}</td>`;
            });
            table += '</tr>';
        });
        table += '</tbody></table>';
        return table;
    }
});