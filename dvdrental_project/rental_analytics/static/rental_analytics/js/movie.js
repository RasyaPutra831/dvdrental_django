let lastPrediction = null;
let chartInstance = null;
let currentMode = 'existing';
let historyData = [];

// Elements (loaded after DOM)
let search, suggestions, category, revenue, length, rating, predict_month, searchWrapper, modeToggle;

function initElements() {
    search = document.getElementById('search');
    suggestions = document.getElementById('suggestions');
    category = document.getElementById('category');
    revenue = document.getElementById('revenue');
    length = document.getElementById('length');
    rating = document.getElementById('rating');
    predict_month = document.getElementById('predict_month');
    searchWrapper = document.getElementById('searchWrapper');
    modeToggle = document.querySelector('.mode-toggle');
    
    if (!search) console.error('JS: Elements not found - wrong template?');
}

/* Toggle Mode */
function toggleMode(mode) {
    currentMode = mode;
    if (modeToggle) modeToggle.setAttribute('data-mode', mode);
    
    // Update buttons
    document.querySelectorAll('.mode-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    // Toggle fields
    const fields = [category, revenue, length, rating];
    fields.forEach(field => {
        if (!field) return;
        if (mode === 'existing') {
            field.setAttribute('readonly', true);
            field.classList.add('readonly-field');
            field.placeholder = '';
        } else {
            field.removeAttribute('readonly');
            field.classList.remove('readonly-field');
            if (field === revenue) field.placeholder = 'e.g. 1500000';
            else if (field === length) field.placeholder = 'e.g. 120';
            else if (field === rating) field.placeholder = 'e.g. PG-13';
        }
    });
    
    // Search behavior
    if (search) {
        if (mode === 'existing') {
            search.placeholder = 'Type movie title...';
        } else {
            search.value = '';
            search.placeholder = 'Enter new movie title';
            if (suggestions) suggestions.style.display = 'none';
        }
    }
    
    // Clear new mode
    if (mode === 'new') {
        [category, revenue, length, rating].forEach(f => f && (f.value = ''));
    }
}

/* Search Autocomplete (existing mode only) */
function initSearch() {
    if (!search) return;
    
    search.addEventListener('input', async () => {
        if (currentMode !== 'existing') return;
        
        const value = search.value.trim();
        if (!value) {
            if (suggestions) suggestions.style.display = 'none';
            return;
        }

        try {
            const res = await fetch(`/analytics/search-movie/?q=${value}`);
            const data = await res.json();

            if (suggestions) {
                suggestions.innerHTML = data.length === 0 
                    ? "<div>No results found</div>" 
                    : '';
                    
                data.forEach(item => {
                    const div = document.createElement('div');
                    div.innerText = item;
                    div.onclick = () => selectMovie(item);
                    suggestions.appendChild(div);
                });
                suggestions.style.display = 'block';
            }
        } catch (e) {
            console.error('Search error:', e);
        }
    });
}

async function selectMovie(title) {
    if (currentMode !== 'existing' || !search) return;
    
    search.value = title;
    if (suggestions) suggestions.style.display = 'none';

    try {
        const res = await fetch(`/analytics/get-movie-detail/?title=${encodeURIComponent(title)}`);
        const data = await res.json();

        if (data.error) {
            alert('Movie not found!');
            return;
        }
        
        if (category) category.value = data.category || '';
        if (revenue) revenue.value = data.total_revenue ? '$' + parseFloat(data.total_revenue).toLocaleString() : '';
        if (length) length.value = data.film_length || '';
        if (rating) rating.value = data.rating || '';
    } catch (e) {
        console.error('Detail error:', e);
    }
}

/* Predict (both modes) */
async function predict() {
    if (!category || !revenue || !length || !rating || !predict_month) {
        alert('Fields not loaded!');
        return;
    }
    
    const rawRevenue = revenue.value.replace(/[$\,]/g, '');
    
    if (!category.value.trim() || isNaN(parseFloat(rawRevenue)) || 
        !length.value.trim() || !rating.value.trim() || 
        isNaN(parseInt(predict_month.value))) {
        alert('Isi semua field dengan benar!');
        return;
    }
    
    const data = {
        category: category.value.trim(),
        total_revenue: parseFloat(rawRevenue),
        film_length: parseInt(length.value),
        rating: rating.value.trim(),
        predict_month: parseInt(predict_month.value),
        title: search ? (search.value.trim() || 'New Movie') : 'New Movie'
    };

    console.log('Predict:', data, 'Mode:', currentMode);

    try {
        const res = await fetch('/analytics/predict-movie/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        const result = await res.json();
        lastPrediction = result;

        showResult(result);
    } catch (e) {
        console.error('Predict error:', e);
        alert('Prediksi gagal!');
    }
}

function showResult(result) {
    const isPopular = result.label === "Popular";
    const popularPercent = result.prediction === 1 ? result.confidence : 1 - result.confidence;
    const notPopularPercent = 1 - popularPercent;

    if (document.getElementById('result')) {
        document.getElementById('result').innerHTML = `
            <div class="result-text ${isPopular ? 'popular-text' : 'not-popular-text'}">
                ${result.label}
            </div>
        `;
    }

    // Chart
    const canvas = document.getElementById('resultChart');
    if (chartInstance) chartInstance.destroy();
    if (canvas) {
        chartInstance = new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels: ['Popular', 'Not Popular'],
                datasets: [{ data: [popularPercent, notPopularPercent], backgroundColor: ['green', 'red'] }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: { legend: { position: 'bottom' } }
            }
        });
    }

    if (document.getElementById('chartInfo')) {
        document.getElementById('chartInfo').innerHTML = `
            <div class="green">Popular: ${(popularPercent*100).toFixed(2)}%</div>
            <div class="red">Not Popular: ${(notPopularPercent*100).toFixed(2)}%</div>
        `;
    }

    const saveBtn = document.getElementById('saveBtn');
    if (saveBtn) saveBtn.style.display = 'block';
}

