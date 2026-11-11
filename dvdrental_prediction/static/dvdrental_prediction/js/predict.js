document.addEventListener("DOMContentLoaded", function() {
    const statusBox = document.getElementById("statusBox");
    const predictionChart = document.getElementById("predictionChart");

    const inputData = {
        store_id: 1,
        active: 1,
        total_payment: 150,
        payment_count: 3,
        average_payment: 50,
    };

    fetch("/predict-customer/",{
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify(inputData),
    })
    .then(response => response.json())
    .then(data => {
        if (data.prediction !== undefined){
            statusBox.textContent = `Prediction: ${data.prediction}`;

            new Chart(predictionChart, {
                type: 'bar',
                data: {
                    labels: ['class 0', 'class 1'],
                    datasets: [{
                        label: 'Prediction Probability',
                        data: data.probability,
                    }]
                }
            });
        } else {
            statusBox.textContent = 'Error: Could not fetch prediction.';
        }
    })
    .catch(error => {
        statusBox.textContent = 'Error: ' + error.message;
    });
});

function getCSRFToken() {
    return document.cookie.split('; ')
        .find(row => row.startsWith('csrftoken'))
        ?.split('=')[1];
}