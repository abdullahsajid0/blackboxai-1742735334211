// Utility Functions

// Format currency in Pakistani Rupees
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-PK', {
        style: 'currency',
        currency: 'PKR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

// Format date
function formatDate(date) {
    return new Date(date).toLocaleDateString('en-PK', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Show error message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded shadow-lg';
    errorDiv.textContent = message;
    document.body.appendChild(errorDiv);
    setTimeout(() => errorDiv.remove(), 3000);
}

// Show success message
function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded shadow-lg';
    successDiv.textContent = message;
    document.body.appendChild(successDiv);
    setTimeout(() => successDiv.remove(), 3000);
}

// Calculate installment plan
function calculateInstallments(totalAmount, advancePayment, numberOfInstallments, markupPercentage) {
    const markupAmount = (totalAmount * markupPercentage) / 100;
    const totalWithMarkup = totalAmount + markupAmount;
    const remainingAmount = totalWithMarkup - advancePayment;
    const installmentAmount = Math.ceil(remainingAmount / numberOfInstallments);

    const installments = [];
    let remainingBalance = remainingAmount;
    const today = new Date();

    // First installment is the advance payment
    installments.push({
        installmentNumber: 1,
        dueDate: today.toISOString().split('T')[0],
        amount: advancePayment,
        status: 'Paid',
        remainingBalance: remainingBalance
    });

    // Calculate remaining installments
    for (let i = 0; i < numberOfInstallments; i++) {
        const dueDate = new Date(today);
        dueDate.setMonth(dueDate.getMonth() + i + 1);
        
        remainingBalance -= installmentAmount;
        if (remainingBalance < 0) remainingBalance = 0;

        installments.push({
            installmentNumber: i + 2,
            dueDate: dueDate.toISOString().split('T')[0],
            amount: installmentAmount,
            status: 'Pending',
            remainingBalance: remainingBalance
        });
    }

    return {
        totalWithMarkup,
        markupAmount,
        installmentAmount,
        installments
    };
}

// Validate required fields
function validateRequiredFields(data, requiredFields) {
    const missingFields = [];
    for (const field of requiredFields) {
        if (!data[field] || !String(data[field]).trim()) {
            missingFields.push(field.replace(/([A-Z])/g, ' $1').trim());
        }
    }
    return missingFields;
}

// Generate unique ID
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

// Export utility functions
window.formatCurrency = formatCurrency;
window.formatDate = formatDate;
window.showError = showError;
window.showSuccess = showSuccess;
window.calculateInstallments = calculateInstallments;
window.validateRequiredFields = validateRequiredFields;
window.generateId = generateId;