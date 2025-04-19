document.addEventListener("DOMContentLoaded", function () {
    const productDetailsDiv = document.getElementById("productDetails");
    const compareButton = document.getElementById("compareButton");
    const loader = document.getElementById("loader");
    const resultsDiv = document.getElementById("results");
    const comparisonTable = document.getElementById("comparisonTable");

    const compareModal = document.getElementById("compareModal");
    const similarProductsBtn = document.getElementById("similarProductsBtn");
    const pasteUrlBtn = document.getElementById("pasteUrlBtn");
    const urlInputContainer = document.getElementById("urlInputContainer");
    const productUrlInput = document.getElementById("productUrlInput");
    const submitUrlBtn = document.getElementById("submitUrlBtn");
    const urlError = document.getElementById("urlError");
    const closeModal = document.querySelector(".close");
    const comparisonContainer = document.createElement("div");
    comparisonContainer.className = "comparison-container";
    comparisonContainer.style.display = "none";
    document.querySelector("main").appendChild(comparisonContainer);

    // Replace the existing compareButton event listener with this:
    compareButton.addEventListener("click", function() {
        compareModal.style.display = "block";
    });

    // Close modal when clicking X
    closeModal.addEventListener("click", function() {
        compareModal.style.display = "none";
    });

    // Close modal when clicking outside
    window.addEventListener("click", function(event) {
        if (event.target === compareModal) {
            compareModal.style.display = "none";
        }
    });

    // Similar products button
    similarProductsBtn.addEventListener("click", function() {
        compareModal.style.display = "none";
        // Show loader
        loader.style.display = "block";
        
        // Existing comparison logic
        setTimeout(function() {
            fetch('/compare')
                .then(response => response.json())
                .then(data => {
                    loader.style.display = "none";
                    comparisonContainer.style.display = "none"; // Hide our custom container
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
                    loader.style.display = "none";
                });
        }, 1500);
    });

    // Paste URL button
    pasteUrlBtn.addEventListener("click", function() {
        urlInputContainer.style.display = "block";
    });

    // Submit URL for comparison
    submitUrlBtn.addEventListener("click", function() {
        const url = productUrlInput.value.trim();
        console.log("Submit URL button clicked with URL:", url);
        
        if (!url) {
            console.log("No URL entered");
            alert("Please enter a URL");
            return;
        }
        
        const flipkartPattern = /https?:\/\/(www\.)?flipkart\.com\/.*/;
        const amazonPattern = /https?:\/\/(www\.)?amazon\.in\/.*/;
        
        if (!flipkartPattern.test(url) && !amazonPattern.test(url)) {
            console.log("Invalid URL format:", url);
            alert("Please enter a valid Amazon or Flipkart product URL");
            return;
        }
        
        console.log("Valid URL, proceeding with comparison");
        compareModal.style.display = "none";
        loader.style.display = "block";
        
        const productId = new URLSearchParams(window.location.search).get('id');
        console.log("Current product ID:", productId);
        
        // First fetch current product
        fetch(`/get_product_details/${productId}`)
            .then(res => {
                console.log("Current product response status:", res.status);
                if (!res.ok) throw new Error("Failed to fetch current product");
                return res.json();
            })
            .then(currentProduct => {
                console.log("Successfully fetched current product:", currentProduct);
                
                // Then fetch comparison product
                return fetch('/compare_with_url', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: url })
                })
                .then(res => {
                    console.log("Comparison product response status:", res.status);
                    if (!res.ok) throw new Error("Failed to fetch comparison product");
                    return res.json();
                })
                .then(newProduct => {
                    console.log("Successfully fetched comparison product:", newProduct);
                    
                    loader.style.display = "none";
                    comparisonContainer.style.display = "flex";
                    resultsDiv.style.display = "none";
                    comparisonTable.style.display = "none";
                    
                    comparisonContainer.innerHTML = `
                        <!-- Your comparison HTML here -->
                    `;
                });
            })
            .catch(error => {
                console.error('Error:', error);
                loader.style.display = "none";
                alert('Error: ' + error.message);
            });
    });


    // Check if an ID is available (e.g., passed via query param or localStorage)
    const urlParams = new URLSearchParams(window.location.search);
    const productId = urlParams.get('id');
    if (productId) {
        fetch(`/get_product_details/${productId}`)
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    renderProduct(data.product);
                } else {
                    productDetailsDiv.innerHTML = `<p>Product not found.</p>`;
                }
            });
    } else {
        // Fallback: Simulate fetching product details (for demo)
        fetchProductDetails().then(renderProduct);
    }

    function renderProduct(product) {
        productDetailsDiv.innerHTML = `
            <div class="product-card">
                <img src="${product.imageUrl}" alt="${product.name}" class="product-image">
                <h3 class="product-name">${product.name}</h3>
                <p class="product-price"><strong>Price:</strong> ${product.price}</p>
                <p class="product-rating"><strong>Rating:</strong> ${product.rating}</p>
                ${renderStars(product.rating)}
            </div>
        `;
        document.getElementById('buyNowBtn').onclick = function() {
            window.open(product.buy_link, '_blank');
        };
    }

    function renderStars(rating) {
        const maxStars = 5;
        let html = '';
        for (let i = 1; i <= maxStars; i++) {
            html += `<span class="star${i <= Math.round(rating) ? '' : ' empty'}">&#9733;</span>`;
        }
        return `<div class="star-rating">${html}</div>`;
    }

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

});

