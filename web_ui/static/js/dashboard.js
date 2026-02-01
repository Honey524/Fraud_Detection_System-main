// Dashboard State
let stats = {
    totalTransactions: 0,
    fraudCount: 0,
    normalCount: 0
};

let fraudTrend = {
    labels: [],
    data: []
};

let chart = null;

// Initialize Dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initialized');
    
    // Check service health
    checkServices();
    setInterval(checkServices, 5000);
    
    // Load recent alerts
    loadRecentAlerts();
    setInterval(loadRecentAlerts, 10000);
    
    // Initialize chart
    initChart();
    
    // Setup test form
    document.getElementById('test-form').addEventListener('submit', testTransaction);
});

// Check Service Health
async function checkServices() {
    try {
        const mlResponse = await fetch('http://localhost:5002/health');
        const mlStatus = document.getElementById('ml-status');
        if (mlResponse.ok) {
            mlStatus.className = 'badge bg-success me-2';
            mlStatus.textContent = 'ML Service: ●';
        } else {
            mlStatus.className = 'badge bg-danger me-2';
            mlStatus.textContent = 'ML Service: ●';
        }
    } catch (error) {
        document.getElementById('ml-status').className = 'badge bg-danger me-2';
    }
    
    try {
        const alertResponse = await fetch('http://localhost:5001/health');
        const alertStatus = document.getElementById('alert-status');
        if (alertResponse.ok) {
            alertStatus.className = 'badge bg-success';
            alertStatus.textContent = 'Alert Service: ●';
        } else {
            alertStatus.className = 'badge bg-danger';
            alertStatus.textContent = 'Alert Service: ●';
        }
    } catch (error) {
        document.getElementById('alert-status').className = 'badge bg-danger';
    }
}

// Test Transaction
async function testTransaction(event) {
    event.preventDefault();
    
    const amount = parseFloat(document.getElementById('amount').value);
    const hour = parseInt(document.getElementById('hour').value);
    const type = document.getElementById('type').value;
    const day = parseInt(document.getElementById('day').value);
    
    const transaction = {
        transaction_id: 'TEST_' + Date.now(),
        amount: amount,
        amount_log: Math.log1p(amount),
        hour: hour,
        day_of_week: day,
        is_weekend: day >= 5 ? 1 : 0,
        is_night: (hour >= 22 || hour <= 6) ? 1 : 0,
        transaction_type: type,
        latitude: 40.7128,
        longitude: -74.0060
    };
    
    try {
        const response = await fetch('http://localhost:5002/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(transaction)
        });
        
        const result = await response.json();
        
        // Display result
        const resultDiv = document.getElementById('test-result');
        const isFraud = result.is_fraud;
        const riskClass = result.risk_level.toLowerCase();
        
        resultDiv.innerHTML = `
            <div class="alert alert-${isFraud ? 'danger' : 'success'}">
                <h6>${isFraud ? '🚨 FRAUD DETECTED' : '✅ NORMAL TRANSACTION'}</h6>
                <p class="mb-1"><strong>Fraud Probability:</strong> ${(result.fraud_probability * 100).toFixed(2)}%</p>
                <p class="mb-0"><strong>Risk Level:</strong> <span class="risk-badge risk-${riskClass}">${result.risk_level}</span></p>
            </div>
        `;
        
        // Add to stream
        addTransactionToStream(transaction, result);
        
        // Update stats
        updateStats(result.is_fraud);
        
    } catch (error) {
        document.getElementById('test-result').innerHTML = `
            <div class="alert alert-danger">
                Error: ${error.message}
            </div>
        `;
    }
}

// Add Transaction to Stream
function addTransactionToStream(transaction, result) {
    const streamDiv = document.getElementById('transaction-stream');
    
    // Remove "waiting" message if present
    if (streamDiv.querySelector('.text-muted')) {
        streamDiv.innerHTML = '';
    }
    
    const isFraud = result.is_fraud;
    const transactionItem = document.createElement('div');
    transactionItem.className = `transaction-item ${isFraud ? 'fraud' : 'normal'}`;
    
    transactionItem.innerHTML = `
        <div class="d-flex justify-content-between align-items-center">
            <div>
                <strong>${transaction.transaction_id}</strong><br>
                <small>Amount: $${transaction.amount.toFixed(2)} | Type: ${transaction.transaction_type}</small>
            </div>
            <div class="text-end">
                <div class="risk-badge risk-${result.risk_level.toLowerCase()}">
                    ${result.risk_level}
                </div>
                <small class="d-block mt-1">${(result.fraud_probability * 100).toFixed(1)}%</small>
            </div>
        </div>
    `;
    
    streamDiv.insertBefore(transactionItem, streamDiv.firstChild);
    
    // Keep only last 10 transactions
    while (streamDiv.children.length > 10) {
        streamDiv.removeChild(streamDiv.lastChild);
    }
}

// Update Statistics
function updateStats(isFraud) {
    stats.totalTransactions++;
    if (isFraud) {
        stats.fraudCount++;
    } else {
        stats.normalCount++;
    }
    
    document.getElementById('total-transactions').textContent = stats.totalTransactions;
    document.getElementById('fraud-count').textContent = stats.fraudCount;
    document.getElementById('normal-count').textContent = stats.normalCount;
    
    const fraudRate = stats.totalTransactions > 0 
        ? ((stats.fraudCount / stats.totalTransactions) * 100).toFixed(1) 
        : 0;
    document.getElementById('fraud-rate').textContent = fraudRate + '%';
    
    // Update chart
    updateChart(isFraud);
}

// Initialize Chart
function initChart() {
    const ctx = document.getElementById('fraudChart').getContext('2d');
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: fraudTrend.labels,
            datasets: [{
                label: 'Fraud Rate (%)',
                data: fraudTrend.data,
                borderColor: 'rgb(220, 53, 69)',
                backgroundColor: 'rgba(220, 53, 69, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: function(value) {
                            return value + '%';
                        }
                    }
                }
            }
        }
    });
}

// Update Chart
function updateChart(isFraud) {
    const now = new Date().toLocaleTimeString();
    fraudTrend.labels.push(now);
    
    const currentRate = stats.totalTransactions > 0 
        ? ((stats.fraudCount / stats.totalTransactions) * 100).toFixed(1)
        : 0;
    fraudTrend.data.push(parseFloat(currentRate));
    
    // Keep only last 20 data points
    if (fraudTrend.labels.length > 20) {
        fraudTrend.labels.shift();
        fraudTrend.data.shift();
    }
    
    chart.update();
}

// Load Recent Alerts
async function loadRecentAlerts() {
    try {
        const response = await fetch('http://localhost:5001/alerts/recent?limit=5');
        const alerts = await response.json();
        
        const alertsDiv = document.getElementById('recent-alerts');
        
        if (alerts.length === 0) {
            alertsDiv.innerHTML = '<p class="text-muted text-center">No alerts yet</p>';
            return;
        }
        
        alertsDiv.innerHTML = alerts.map(alert => `
            <div class="alert-item">
                <strong>${alert.transaction_id}</strong><br>
                <small>Amount: $${alert.amount.toFixed(2)}</small><br>
                <small>Risk: ${alert.risk_level} (${(alert.fraud_probability * 100).toFixed(1)}%)</small>
            </div>
        `).join('');
        
    } catch (error) {
        console.error('Error loading alerts:', error);
    }
}
