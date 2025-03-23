// UI Components and Handlers

// Navigation
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
        section.style.display = 'none';
    });
    
    // Show selected section
    const selectedSection = document.getElementById(sectionId);
    if (selectedSection) {
        selectedSection.classList.add('active');
        selectedSection.style.display = 'block';
    }

    // Update navigation buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('border-blue-500');
        if (btn.getAttribute('onclick').includes(sectionId)) {
            btn.classList.add('border-blue-500');
        }
    });

    // Load section data
    loadSectionData(sectionId);
}

// Load section-specific data
async function loadSectionData(sectionId) {
    try {
        switch (sectionId) {
            case 'dashboard':
                await loadDashboardData();
                break;
            case 'inventory':
                await loadInventoryData();
                break;
            case 'customers':
                await loadCustomersData();
                break;
            case 'installments':
                await loadInstallmentsData();
                break;
            case 'reports':
                await loadReportsData();
                break;
        }
    } catch (error) {
        handleApiError(error);
    }
}

// Dashboard Data Loading
async function loadDashboardData() {
    try {
        const summary = await api.getSalesSummary();
        const installments = await api.getInstallments('pending');
        const products = await api.getProducts();

        // Update stats
        updateDashboardStats(summary, installments, products);

        // Update recent sales
        updateRecentSales(summary.recent_sales || []);

        // Update upcoming installments
        updateUpcomingInstallments(installments);
    } catch (error) {
        handleApiError(error);
    }
}

// Update Dashboard Statistics
function updateDashboardStats(summary, installments, products) {
    // Total Sales
    const totalSales = summary.cash_sales + summary.installment_sales;
    document.getElementById('totalSales').textContent = formatCurrency(totalSales);

    // Active Installments
    const activeInstallments = installments.filter(i => i.status === 'pending').length;
    document.getElementById('activeInstallments').textContent = activeInstallments;

    // Low Stock Items
    const lowStockItems = products.filter(p => p.stock <= 5).length;
    document.getElementById('lowStockItems').textContent = lowStockItems;
}

// Product Management
function showAddProductModal() {
    const modalHtml = `
        <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div class="mt-3">
                <h3 class="text-lg font-medium text-gray-900 mb-4">Add New Product</h3>
                <form id="addProductForm" class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Product Name</label>
                        <input type="text" name="name" required
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Brand</label>
                        <input type="text" name="brand" required
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Model</label>
                        <input type="text" name="model" required
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Category</label>
                        <select name="category" required
                                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                            <option value="electronics">Electronics</option>
                            <option value="appliances">Home Appliances</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Price</label>
                        <input type="number" name="price" required min="0" step="0.01"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Stock</label>
                        <input type="number" name="stock" required min="0"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500">
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Description</label>
                        <textarea name="description" rows="3"
                                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"></textarea>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Features (one per line)</label>
                        <textarea name="features" rows="3"
                                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"></textarea>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700">Tags (comma-separated)</label>
                        <input type="text" name="tags"
                               class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                               placeholder="e.g., AC, LED, Smart TV">
                    </div>
                    <div class="flex justify-end space-x-3">
                        <button type="button" onclick="hideModal('addProductModal')"
                                class="bg-gray-200 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-300">
                            Cancel
                        </button>
                        <button type="submit"
                                class="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600">
                            Add Product
                        </button>
                    </div>
                </form>
            </div>
        </div>
    `;

    const modal = document.getElementById('addProductModal');
    modal.innerHTML = modalHtml;
    modal.classList.remove('hidden');

    // Add form submit handler
    document.getElementById('addProductForm').addEventListener('submit', handleAddProduct);
}

// Handle Add Product Form Submission
async function handleAddProduct(e) {
    e.preventDefault();
    const form = e.target;
    const formData = new FormData(form);

    try {
        const productData = {
            name: formData.get('name'),
            brand: formData.get('brand'),
            model: formData.get('model'),
            category: formData.get('category'),
            price: parseFloat(formData.get('price')),
            stock: parseInt(formData.get('stock')),
            description: formData.get('description'),
            features: formData.get('features').split('\n').filter(f => f.trim()),
            tags: formData.get('tags').split(',').map(t => t.trim()).filter(t => t)
        };

        await api.addProduct(productData);
        hideModal('addProductModal');
        showSuccess('Product added successfully');
        loadInventoryData();
    } catch (error) {
        handleApiError(error);
    }
}

// Show/Hide Modal
function showModal(modalId) {
    document.getElementById(modalId).classList.remove('hidden');
}

function hideModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

// Show Messages
function showError(message) {
    showNotification(message, 'error');
}

function showSuccess(message) {
    showNotification(message, 'success');
}

function showNotification(message, type) {
    const notificationDiv = document.createElement('div');
    notificationDiv.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg ${
        type === 'error' ? 'bg-red-500' : 'bg-green-500'
    } text-white`;
    notificationDiv.textContent = message;

    document.body.appendChild(notificationDiv);
    setTimeout(() => notificationDiv.remove(), 3000);
}

// Format Helpers
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-PK', {
        style: 'currency',
        currency: 'PKR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function formatDate(date) {
    return new Date(date).toLocaleDateString('en-PK', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Export UI functions
window.showSection = showSection;
window.showModal = showModal;
window.hideModal = hideModal;
window.showAddProductModal = showAddProductModal;
window.showError = showError;
window.showSuccess = showSuccess;
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;