const products = [
    { id: 1, name: 'iPhone 13', price: '₹79,900', features: ['128GB Storage', 'A15 Bionic Chip'], website: 'Amazon' },
    { id: 2, name: 'Samsung Galaxy S21', price: '₹69,999', features: ['128GB Storage', 'Exynos 2100'], website: 'Flipkart' },
    { id: 3, name: 'OnePlus 9 Pro', price: '₹64,999', features: ['256GB Storage', 'Snapdragon 888'], website: 'Snapdeal' },
    { id: 4, name: 'Sony WH-1000XM4', price: '₹29,990', features: ['Noise Cancelling', '30 Hours Battery'], website: 'Amazon' },
    { id: 5, name: 'Dell XPS 13', price: '₹1,49,999', features: ['11th Gen Intel i7', '16GB RAM'], website: 'Croma' }
];

function searchProducts() {
    const searchInput = document.getElementById('searchInput').value.toLowerCase();
    const filteredProducts = products.filter(product => 
        product.name.toLowerCase().includes(searchInput) || 
        product.features.some(feature => feature.toLowerCase().includes(searchInput))
    );
    displayProducts(filteredProducts);
}

function displayProducts(products) {
    const productList = document.getElementById('productList');
    productList.innerHTML = '';
    products.forEach(product => {
        const productElement = document.createElement('div');
        productElement.className = 'product';
        productElement.innerHTML = `
            <h3>${product.name}</h3>
            <p class="price">${product.price}</p>
            <p>Features: ${product.features.join(', ')}</p>
            <p>Website: ${product.website}</p>
        `;
        productList.appendChild(productElement);
    });
}
