document.getElementById('screeningForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = {
        age: document.getElementById('age').value,
        gender: document.getElementById('gender').value,
        history: document.getElementById('history').value,
        smoking: document.getElementById('smoking').value,
        symptoms: document.getElementById('symptoms').value
    };

    // UI Updates
    document.getElementById('screeningForm').classList.add('hidden');
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('errorMsg').classList.add('hidden');

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const result = await response.json();

        if (response.ok) {
            displayResult(result);
        } else {
            throw new Error(result.error || 'Prediction failed');
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('errorMsg').classList.remove('hidden');
        document.getElementById('screeningForm').classList.remove('hidden');
    }
});

function displayResult(result) {
    document.getElementById('loading').classList.add('hidden');
    const resultCard = document.getElementById('resultCard');
    const riskBadge = document.getElementById('riskBadge');
    
    resultCard.classList.remove('hidden');
    
    // Set Risk Level and Styling
    riskBadge.innerText = result.risk_level;
    riskBadge.className = 'badge ' + result.risk_level.toLowerCase();
    
    // Update Content
    document.getElementById('probabilityText').innerText = result.probability;
    document.getElementById('explanationText').innerText = result.explanation;
    
    // Smooth scroll to result
    resultCard.scrollIntoView({ behavior: 'smooth' });
}

function resetForm() {
    document.getElementById('resultCard').classList.add('hidden');
    document.getElementById('screeningForm').classList.remove('hidden');
    document.getElementById('screeningForm').reset();
}