// ----------------- PRICE HISTORY GRAPH -------------------
// Fetch graph data from JSON
        fetch('graph_data.json')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(graphData => {
                // Show lowest and average price on the page
                document.getElementById("lowest-price").textContent = `Lowest Price: ₹${graphData.lowest_price.toLocaleString('en-IN')}`;
                document.getElementById("average-price").textContent = `Average Price: ₹${graphData.average_price.toLocaleString('en-IN')}`;

                // Parse SVG path data to extract coordinates
                function parsePathData(pathData) {
                    const commands = pathData.split(/\s+/);
                    const points = [];
                    let i = 0;

                    while (i < commands.length) {
                        const cmd = commands[i];
                        if (cmd === 'M' || cmd === 'C') {
                            i++;
                            while (i < commands.length && !isNaN(parseFloat(commands[i]))) {
                                const x = parseFloat(commands[i]);
                                i++;
                                const y = parseFloat(commands[i]);
                                i++;
                                points.push({ x, y });
                            }
                        } else {
                            i++;
                        }
                    }
                    return points;
                }

                // Convert SVG Y-coordinates to prices with proper scaling
                function svgYToPrice(y) {
                    // Get min and max prices from the y_axis_labels
                    const minPrice = parseFloat(graphData.y_axis_labels[0].replace('₹', '').replace(',', ''));
                    const maxPrice = parseFloat(graphData.y_axis_labels[graphData.y_axis_labels.length - 1].replace('₹', '').replace(',', ''));
                    
                    // SVG coordinate range (from the path data)
                    const svgMinY = 0;
                    const svgMaxY = 150; // Approximate max from the path data
                    
                    // Calculate price based on SVG y position (inverted because SVG y increases downward)
                    const price = maxPrice - ((y - svgMinY) / (svgMaxY - svgMinY)) * (maxPrice - minPrice);
                    return Math.max(minPrice, Math.min(maxPrice, price)); // Clamp to min/max
                }

                // Generate dates for X-axis (4 months period ending today)
                function generateDates(count) {
                    const endDate = new Date(); // Today's date
                    const startDate = new Date(endDate);
                    startDate.setMonth(endDate.getMonth() - 4); // Go back 4 months
                    
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

                const points = parsePathData(graphData.path_data);
                
                // Generate dates for 4 months period
                const dates = generateDates(points.length);

                // Build chart series data
                const seriesData = points.map((point, i) => {
                    const price = svgYToPrice(point.y);
                    return {
                        x: dates[i].getTime(),
                        y: price,
                        price: `₹${price.toLocaleString('en-IN', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`
                    };
                });

                // Get min and max prices from y_axis_labels
                const minPrice = parseFloat(graphData.y_axis_labels[0].replace('₹', '').replace(',', ''));
                const maxPrice = parseFloat(graphData.y_axis_labels[graphData.y_axis_labels.length - 1].replace('₹', '').replace(',', ''));

                // Calculate tick interval
                const priceRange = maxPrice - minPrice;
                const tickInterval = priceRange <= 20000 ? 5000 : 
                                   priceRange <= 50000 ? 10000 : 
                                   20000;

                // Render Highcharts
                Highcharts.chart('chart-container', {
                    chart: {
                        type: 'areaspline',
                        backgroundColor: 'transparent'
                    },
                    title: {
                        text: graphData.title || '4-Month Price History',
                        style: {
                            color: '#333',
                            fontSize: '1.2em',
                            fontWeight: 'bold'
                        }
                    },
                    subtitle: {
                        text: graphData.subtitle || `Price trend from ${dates[0].toLocaleDateString()} to ${dates[dates.length-1].toLocaleDateString()}`,
                        style: {
                            color: '#666',
                            fontSize: '0.8em'
                        }
                    },
                    xAxis: {
                        type: 'datetime',
                        title: {
                            text: 'Date'
                        },
                        labels: {
                            format: '{value:%b %d}',
                            rotation: -45
                        },
                        gridLineWidth: 1,
                        gridLineColor: '#e6e6e6',
                        min: dates[0].getTime(),
                        max: dates[dates.length-1].getTime()
                    },
                    yAxis: {
                        title: {
                            text: 'Price (₹)'
                        },
                        labels: {
                            formatter: function() {
                                return `₹${this.value.toLocaleString('en-IN')}`;
                            }
                        },
                        min: minPrice,
                        max: maxPrice,
                        tickInterval: tickInterval,
                        gridLineWidth: 1,
                        gridLineColor: '#e6e6e6'
                    },
                    tooltip: {
                        formatter: function() {
                            return `<b>${Highcharts.dateFormat('%A %b %d, %Y', this.x)}</b><br/>Price: ${this.point.price}`;
                        }
                    },
                    plotOptions: {
                        areaspline: {
                            fillOpacity: 0.2,
                            marker: {
                                enabled: true,
                                radius: 3,
                                states: {
                                    hover: {
                                        radius: 5
                                    }
                                }
                            },
                            lineWidth: 3,
                            states: {
                                hover: {
                                    lineWidth: 4
                                }
                            }
                        }
                    },
                    series: [{
                        name: 'Price',
                        data: seriesData,
                        color: '#1e88e5',
                        fillColor: {
                            linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
                            stops: [
                                [0, 'rgba(30, 136, 229, 0.3)'],
                                [1, 'rgba(30, 136, 229, 0.05)']
                            ]
                        }
                    }],
                    annotations: [{
                        labels: [{
                            point: {
                                x: dates[0].getTime(),
                                y: graphData.lowest_price,
                                xAxis: 0,
                                yAxis: 0
                            },
                            text: `Lowest: ₹${graphData.lowest_price.toLocaleString('en-IN')}`,
                            backgroundColor: 'rgba(255, 255, 255, 0.9)',
                            borderColor: '#d32f2f',
                            borderRadius: 4,
                            style: {
                                color: '#d32f2f',
                                fontWeight: 'bold'
                            },
                            padding: 8
                        }, {
                            point: {
                                x: dates[Math.floor(dates.length / 2)].getTime(),
                                y: graphData.average_price,
                                xAxis: 0,
                                yAxis: 0
                            },
                            text: `Avg: ₹${graphData.average_price.toLocaleString('en-IN')}`,
                            backgroundColor: 'rgba(255, 255, 255, 0.9)',
                            borderColor: '#1976d2',
                            borderRadius: 4,
                            style: {
                                color: '#1976d2',
                                fontWeight: 'bold'
                            },
                            padding: 8
                        }]
                    }],
                    credits: {
                        enabled: false
                    },
                    responsive: {
                        rules: [{
                            condition: {
                                maxWidth: 600
                            },
                            chartOptions: {
                                xAxis: {
                                    labels: {
                                        rotation: -30
                                    }
                                },
                                annotations: {
                                    labels: [{
                                        style: {
                                            fontSize: '10px'
                                        }
                                    }]
                                }
                            }
                        }]
                    }
                });
            })
            .catch(error => {
                console.error('Error fetching graph data:', error);
                alert('Failed to load graph data. Please try again later.');
            });
// ----------------- END OF PRICE HISTORY GRAPH -------------------

// ----------------- PRICE ALERT FUNCTIONALITY -------------------

document.getElementById("setPriceAlertBtn").addEventListener("click", function () {
    const price = document.getElementById("alertPrice").value;
    const email = document.getElementById("alertEmail").value;
    const productId = new URLSearchParams(window.location.search).get('id');

    // Email validation regex
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (!price || !email || !productId) {
        alert("Please fill all fields correctly.");
        return;
    }
    
    if (!emailRegex.test(email)) {
        alert("Please enter a valid email address");
        return;
    }

    fetch('/set_price_alert', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId, desired_price: price, email: email })
    })
    .then(res => res.json())
    .then(data => {
        const msg = document.getElementById("alertMsg");
        if (data.status === "success") {
            msg.textContent = "✅ Price alert set successfully!";
        } else {
            msg.textContent = "❌ Failed to set alert. Try again.";
        }
    })
    .catch(err => {
        console.error(err);
        alert("An error occurred while setting alert.");
    });
});