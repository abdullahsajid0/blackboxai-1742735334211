// Main Application Logic

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeApp);

async function initializeApp() {
    try {
        // Load initial dashboard data
        await loadDashboardData();
        
        // Set up event listeners
        setupEventListeners();
        
        // Load settings
        await loadSettings();
    } catch (error) {
        handleApiError(error);
    }
}

function setupEventListeners() {
    // Search inputs
    document.querySelectorAll('[data-search]').forEach(input => {
        input.addEventListener('input', debounce(handleSearch, 300));
    });

    // Filter dropdowns
    document.querySelectorAll('[data-filter]').forEach(select => {
        select.addEventListener('change', handleFilter);
    });
}

// Search Handler
async function handleSearch(event) {
    const searchType = event.target.dataset.search;
    const searchTerm = event.target.value;

    try {
        switch (searchType) {
            case 'products':
                const products = await api.getProducts(searchTerm);
                updateProductsTable(products);
                break;
            case 'customers':
                const customers = await api.getCustomers(searchTerm);
                updateCustomersTable(customers);
                break;
            case 'installments':
                const installments = await api.getInstallments('', searchTerm);
                updateInstallmentsTable(installments);
                break;
        }
    } catch (error) {
        handleApiError(error);
    }
}

// Filter Handler
async function handleFilter(event) {
    const filterType = event.target.dataset.filter;
    const filterValue = event.target.value;

    try {
        switch (filterType) {
            case 'installments':
                const installments = await api.getInstallments(filterValue);
                updateInstallmentsTable(installments);
                break;
        }
    } catch (error) {
        handleApiError(error);
    }
}

// Cash Sale Handler
async function handleCashSale(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    try {
        const saleData = {
            customerName: formData.get('customerName'),
            contactNumber: formData.get('contactNumber'),
            address: formData.get('address'),
            productId: formData.get('product'),
            quantity: parseInt(formData.get('quantity')),
            amount: parseFloat(formData.get('amount'))
        };

        const result = await api.createCashSale(saleData);
        showSuccess('Sale completed successfully');
        showReceiptModal(result.id, 'cash');
        form.reset();
        loadDashboardData();
    } catch (error) {
        handleApiError(error);
    }
}

// Installment Sale Handler
async function handleInstallmentSale(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    try {
        const saleData = {
            customerName: formData.get('customerName'),
            contactNumber: formData.get('contactNumber'),
            cnic: formData.get('cnic'),
            address: formData.get('address'),
            witnessName: formData.get('witnessName'),
            witnessCnic: formData.get('witnessCnic'),
            witnessAddress: formData.get('witnessAddress'),
            productId: formData.get('product'),
            markupPercentage: parseFloat(formData.get('markupPercentage')),
            installmentCount: parseInt(formData.get('installmentCount')),
            advancePayment: parseFloat(formData.get('advancePayment'))
        };

        const result = await api.createInstallmentSale(saleData);
        showSuccess('Installment sale completed successfully');
        showReceiptModal(result.id, 'installment');
        form.reset();
        loadDashboardData();
    } catch (error) {
        handleApiError(error);
    }
}

// Receipt Modal
async function showReceiptModal(saleId, type) {
    try {
        const sale = type === 'cash' 
            ? await api.getCashSale(saleId)
            : await api.getInstallmentSale(saleId);
        
        const settings = await api.getSettings();
        
        const modalContent = generateReceiptHtml(sale, settings);
        const modal = document.getElementById('receiptModal');
        modal.innerHTML = modalContent;
        showModal('receiptModal');
    } catch (error) {
        handleApiError(error);
    }
}

// Generate Receipt HTML
function generateReceiptHtml(sale, settings) {
    return `
        <div class="relative top-20 mx-auto p-5 border w-[800px] shadow-lg rounded-md bg-white">
            <div class="text-center mb-8">
                <h2 class="text-2xl font-bold">${settings.businessName}</h2>
                <p class="text-gray-600">${settings.businessAddress}</p>
                <p class="text-gray-600">Phone: ${settings.businessPhone}</p>
            </div>
            
            <div class="mb-8">
                <div class="flex justify-between mb-4">
                    <div>
                        <p class="font-medium">Receipt No: ${sale.id}</p>
                        <p>Date: ${formatDate(sale.date)}</p>
                    </div>
                    <div>
                        <p class="font-medium">Customer Details:</p>
                        <p>${sale.customerName}</p>
                        <p>${sale.contactNumber}</p>
                    </div>
                </div>
                
                <table class="w-full mb-4">
                    <thead>
                        <tr class="border-b">
                            <th class="text-left py-2">Product</th>
                            <th class="text-right py-2">Price</th>
                            <th class="text-right py-2">Quantity</th>
                            <th class="text-right py-2">Total</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="py-2">${sale.productDetails.name}</td>
                            <td class="text-right">${formatCurrency(sale.productDetails.price)}</td>
                            <td class="text-right">${sale.quantity}</td>
                            <td class="text-right">${formatCurrency(sale.amount)}</td>
                        </tr>
                    </tbody>
                </table>
                
                ${sale.type === 'installment' ? generateInstallmentScheduleHtml(sale) : ''}
            </div>
            
            <div class="flex justify-end space-x-4">
                <button onclick="hideModal('receiptModal')"
                        class="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300">
                    Close
                </button>
                <button onclick="printReceipt()"
                        class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
                    Print
                </button>
            </div>
        </div>
    `;
}

// Generate Installment Schedule HTML
function generateInstallmentScheduleHtml(sale) {
    return `
        <div class="mt-8">
            <h3 class="font-medium mb-4">Installment Schedule</h3>
            <table class="w-full">
                <thead>
                    <tr class="border-b">
                        <th class="text-left py-2">No.</th>
                        <th class="text-left py-2">Due Date</th>
                        <th class="text-right py-2">Amount</th>
                        <th class="text-right py-2">Balance</th>
                    </tr>
                </thead>
                <tbody>
                    ${sale.installments.map(inst => `
                        <tr class="border-b">
                            <td class="py-2">${inst.installmentNumber}</td>
                            <td>${formatDate(inst.dueDate)}</td>
                            <td class="text-right">${formatCurrency(inst.amount)}</td>
                            <td class="text-right">${formatCurrency(inst.remainingBalance)}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;
}

// Print Receipt
function printReceipt() {
    const receiptContent = document.getElementById('receiptModal').innerHTML;
    const printWindow = window.open('', '', 'height=600,width=800');
    printWindow.document.write(`
        <html>
            <head>
                <title>Print Receipt</title>
                <link href="https://cdn.tailwindcss.com" rel="stylesheet">
            </head>
            <body class="p-8">
                ${receiptContent}
                <script>
                    window.onload = function() {
                        window.print();
                        window.close();
                    }
                </script>
            </body>
        </html>
    `);
}

// Utility Functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions that need to be globally available
window.handleCashSale = handleCashSale;
window.handleInstallmentSale = handleInstallmentSale;
window.showReceiptModal = showReceiptModal;
window.printReceipt = printReceipt;