document.addEventListener('DOMContentLoaded', () => {
    const colorText = document.getElementById('colorText');
    const statusOverlay = document.getElementById('statusOverlay');
    const lightRed = document.getElementById('lightRed');
    const lightYellow = document.getElementById('lightYellow');
    const lightGreen = document.getElementById('lightGreen');
    const audioToggle = document.getElementById('audioToggle');
    
    let previousColor = "None";
    let audioEnabled = true;
    
    // Synthesize speech API
    const synth = window.speechSynthesis;
    
    function speak(text) {
        if (!audioEnabled || synth.speaking) return;
        
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.rate = 1.0;
        utterance.pitch = 1.1; // Slightly higher pitch for alert style
        synth.speak(utterance);
    }
    
    audioToggle.addEventListener('click', () => {
        audioEnabled = !audioEnabled;
        if (audioEnabled) {
            audioToggle.classList.add('active');
            audioToggle.textContent = 'Audio Alerts: ON';
            // Speak a test message to initialize audio context on user interaction
            speak("Audio enabled");
        } else {
            audioToggle.classList.remove('active');
            audioToggle.textContent = 'Audio Alerts: OFF';
            synth.cancel(); // Stop any pending speech
        }
    });

    function updateUI(color) {
        // Reset styles
        lightRed.classList.remove('active');
        lightYellow.classList.remove('active');
        lightGreen.classList.remove('active');
        
        colorText.className = '';
        
        if (color === "None") {
            colorText.textContent = "Searching...";
            colorText.classList.add('none');
            statusOverlay.textContent = "Scanning...";
            statusOverlay.style.color = "white";
        } else {
            colorText.textContent = color;
            colorText.classList.add(color.toLowerCase());
            statusOverlay.textContent = `${color} Detected`;
            
            if (color === "Red") {
                lightRed.classList.add('active');
                statusOverlay.style.color = "#ef4444";
            } else if (color === "Yellow") {
                lightYellow.classList.add('active');
                statusOverlay.style.color = "#eab308";
            } else if (color === "Green") {
                lightGreen.classList.add('active');
                statusOverlay.style.color = "#22c55e";
            }
        }
    }

    async function fetchColor() {
        try {
            const response = await fetch('/get_color');
            const data = await response.json();
            const currentColor = data.color;
            
            if (currentColor !== previousColor) {
                updateUI(currentColor);
                
                // Trigger audio alert on change (ignoring "None" to avoid spam)
                if (currentColor !== "None") {
                    speak(`${currentColor} Light Detected`);
                }
                
                previousColor = currentColor;
            }
            
        } catch (error) {
            console.error("Error fetching color:", error);
        }
    }

    // Poll for color updates every 500ms
    setInterval(fetchColor, 500);
});