/* Save */
async function savePrediction() {
    if (!lastPrediction) return alert('No prediction!');
    
    try {
        await fetch('/analytics/save-movie/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(lastPrediction)
        });
        alert('Saved!');
        loadHistory();
    } catch (e) {
        alert('Error Saved!');
    }
}

/* History (unchanged logic) */
async function loadHistory(filter = '') {
    try {
        const res = await fetch(`/analytics/get-history/?result=${filter}`);
        historyData = await res.json();
        renderHistory();
    } catch (e) {
        console.error('History error:', e);
    }
}

function renderHistory() {
    const tbody = document.querySelector('#historyTable tbody');
    const countEl = document.getElementById('historyCount');
    
    if (!tbody) return;
    
    if (historyData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; color:#999;">No history yet.</td></tr>';
        if (countEl) countEl.textContent = '(0)';
        return;
    }

    tbody.innerHTML = historyData.map(item => `
        <tr>
            <td><input type="checkbox" class="history-checkbox" value="${item.id}"></td>
            <td>${item.input_data.title || 'N/A'}</td>
            <td>${item.input_data.category || 'N/A'}</td>
            <td>$${parseFloat(item.input_data.total_revenue || 0).toLocaleString()}</td>
            <td>${item.input_data.film_length || 'N/A'}</td>
            <td>${item.input_data.rating || 'N/A'}</td>
            <td>${item.input_data.predict_month || 'N/A'} months</td>
            <td><span class="${item.prediction === 'Popular' ? 'popular-text' : 'not-popular-text'}">${item.prediction}</span></td>
        </tr>
    `).join('');

    if (countEl) countEl.textContent = `(${historyData.length})`;
}

function toggleSelectAll() {
    const selectAll = document.getElementById('selectAll');
    const checkboxes = document.querySelectorAll('.history-checkbox');
    checkboxes.forEach(cb => cb.checked = !!selectAll?.checked);
}

async function deleteSelected() {
    const checkboxes = document.querySelectorAll('.history-checkbox:checked');
    const ids = Array.from(checkboxes).map(cb => parseInt(cb.value));
    
    if (ids.length === 0) return alert('Pilih item!');
    if (!confirm(`Delete ${ids.length} item?`)) return;

    try {
        await fetch('/analytics/delete-movie-selected/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ids})
        });
        loadHistory(document.getElementById('historyFilter')?.value || '');
    } catch (e) {
        alert('Error!');
    }
}

async function clearAllHistory() {
    if (!confirm('Delete All?')) return;
    try {
        await fetch('/analytics/clear-movies/', {method: 'POST'});
        loadHistory();
    } catch (e) {
        alert('Error!');
    }
}

// Event listeners
function initEvents() {
    const filterSelect = document.getElementById('historyFilter');
    if (filterSelect) {
        filterSelect.addEventListener('change', (e) => loadHistory(e.target.value));
    }
    
    // Button onclicks if not inline
    const predictBtn = document.querySelector('.predict-btn');
    if (predictBtn) predictBtn.onclick = predict;
    
    const saveBtn = document.getElementById('saveBtn');
    if (saveBtn) saveBtn.onclick = savePrediction;
    
    const delBtn = document.querySelector('button[onclick="deleteSelected()"]');
    if (delBtn) delBtn.onclick = deleteSelected;
    
    const clearBtn = document.querySelector('button[onclick="clearAllHistory()"]');
    if (clearBtn) clearBtn.onclick = clearAllHistory;
}

// INIT
document.addEventListener('DOMContentLoaded', () => {
    initElements();
    initSearch();
    initEvents();
    if (modeToggle) toggleMode('existing'); // Default
    loadHistory();
});

