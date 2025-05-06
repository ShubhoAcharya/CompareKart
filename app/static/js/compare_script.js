document.addEventListener("DOMContentLoaded", function() {
    // Set current year
    document.getElementById('currentYear').textContent = new Date().getFullYear();
    
    // Initialize variables
    const comparisonId = document.getElementById('comparisonGrid')?.getAttribute('data-comparison-id');
    const comparisonGrid = document.getElementById('comparisonGrid');
    const addMoreBtn = document.getElementById('addMoreBtn');
    const addMoreContainer = document.getElementById('addMoreContainer');
    const newProductUrl = document.getElementById('newProductUrl');
    const submitNewProduct = document.getElementById('submitNewProduct');
    const addMoreError = document.getElementById('addMoreError');
    const highlightDifferencesBtn = document.getElementById('highlightDifferences');
    const exportComparisonBtn = document.getElementById('exportComparison');
    const shareComparisonBtn = document.getElementById('shareComparison');
    const searchButton = document.getElementById('searchButton');
    const searchQuery = document.getElementById('searchQuery');
    const searchResults = document.getElementById('searchResults');
    
    // Highlight best value product
    function highlightBestValue() {
        // Remove any existing best value highlights
        document.querySelectorAll('.best-value').forEach(el => {
            el.classList.remove('best-value');
        });
        
        // Find the product with lowest price
        let lowestPrice = Infinity;
        let bestValueProduct = null;
        
        document.querySelectorAll('.comparison-card').forEach(card => {
            const priceStr = card.querySelector('.price-cell').textContent.replace(/[^0-9.]/g, '');
            const price = parseFloat(priceStr);
            
            if (price < lowestPrice) {
                lowestPrice = price;
                bestValueProduct = card;
            }
        });
        
        // Add best value class to the card
        if (bestValueProduct) {
            bestValueProduct.classList.add('best-value');
        }
    }
    
    // Highlight differences between products
    function highlightDifferences() {
        const cards = document.querySelectorAll('.comparison-card');
        if (!cards.length) return;
        
        cards.forEach(card => card.classList.toggle('highlight-differences'));
        
        // Update button text
        const isHighlighted = cards[0].classList.contains('highlight-differences');
        highlightDifferencesBtn.innerHTML = isHighlighted ? 
            '<i class="fas fa-highlighter"></i> Remove Highlights' : 
            '<i class="fas fa-highlighter"></i> Highlight Differences';
        
        // Highlight lowest and highest prices
        if (isHighlighted) {
            let prices = [];
            document.querySelectorAll('.price-cell').forEach(cell => {
                const priceStr = cell.textContent.replace(/[^0-9.]/g, '');
                const price = parseFloat(priceStr);
                prices.push({price, cell});
            });
            
            if (prices.length > 0) {
                prices.sort((a, b) => a.price - b.price);
                
                // Reset all highlights first
                prices.forEach(item => {
                    item.cell.classList.remove('lowest', 'highest');
                });
                
                // Highlight lowest price
                prices[0].cell.classList.add('lowest');
                
                // Highlight highest price (if more than one product)
                if (prices.length > 1) {
                    prices[prices.length - 1].cell.classList.add('highest');
                }
            }
        } else {
            // Remove all highlights when toggled off
            document.querySelectorAll('.price-cell').forEach(cell => {
                cell.classList.remove('lowest', 'highest');
            });
        }
    }
    
    // Remove product function
    function removeProduct(comparisonId, productId) {
        if (!confirm("Are you sure you want to remove this product from comparison?")) {
            return;
        }
        
        const card = document.querySelector(`.comparison-card[data-product-id="${productId}"]`);
        if (!card) return;
        
        const originalContent = card.innerHTML;
        card.innerHTML = '<div class="spinner">Removing...</div>';
        
        fetch('/update_comparison', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                comparison_id: comparisonId,
                product_id: productId,
                new_url: null // Indicates removal
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === "success") {
                // Instead of reloading, remove the card from DOM
                card.remove();
                
                // Update the UI
                const remainingCards = document.querySelectorAll('.comparison-card');
                if (remainingCards.length === 0) {
                    showEmptyState();
                } else {
                    highlightBestValue();
                }
                
                showToast("Product removed successfully");
            } else {
                card.innerHTML = originalContent;
                showToast(data.message || "Failed to remove product", "error");
            }
        })
        .catch(error => {
            card.innerHTML = originalContent;
            showToast("Error removing product", "error");
            console.error("Error:", error);
        });
    }
    
    function showEmptyState() {
        comparisonGrid.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-balance-scale-left"></i>
                <h3>No Products to Compare</h3>
                <p>Add products to start comparing features and prices</p>
                <button id="addMoreBtn" class="add-more-btn">
                    <i class="fas fa-plus"></i> Add Products
                </button>
            </div>
        `;
        
        // Re-attach event listener to the new button
        document.getElementById('addMoreBtn').addEventListener('click', toggleAddMoreContainer);
    }
    
    // Export comparison as CSV
    function exportComparison() {
        if (!comparisonId) {
            showToast("No comparison to export", "error");
            return;
        }
        window.open(`/export_comparison?id=${comparisonId}`, '_blank');
    }
    
    // Share comparison link
    function shareComparison() {
        if (!comparisonId) {
            showToast("No comparison to share", "error");
            return;
        }
        
        const url = window.location.href;
        
        if (navigator.share) {
            navigator.share({
                title: 'Product Comparison - CompareKart',
                text: 'Check out this product comparison I created on CompareKart',
                url: url
            })
            .catch(err => {
                copyToClipboard(url);
            });
        } else {
            copyToClipboard(url);
        }
    }
    
    // Helper function to copy to clipboard
    function copyToClipboard(text) {
        navigator.clipboard.writeText(text).then(() => {
            showToast('Comparison link copied to clipboard!');
        }).catch(() => {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            showToast('Comparison link copied to clipboard!');
        });
    }
    
    // Search functionality
    function handleSearch() {
        const query = searchQuery.value.trim();
        if (!query) {
            showSearchError("Please enter a search term");
            return;
        }

        searchResults.innerHTML = '<div class="spinner"></div>';
        searchResults.style.display = 'block';
        
        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                window.location.href = data.redirect;
            } else {
                showSearchError(data.message || "No matching products found");
            }
        })
        .catch(error => {
            showSearchError("Error occurred during search");
        });
    }

    function showSearchError(message) {
        searchResults.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-circle"></i>
                <p>${message}</p>
            </div>
        `;
    }
    
    // Add new product to comparison
    function addNewProduct() {
        const newUrl = newProductUrl.value.trim();
        const currentCount = document.querySelectorAll('.comparison-card').length;
        
        addMoreError.textContent = '';
        
        if (currentCount >= 4) {
            addMoreError.textContent = "Maximum of 4 products allowed";
            return;
        }
        
        if (!newUrl.match(/https?:\/\/(www\.)?(flipkart\.com|amazon\.in)\/.*/)) {
            addMoreError.textContent = "Please enter a valid Amazon or Flipkart product URL";
            return;
        }
        
        // Show loading state
        const originalContent = addMoreContainer.innerHTML;
        addMoreContainer.innerHTML = '<div class="spinner"></div>';
        
        fetch('/update_comparison', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                comparison_id: comparisonId,
                product_id: 0, // Indicates to add rather than replace
                new_url: newUrl
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                window.location.reload();
            } else {
                addMoreContainer.innerHTML = originalContent;
                addMoreError.textContent = data.message || "Failed to add product";
            }
        })
        .catch(error => {
            addMoreContainer.innerHTML = originalContent;
            addMoreError.textContent = "Error adding product";
            console.error("Error:", error);
        });
    }
    
    // Toggle add more container
    function toggleAddMoreContainer() {
        const currentCount = document.querySelectorAll('.comparison-card').length;
        if (currentCount >= 4) {
            showToast("Maximum of 4 products allowed", "error");
            return;
        }
        addMoreContainer.style.display = addMoreContainer.style.display === 'block' ? 'none' : 'block';
    }
    
    // Show toast notification
    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast-notification ${type}`;
        toast.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);
        
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 3000);
    }
    
    // Event listeners
    if (addMoreBtn) {
        addMoreBtn.addEventListener('click', toggleAddMoreContainer);
    }
    
    if (submitNewProduct) {
        submitNewProduct.addEventListener('click', addNewProduct);
    }
    
    if (highlightDifferencesBtn) {
        highlightDifferencesBtn.addEventListener('click', highlightDifferences);
    }
    
    if (exportComparisonBtn) {
        exportComparisonBtn.addEventListener('click', exportComparison);
    }
    
    if (shareComparisonBtn) {
        shareComparisonBtn.addEventListener('click', shareComparison);
    }
    
    if (searchButton) {
        searchButton.addEventListener('click', handleSearch);
    }
    
    if (searchQuery) {
        searchQuery.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') handleSearch();
        });
    }
    
    // Close search results when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.search-container') && !e.target.closest('.search-results')) {
            searchResults.style.display = 'none';
        }
    });
    
    // Initialize page
    highlightBestValue();
    
    // Scroll to top functionality
    const scrollToTopBtn = document.getElementById('scrollToTop');
    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            scrollToTopBtn.classList.add('show');
        } else {
            scrollToTopBtn.classList.remove('show');
        }
    });
    
    scrollToTopBtn.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    
    // Make functions available globally for inline event handlers
    window.removeProduct = removeProduct;
});

// Toast notification styles
const toastStyle = document.createElement('style');
toastStyle.textContent = `
.toast-notification {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    background: #4f46e5;
    color: white;
    padding: 12px 24px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    gap: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 1000;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.toast-notification.show {
    opacity: 1;
}

.toast-notification.error {
    background: #ef4444;
}

.toast-notification i {
    font-size: 1.2rem;
}
`;
document.head.appendChild(toastStyle);