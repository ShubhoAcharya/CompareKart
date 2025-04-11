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

    var compareButton = document.getElementById("product");
    compareButton.addEventListener("click", function() {
        var loader = document.getElementById("loader");
        var resultsDiv = document.getElementById("results");
        var comparisonTable = document.getElementById("comparisonTable");

        // Show loader and hide results and comparison table
        loader.style.display = "block";
        resultsDiv.style.display = "none";
        comparisonTable.style.display = "none";

        setTimeout(function() {
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


var urlButton = document.getElementById("urlButton");
    urlButton.addEventListener("click", function() {
        var productURL = document.getElementById("productURL").value;
        fetch('/save_url', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: productURL }),
        })
        .then(response => {
            if (response.ok) {
                console.log("URL saved successfully");
                fetch('/check_url', {
                    method: 'POST',
                })
                .then(response => {
                    if (response.ok) {
                        console.log("URL checked successfully");
                    } else {
                        console.error('Error checking URL');
                    }
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
            } else {
                console.error('Error saving URL');
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });