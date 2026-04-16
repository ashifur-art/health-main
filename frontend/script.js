// API Configuration
const API_URL = 'http://localhost:8000';

// DOM Elements
const bmiCard = document.getElementById('bmiCard');
const bmiValue = document.getElementById('bmiValue');
const bmiCategory = document.getElementById('bmiCategory');
const formContainer = document.getElementById('formContainer');
const resultContainer = document.getElementById('resultContainer');
const loadingSpinner = document.getElementById('loadingSpinner');
const predictionForm = document.getElementById('predictionForm');
const recommendationsDiv = document.getElementById('recommendations');

// BMI Calculation Function
function calculateBMI() {
    const height = parseFloat(document.getElementById('height_cm').value);
    const weight = parseFloat(document.getElementById('weight_kg').value);
    
    if (height > 0 && weight > 0) {
        const heightM = height / 100;
        const bmi = weight / (heightM * heightM);
        const roundedBMI = bmi.toFixed(1);
        
        // Update BMI display
        if (bmiValue) bmiValue.textContent = roundedBMI;
        if (bmiCard) bmiCard.style.display = 'block';
        
        // Determine BMI category and color
        let category = '';
        let color = '';
        
        if (bmi < 18.5) {
            category = 'Underweight';
            color = '#3498db';
        } else if (bmi < 25) {
            category = 'Normal weight';
            color = '#2ecc71';
        } else if (bmi < 30) {
            category = 'Overweight';
            color = '#f39c12';
        } else {
            category = 'Obese';
            color = '#e74c3c';
        }
        
        if (bmiCategory) {
            bmiCategory.textContent = category;
            bmiCategory.style.color = color;
        }
        
        // Highlight the appropriate scale marker
        highlightBMIScale(bmi);
    } else {
        if (bmiCard) bmiCard.style.display = 'none';
    }
}

// Highlight BMI scale based on value
function highlightBMIScale(bmi) {
    const markers = document.querySelectorAll('.scale-marker');
    if (markers.length > 0) {
        markers.forEach(marker => {
            marker.style.opacity = '0.5';
            marker.style.transform = 'none';
        });
        
        if (bmi < 18.5 && markers[0]) {
            markers[0].style.opacity = '1';
            markers[0].style.transform = 'scale(1.05)';
        } else if (bmi < 25 && markers[1]) {
            markers[1].style.opacity = '1';
            markers[1].style.transform = 'scale(1.05)';
        } else if (bmi < 30 && markers[2]) {
            markers[2].style.opacity = '1';
            markers[2].style.transform = 'scale(1.05)';
        } else if (markers[3]) {
            markers[3].style.opacity = '1';
            markers[3].style.transform = 'scale(1.05)';
        }
    }
}

// Form Submission
if (predictionForm) {
    predictionForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Validate form
        if (!validateForm()) {
            return;
        }
        
        // Show loading spinner
        if (loadingSpinner) loadingSpinner.style.display = 'flex';
        
        // Collect form data
        const patientData = {
            gender: document.getElementById('gender').value,
            age: parseFloat(document.getElementById('age').value),
            hypertension: parseInt(document.getElementById('hypertension').value),
            heart_disease: parseInt(document.getElementById('heart_disease').value),
            ever_married: document.getElementById('ever_married').value,
            work_type: document.getElementById('work_type').value,
            Residence_type: document.getElementById('Residence_type').value,
            avg_glucose_level: parseFloat(document.getElementById('avg_glucose_level').value),
            height_cm: parseFloat(document.getElementById('height_cm').value),
            weight_kg: parseFloat(document.getElementById('weight_kg').value),
            smoking_status: document.getElementById('smoking_status').value
        };

        try {
            // Make API call
            const response = await fetch(`${API_URL}/predict`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(patientData)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || 'Prediction failed');
            }
            
            // Hide loading spinner
            if (loadingSpinner) loadingSpinner.style.display = 'none';
            
            // Display results
            displayResults(result);
            
        } catch (error) {
            if (loadingSpinner) loadingSpinner.style.display = 'none';
            showError('Error: ' + error.message);
        }
    });
}

// Form Validation
function validateForm() {
    const height = parseFloat(document.getElementById('height_cm').value);
    const weight = parseFloat(document.getElementById('weight_kg').value);
    const age = parseFloat(document.getElementById('age').value);
    const glucose = parseFloat(document.getElementById('avg_glucose_level').value);
    
    if (!height || height < 100 || height > 250) {
        showError('Height must be between 100cm and 250cm');
        return false;
    }
    
    if (!weight || weight < 30 || weight > 200) {
        showError('Weight must be between 30kg and 200kg');
        return false;
    }
    
    if (!age || age < 0 || age > 120) {
        showError('Please enter a valid age between 0 and 120');
        return false;
    }
    
    if (!glucose || glucose < 50 || glucose > 300) {
        showError('Glucose level must be between 50 and 300 mg/dL');
        return false;
    }
    
    return true;
}

