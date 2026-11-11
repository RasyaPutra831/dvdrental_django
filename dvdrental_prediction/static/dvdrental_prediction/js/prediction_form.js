document.getElementById('predictionForm').addEventListener('submit', function(e) {
    e.preventDefault();

    const data = {
        store_id: parseInt(document.getElementById('id_store_id').value),
        active: parseInt(document.getElementById('id_active').value),
        total_payment: parseFloat(document.getElementById('id_total_payment').value),
        payment_count: parseInt(document.getElementById('id_payment_count').value),
        average_payment: parseFloat(document.getElementById('id_average_payment').value)
    }
    fetch('/predict-customer/',{
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        console.log("Prediction Result:", result);
        document.getElementById('statusBox').innerText =
            `Prediction: ${result.prediction}, Probabilities: ${result.probability.map(p => p.toFixed(2)).join(', ')}`;
        updateChart(result.probability);
    })
    .catch(err =>{
        console.error('Prediction error:', err);
        document.getElementById('statusBox').innerText = 'Error making prediction';
    })
});

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// chart.js
let probabilityChart = null;
function updateChart(probabilities) {
    const ctx = document.getElementById('predictionChart').getContext('2d');
    console.log("Canvas Context:", ctx);
    const labels = probabilities.map((_, index) => `Class ${index}`);
    const data = {
        labels: labels,
        datasets: [{
            label: 'Probability',
            data: probabilities,
            backgroundColor: ['rgba(54, 162, 235, 0.7)', 'rgba(255, 99, 132, 0.7)'],
            borderColor: ['rgba(54, 162, 235, 1)', 'rgba(255, 99, 132, 1)'],
            borderWidth: 1
        }]
    };
    const config = {
        type: 'bar',
        data: data,
        option: {
            scales: {
                y: { beginAtZero: true, max: 1 }
            }
        }
    };

    if (probabilityChart) {
        predictionChart.data = data;
        predictionChart.update();
    } else {
        predictionChart = new Chart(ctx, config);
    }
}