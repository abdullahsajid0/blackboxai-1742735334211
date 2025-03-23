// API endpoint configuration
const API_BASE_URL = '/api';

// API Calls
const api = {
    // Products
    async getProducts(searchTerm = '') {
        const response = await fetch(`${API_BASE_URL}/products?search=${searchTerm}`);
        if (!response.ok) throw new Error('Failed to fetch products');
        return response.json();
    },

    async addProduct(productData) {
        const response = await fetch(`${API_BASE_URL}/products`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(productData)
        });
        if (!response.ok) throw new Error('Failed to add product');
        return response.json();
    },

    // Customers
    async getCustomers(searchTerm = '') {
        const response = await fetch(`${API_BASE_URL}/customers?search=${searchTerm}`);
        if (!response.ok) throw new Error('Failed to fetch customers');
        return response.json();
    },

    // Sales
    async createCashSale(saleData) {
        const response = await fetch(`${API_BASE_URL}/sales/cash`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(saleData)
        });
        if (!response.ok) throw new Error('Failed to create cash sale');
        return response.json();
    },

    async createInstallmentSale(saleData) {
        const response = await fetch(`${API_BASE_URL}/sales/installment`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(saleData)
        });
        if (!response.ok) throw new Error('Failed to create installment sale');
        return response.json();
    },

    // Installments
    async getInstallments(status = '', searchTerm = '') {
        const response = await fetch(
            `${API_BASE_URL}/installments?status=${status}&search=${searchTerm}`
        );
        if (!response.ok) throw new Error('Failed to fetch installments');
        return response.json();
    },

    async markInstallmentPaid(saleId, installmentNumber) {
        const response = await fetch(
            `${API_BASE_URL}/installments/${saleId}/${installmentNumber}/pay`,
            { method: 'POST' }
        );
        if (!response.ok) throw new Error('Failed to mark installment as paid');
        return response.json();
    },

    // Reports
    async getSalesSummary(startDate = '', endDate = '') {
        const response = await fetch(
            `${API_BASE_URL}/reports/summary?start_date=${startDate}&end_date=${endDate}`
        );
        if (!response.ok) throw new Error('Failed to fetch sales summary');
        return response.json();
    },

    // Settings
    async getSettings() {
        const response = await fetch(`${API_BASE_URL}/settings`);
        if (!response.ok) throw new Error('Failed to fetch settings');
        return response.json();
    },

    async updateSettings(settingsData) {
        const response = await fetch(`${API_BASE_URL}/settings`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settingsData)
        });
        if (!response.ok) throw new Error('Failed to update settings');
        return response.json();
    }
};

// Error Handler
const handleApiError = (error) => {
    console.error('API Error:', error);
    showError(error.message || 'An error occurred while processing your request');
};

// Export API
window.api = api;
window.handleApiError = handleApiError;