// Display Results
function displayResults(result) {
    // Hide form, show results
    if (formContainer) formContainer.style.display = 'none';
    if (bmiCard) bmiCard.style.display = 'none';
    if (resultContainer) resultContainer.style.display = 'block';
    
    // Set risk indicator
    const indicator = document.getElementById('riskIndicator');
    if (indicator) {
        indicator.className = 'risk-indicator ' + result.risk_level.toLowerCase();
        indicator.textContent = result.risk_level;
    }
    
    // Set risk level
    const riskLevelEl = document.getElementById('riskLevel');
    if (riskLevelEl) riskLevelEl.textContent = result.risk_level + ' Risk';
    
    // Set probability
    const probabilityEl = document.getElementById('probability');
    if (probabilityEl) {
        probabilityEl.textContent = (result.probability * 100).toFixed(1) + '%';
    }
    
    // Set prediction status
    const predictionEl = document.getElementById('prediction');
    if (predictionEl) {
        predictionEl.textContent = result.prediction === 1 ? 'At Risk' : 'Not at Risk';
        predictionEl.style.color = result.prediction === 1 ? '#f44336' : '#4CAF50';
    }
    
    // Set BMI
    const resultBMIEl = document.getElementById('resultBMI');
    if (resultBMIEl) resultBMIEl.textContent = result.bmi;
    
    // Set message
    const messageEl = document.getElementById('message');
    if (messageEl) {
        messageEl.textContent = result.message;
        
        // Set message color based on risk
        if (result.risk_level === 'Low') {
            messageEl.style.background = '#e8f5e8';
            messageEl.style.color = '#2e7d32';
        } else if (result.risk_level === 'Medium') {
            messageEl.style.background = '#fff3e0';
            messageEl.style.color = '#ef6c00';
        } else {
            messageEl.style.background = '#ffebee';
            messageEl.style.color = '#c62828';
        }
    }
    
    // Generate recommendations
    generateRecommendations(result);
}

// Generate Recommendations based on risk level
function generateRecommendations(result) {
    if (!recommendationsDiv) return;
    
    let recommendations = '';
    
    if (result.risk_level === 'Low') {
        recommendations = `
            <h4><i class="fas fa-check-circle" style="color: #4CAF50;"></i> Keep Up the Good Work!</h4>
            <ul>
                <li><i class="fas fa-heart"></i> Maintain a healthy diet rich in fruits and vegetables</li>
                <li><i class="fas fa-running"></i> Exercise regularly (150 minutes per week)</li>
                <li><i class="fas fa-smoking-ban"></i> Avoid smoking and limit alcohol consumption</li>
                <li><i class="fas fa-calendar-check"></i> Schedule regular health checkups</li>
                <li><i class="fas fa-weight-scale"></i> Maintain your healthy BMI (${result.bmi})</li>
            </ul>
        `;
    } else if (result.risk_level === 'Medium') {
        recommendations = `
            <h4><i class="fas fa-exclamation-triangle" style="color: #FF9800;"></i> Time to Take Action!</h4>
            <ul>
                <li><i class="fas fa-heartbeat"></i> Monitor your blood pressure regularly</li>
                <li><i class="fas fa-apple-alt"></i> Reduce salt and saturated fat intake</li>
                <li><i class="fas fa-walking"></i> Increase physical activity to 30 minutes daily</li>
                <li><i class="fas fa-weight-scale"></i> Work towards a healthier BMI (currently ${result.bmi})</li>
                <li><i class="fas fa-user-md"></i> Consult your doctor for a checkup</li>
            </ul>
        `;
    } else {
        recommendations = `
            <h4><i class="fas fa-exclamation-circle" style="color: #f44336;"></i> Immediate Attention Needed!</h4>
            <ul>
                <li><i class="fas fa-ambulance"></i> Schedule a doctor's appointment immediately</li>
                <li><i class="fas fa-heart"></i> Monitor blood pressure and glucose daily</li>
                <li><i class="fas fa-pills"></i> Take prescribed medications regularly</li>
                <li><i class="fas fa-utensils"></i> Follow a strict heart-healthy diet</li>
                <li><i class="fas fa-dumbbell"></i> Begin a supervised exercise program</li>
                <li><i class="fas fa-weight-scale"></i> Work on achieving a healthy BMI (${result.bmi})</li>
            </ul>
        `;
    }
    
    recommendationsDiv.innerHTML = recommendations;
}

// Reset Form
function resetForm() {
    // Reset form
    if (predictionForm) predictionForm.reset();
    
    // Hide results, show form
    if (formContainer) formContainer.style.display = 'block';
    if (resultContainer) resultContainer.style.display = 'none';
    if (bmiCard) bmiCard.style.display = 'none';
    
    // Reset any custom styles
    const markers = document.querySelectorAll('.scale-marker');
    markers.forEach(marker => {
        marker.style.opacity = '1';
        marker.style.transform = 'none';
    });
}

// Show Error Message
function showError(message) {
    // Remove any existing toast
    const existingToast = document.querySelector('.error-toast');
    if (existingToast) existingToast.remove();
    
    // Create error toast
    const toast = document.createElement('div');
    toast.className = 'error-toast';
    toast.innerHTML = `
        <i class="fas fa-exclamation-circle"></i>
        <span>${message}</span>
    `;
    
    // Style the toast
    Object.assign(toast.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        backgroundColor: '#f44336',
        color: 'white',
        padding: '15px 20px',
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        zIndex: '1000',
        animation: 'slideIn 0.3s ease',
        maxWidth: '400px'
    });
    
    // Add icon style
    const icon = toast.querySelector('i');
    if (icon) {
        icon.style.fontSize = '20px';
    }
    
    document.body.appendChild(toast);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);