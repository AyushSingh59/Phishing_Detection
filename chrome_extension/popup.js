const statusEl = document.getElementById('status');
const scanBtn = document.getElementById('scanBtn');

scanBtn.addEventListener('click', async () => {
    statusEl.textContent = 'Scanning active page...';
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab || !tab.url) {
        statusEl.textContent = 'Unable to read current tab URL.';
        return;
    }

    try {
        const response = await fetch('http://localhost:5000/api/scan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: tab.url }),
        });
        const data = await response.json();
        if (data.error) {
            statusEl.textContent = `Error: ${data.error}`;
            return;
        }
        if (data.risk_score >= 75) {
            statusEl.textContent = `Dangerous: ${data.result} (${data.risk_score}%)`;
            alert('Warning: this page appears dangerous.');
        } else if (data.risk_score >= 40) {
            statusEl.textContent = `Suspicious: ${data.result} (${data.risk_score}%)`;
        } else {
            statusEl.textContent = `Safe: ${data.result} (${data.risk_score}%)`;
        }
    } catch (error) {
        statusEl.textContent = 'Scan failed. Make sure the backend is running on localhost:5000.';
    }
});
