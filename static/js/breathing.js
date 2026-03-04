const circle = document.getElementById('breathing-circle');
const instruction = document.getElementById('breath-instruction');
let isBreathing = false;

function startBreathing() {
    if (isBreathing) return;
    isBreathing = true;

    document.getElementById('start-breath-btn').style.display = 'none';
    document.getElementById('stop-breath-btn').style.display = 'inline-block';

    breathingCycle();

    // Log session start
    fetch('/api/calm-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'breathing', duration: 0 }) // Duration tracked later if needed
    });
}

function stopBreathing() {
    isBreathing = false;
    document.getElementById('start-breath-btn').style.display = 'inline-block';
    document.getElementById('stop-breath-btn').style.display = 'none';

    circle.className = 'breathing-circle';
    instruction.textContent = "Ready to begin?";
}

function breathingCycle() {
    if (!isBreathing) return;

    // Inhale (4s)
    instruction.textContent = "Inhale...";
    circle.className = 'breathing-circle inhale';

    setTimeout(() => {
        if (!isBreathing) return;

        // Hold (7s -> abbreviated to 4s for UX pacing in web demo, user can adjust)
        instruction.textContent = "Hold...";
        circle.className = 'breathing-circle hold';

        setTimeout(() => {
            if (!isBreathing) return;

            // Exhale (8s)
            instruction.textContent = "Exhale...";
            circle.className = 'breathing-circle exhale';

            setTimeout(() => {
                breathingCycle(); // Loop
            }, 8000); // Exhale duration

        }, 4000); // Hold duration

    }, 4000); // Inhale duration
}

document.getElementById('start-breath-btn').addEventListener('click', startBreathing);
document.getElementById('stop-breath-btn').addEventListener('click', stopBreathing);
