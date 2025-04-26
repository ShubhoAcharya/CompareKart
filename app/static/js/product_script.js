document.addEventListener("DOMContentLoaded", function () {
    // DOM Elements - Updated to include search elements
    const elements = {
        productDetails: document.getElementById("productDetails"),
        productLoader: document.getElementById("productLoader"),
        graphLoader: document.getElementById("graphLoader"),
        chartContainer: document.getElementById("chart-container"),
        priceAlertBtn: document.getElementById("setPriceAlertButton"),
        alertMsg: document.getElementById("priceAlertMessage"),
        emailLoader: document.getElementById("emailLoader"),
        buyNowBtn: document.getElementById("buyNowBtn"),
        compareButton: document.getElementById("compareButton"),
        scrollToTop: document.getElementById("scrollToTop"),
        compareModal: document.getElementById("compareModal"),
        similarProductsBtn: document.getElementById("similarProductsBtn"),
        pasteUrlBtn: document.getElementById("pasteUrlBtn"),
        urlInputContainer: document.getElementById("urlInputContainer"),
        productUrlInput: document.getElementById("productUrlInput"),
        submitUrlBtn: document.getElementById("submitUrlBtn"),
        urlError: document.getElementById("urlError"),
        closeModal: document.querySelector(".close"),
        searchButton: document.getElementById("searchButton"),
        searchQueryInput: document.getElementById("searchQuery"),
        searchResults: document.getElementById("results"),
        loader: document.getElementById("loader"),
        comparisonContainer: (() => {
            const container = document.createElement("div");
            container.className = "comparison-container";
            container.style.display = "none";
            document.querySelector("main").appendChild(container);
            return container;
        })()
    };

    // Get product ID from URL
    const productId = new URLSearchParams(window.location.search).get('id');
    
    if (productId) {
        loadProductDetails(productId);
    } else {
        showProductError("No product ID found in URL");
    }

    // Search functionality
    function handleSearch() {
        const searchQuery = elements.searchQueryInput.value.trim();
        if (!searchQuery) {
            showSearchError("Please enter a search term");
            return;
        }

        showLoading(elements.loader, "Searching products...");
        
        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: searchQuery }),
        })
        .then(response => response.json())
        .then(data => {
            hideLoading(elements.loader);
            if (data.status === 'success') {
                // Redirect to product display page with the found product
                window.location.href = data.redirect;
            } else if (data.status === 'not_found') {
                showSearchError(data.message || "No matching products found");
            } else {
                throw new Error(data.message || 'Search failed');
            }
        })
        .catch((error) => {
            hideLoading(elements.loader);
            console.error('Error:', error);
            showSearchError(error.message || "Error occurred during search");
        });
    }

    function showSearchError(message) {
        elements.searchResults.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-circle"></i>
                <p>${message}</p>
            </div>
        `;
        elements.searchResults.style.display = 'block';
    }

    // Event listeners for search
    elements.searchButton.addEventListener("click", handleSearch);
    elements.searchQueryInput.addEventListener("keypress", function(event) {
        if (event.key === "Enter") {
            handleSearch();
        }
    });

    // Close search results when clicking outside
    document.addEventListener('click', function(event) {
        if (!event.target.closest('.search-container') && 
            !event.target.closest('#results')) {
            elements.searchResults.style.display = 'none';
        }
    });

    // Main product loading function
    async function loadProductDetails(productId) {
        try {
            showLoading(elements.productLoader, "Loading product details...");
            
            const response = await fetch(`/get_product_details/${productId}`);
            const data = await response.json();
            
            if (data.status === "success") {
                renderProduct(data.product);
                if (data.modified_url) {
                    loadGraphData(productId, data.modified_url);
                }
            } else {
                showProductError("Product not found");
            }
        } catch (error) {
            console.error('Error loading product:', error);
            showProductError("Error loading product details");
        } finally {
            hideLoading(elements.productLoader);
        }
    }

    // Graph data loading
    async function loadGraphData(productId, modifiedUrl) {
        try {
            showLoading(elements.graphLoader, "Loading price history...");
            
            const response = await fetch(`/get_graph_data?product_id=${productId}&modified_url=${encodeURIComponent(modifiedUrl)}`);
            const data = await response.json();
            
            if (data.status === "success") {
                renderGraph(data.graph_data);
            } else {
                showGraphError("Failed to load price history", productId, modifiedUrl);
            }
        } catch (error) {
            console.error('Error loading graph:', error);
            showGraphError("Error loading price history", productId, modifiedUrl);
        }
    }

    // UI Helper Functions
    function showLoading(element, message = "") {
        element.style.display = 'flex';
        element.innerHTML = `
            <div class="spinner"></div>
            ${message ? `<p>${message}</p>` : ''}
        `;
    }

    function hideLoading(element) {
        element.style.display = 'none';
    }

    function showError(element, message) {
        element.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${message}</p>
            </div>
        `;
    }

    function showProductError(message) {
        showError(elements.productDetails, message);
    }

    function showGraphError(message, productId, modifiedUrl) {
        elements.graphLoader.innerHTML = `
            <div class="graph-error">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${message}</p>
                <button id="retryGraphBtn" class="btn-retry">Try Again</button>
            </div>
        `;
        
        document.getElementById('retryGraphBtn').onclick = () => {
            loadGraphData(productId, modifiedUrl);
        };
    }

    // Product Rendering
    function renderProduct(product) {
        elements.productDetails.innerHTML = `
            <div class="product-card">
                <img src="${product.imageUrl}" alt="${product.name}" class="product-image">
                <h3 class="product-name">${product.name}</h3>
                <p class="product-price"><strong>Price:</strong> ${product.price}</p>
                <p class="product-rating"><strong>Rating:</strong> ${product.rating}</p>
                ${renderStars(product.rating)}
            </div>
        `;
        
        elements.buyNowBtn.onclick = () => window.open(product.buy_link, '_blank');
    }

    function renderStars(rating) {
        const maxStars = 5;
        let html = '';
        const numericRating = parseFloat(rating) || 0;
        
        for (let i = 1; i <= maxStars; i++) {
            html += `<span class="star${i <= Math.round(numericRating) ? '' : ' empty'}">&#9733;</span>`;
        }
        return `<div class="star-rating">${html}</div>`;
    }

    // Graph Rendering
    function renderGraph(graphData) {
        hideLoading(elements.graphLoader);
        
        // Update price summary
        document.getElementById("lowest-price").textContent = `Lowest Price: ₹${graphData.lowest_price.toLocaleString('en-IN')}`;
        document.getElementById("average-price").textContent = `Average Price: ₹${graphData.average_price.toLocaleString('en-IN')}`;

        // Process graph data
        const points = parsePathData(graphData.path_data);
        const dates = generateDates(points.length);
        const seriesData = points.map((point, i) => ({
            x: dates[i].getTime(),
            y: svgYToPrice(point.y, graphData),
            price: `₹${svgYToPrice(point.y, graphData).toLocaleString('en-IN')}`
        }));

        // Create chart
        Highcharts.chart('chart-container', {
            chart: { type: 'areaspline', backgroundColor: 'transparent' },
            title: { text: graphData.title || 'Price History' },
            subtitle: { text: graphData.subtitle || 'Historical price trends' },
            xAxis: {
                type: 'datetime',
                labels: { format: '{value:%b %d}' }
            },
            yAxis: {
                title: { text: 'Price (₹)' },
                labels: { formatter: function() { return `₹${this.value.toLocaleString('en-IN')}`; } }
            },
            tooltip: {
                formatter: function() {
                    return `<b>${Highcharts.dateFormat('%b %d, %Y', this.x)}</b><br/>Price: ${this.point.price}`;
                }
            },
            series: [{
                name: 'Price',
                data: seriesData,
                color: '#4f46e5'
            }],
            credits: { enabled: false }
        });
    }

    // Graph Data Processing Helpers
    function parsePathData(pathData) {
        const commands = pathData.split(/\s+/);
        const points = [];
        let i = 0;

        while (i < commands.length) {
            const cmd = commands[i];
            if (cmd === 'M' || cmd === 'C') {
                i++;
                while (i < commands.length && !isNaN(parseFloat(commands[i]))) {
                    points.push({
                        x: parseFloat(commands[i++]),
                        y: parseFloat(commands[i++])
                    });
                }
            } else {
                i++;
            }
        }
        return points;
    }

    function svgYToPrice(y, graphData) {
        const minPrice = parseFloat(graphData.y_axis_labels[0].replace('₹', '').replace(',', ''));
        const maxPrice = parseFloat(graphData.y_axis_labels[graphData.y_axis_labels.length - 1].replace('₹', '').replace(',', ''));
        const svgMinY = 0;
        const svgMaxY = 150;
        const price = maxPrice - ((y - svgMinY) / (svgMaxY - svgMinY)) * (maxPrice - minPrice);
        return Math.max(minPrice, Math.min(maxPrice, price));
    }

    function generateDates(count) {
        const endDate = new Date();
        const startDate = new Date(endDate);
        startDate.setMonth(endDate.getMonth() - 4);
        
        const dates = [];
        const timeDiff = endDate.getTime() - startDate.getTime();
        const dayDiff = timeDiff / (1000 * 3600 * 24);
        const interval = dayDiff / (count - 1);
        
        for (let i = 0; i < count; i++) {
            const date = new Date(startDate);
            date.setDate(startDate.getDate() + (i * interval));
            dates.push(date);
        }
        
        return dates;
    }

    // Price Alert Functionality - Consolidated Version
    elements.priceAlertBtn.addEventListener("click", async function() {
        const price = document.getElementById("alertPrice").value;
        const email = document.getElementById("alertEmail").value;
        const msg = document.getElementById("alertMsg");
        const emailLoader = document.getElementById("emailLoader");
    
        // Clear previous messages and styles
        msg.textContent = "";
        msg.className = "alert-message";
        
        // Validate inputs
        if (!price || !email || !productId) {
            showAlertMessage("Please fill all fields", "error");
            return;
        }
    
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            showAlertMessage("Please enter a valid email", "error");
            return;
        }
    
        try {
            // Show loading state
            emailLoader.style.display = "block";
            elements.priceAlertBtn.disabled = true;
            
            const response = await fetch('/set_price_alert', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    product_id: productId, 
                    desired_price: parseFloat(price), 
                    email: email 
                })
            });
            
            const data = await response.json();
            
            if (data.status === "success") {
                if (data.warning) {
                    showAlertMessage(`Alert #${data.alert_id} set successfully! (Email notification failed)`, "warning");
                } else {
                    showAlertMessage(`Price alert #${data.alert_id} set successfully! You'll be notified when the price drops.`, "success");
                    // Clear the form on success
                    document.getElementById("alertPrice").value = "";
                    document.getElementById("alertEmail").value = "";
                }
            } else {
                showAlertMessage(data.message || "Failed to set alert. Please try again.", "error");
            }
        } catch (error) {
            console.error('Error setting alert:', error);
            showAlertMessage("Network error. Please try again.", "error");
        } finally {
            // Reset loading state
            emailLoader.style.display = "none";
            elements.priceAlertBtn.disabled = false;
        }
    });

    function showAlertMessage(message, type) {
        const msg = document.getElementById("alertMsg");
        msg.textContent = message;
        msg.className = `alert-message ${type}`;
        
        // Auto-hide success messages after 5 seconds
        if (type === "success") {
            setTimeout(() => {
                msg.textContent = "";
                msg.className = "alert-message";
            }, 5000);
        }
    }

    // Comparison Functionality
    elements.compareButton.addEventListener("click", function() {
        elements.compareModal.style.display = "block";
    });

    elements.closeModal.addEventListener("click", function() {
        elements.compareModal.style.display = "none";
    });

    window.addEventListener("click", function(event) {
        if (event.target === elements.compareModal) {
            elements.compareModal.style.display = "none";
        }
    });

    elements.similarProductsBtn.addEventListener("click", function() {
        elements.compareModal.style.display = "none";
        showLoading(loader);
        
        fetch('/compare')
            .then(response => response.json())
            .then(data => {
                hideLoading(loader);
                renderComparisonResults(data);
            })
            .catch((error) => {
                console.error('Error:', error);
                hideLoading(loader);
            });
    });

    elements.pasteUrlBtn.addEventListener("click", function() {
        elements.urlInputContainer.style.display = "block";
    });

    elements.submitUrlBtn.addEventListener("click", function() {
        const url = elements.productUrlInput.value.trim();
        elements.urlError.textContent = "";
        
        if (!url) {
            elements.urlError.textContent = "Please enter a URL";
            return;
        }

        if (!/https?:\/\/(www\.)?(flipkart\.com|amazon\.in)\/.*/.test(url)) {
            elements.urlError.textContent = "Please enter a valid Amazon or Flipkart product URL";
            return;
        }

        elements.compareModal.style.display = "none";
        showLoading(loader);

        fetch(`/get_product_details/${productId}`)
            .then(res => res.json())
            .then(currentProductData => {
                if (currentProductData.status !== "success") throw new Error("Current product not found");

                return fetch('/compare_with_url', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                });
            })
            .then(res => res.json())
            .then(compareProductData => {
                hideLoading(loader);
                if (compareProductData.status !== "success") {
                    throw new Error(compareProductData.message || "Failed to fetch comparison product");
                }
                renderUrlComparison(currentProductData.product, compareProductData.product);
            })
            .catch(error => {
                hideLoading(loader);
                elements.urlError.textContent = error.message || "Error occurred during comparison.";
            });
    });

    function renderComparisonResults(data) {
        elements.comparisonContainer.style.display = "none";
        elements.comparisonTable.style.display = "block";
        elements.comparisonTable.innerHTML = generateTable(data);
        
        elements.resultsDiv.innerHTML = `
            <div class="link-container">
                <a href="${data.product_urls.amazon_link}" class="styled-link amazon-link" target="_blank">
                    <i class="fas fa-shopping-cart"></i> Amazon: Go to Amazon
                </a>
                <a href="${data.product_urls.flipkart_link}" class="styled-link flipkart-link" target="_blank">
                    <i class="fas fa-shopping-cart"></i> Flipkart: Go to Flipkart
                </a>
            </div>
        `;
    }

    function renderUrlComparison(currentProduct, compareProduct) {
        elements.comparisonContainer.style.display = "flex";
        elements.comparisonContainer.innerHTML = `
            <div class="comparison-table-wrapper">
                <div class="comparison-card">
                    <h3>Current Product</h3>
                    ${renderProductTable(currentProduct)}
                </div>
                <div class="comparison-card">
                    <h3>Comparison Product</h3>
                    ${renderProductTable(compareProduct)}
                </div>
            </div>
        `;
    }

    function renderProductTable(product) {
        if (!product) return `<p>No data found.</p>`;
        return `
            <div class="product-image-container">
                <img src="${product.imageUrl || product['Image URL'] || ''}" 
                     alt="Product Image" class="product-table-image">
            </div>
            <table class="product-comparison-table">
                <tr><td><strong>Name</strong></td><td>${product.name || product['Product Name'] || ''}</td></tr>
                <tr><td><strong>Price</strong></td><td>${product.price || product['Price'] || ''}</td></tr>
                <tr><td><strong>Rating</strong></td><td>${product.rating || product['Rating'] || ''}</td></tr>
                <tr><td><strong>Buy Link</strong></td><td><a href="${product.buy_link || '#'}" target="_blank">Buy Now</a></td></tr>
            </table>
        `;
    }

    // Scroll to top functionality
    window.addEventListener("scroll", function() {
        elements.scrollToTop.classList.toggle("show", window.scrollY > 300);
    });
    elements.scrollToTop.addEventListener("click", function() {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });
});

// Fallback function for demo purposes
function fetchProductDetails() {
    return new Promise(resolve => {
        setTimeout(() => {
            resolve({
                name: "Demo Product",
                price: "₹1,999",
                rating: "4.2",
                imageUrl: "https://via.placeholder.com/300",
                buy_link: "#"
            });
        }, 1000);
    });
}

// Helper function for comparison table (if needed elsewhere)
function generateTable(data) {
    // Implementation would go here
    return '';
}