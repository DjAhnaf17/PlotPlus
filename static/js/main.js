document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('prediction-form');
    
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const area = document.getElementById('area').value;
            const rooms = document.getElementById('rooms').value;
            const kitchen = document.getElementById('kitchen').value;
            
            const btn = document.getElementById('predict-btn');
            const btnText = btn.querySelector('.btn-text');
            const loader = btn.querySelector('.loader');
            const resultContainer = document.getElementById('result-container');
            const predictedPrice = document.getElementById('predicted-price');
            
            // Loading State
            btn.disabled = true;
            btnText.classList.add('hidden');
            loader.classList.remove('hidden');
            resultContainer.classList.add('hidden');
            
            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ area, rooms, kitchen })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    predictedPrice.textContent = data.formatted;
                    
                    // Small delay for effect
                    setTimeout(() => {
                        resultContainer.classList.remove('hidden');
                        
                        // Count up animation logic
                        let start = 0;
                        const end = data.price;
                        const duration = 1500;
                        const startTime = performance.now();
                        
                        function updateCounter(currentTime) {
                            const elapsed = currentTime - startTime;
                            const progress = Math.min(elapsed / duration, 1);
                            
                            // Easing out cubic
                            const easeOut = 1 - Math.pow(1 - progress, 3);
                            const current = start + (end - start) * easeOut;
                            
                            predictedPrice.textContent = '₹ ' + current.toLocaleString('en-IN', { maximumFractionDigits: 2, minimumFractionDigits: 2 });
                            
                            if (progress < 1) {
                                requestAnimationFrame(updateCounter);
                            } else {
                                predictedPrice.textContent = data.formatted;
                            }
                        }
                        requestAnimationFrame(updateCounter);
                        
                    }, 300);
                } else {
                    alert('Error: ' + data.error);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Something went wrong during prediction.');
            } finally {
                // Restore Button State
                btn.disabled = false;
                btnText.classList.remove('hidden');
                loader.classList.add('hidden');
            }
        });
    }
});
