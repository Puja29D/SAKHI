const canvas = document.getElementById('doodle-canvas');
const ctx = canvas.getContext('2d');
let isDrawing = false;
let color = '#E8A0BF'; // Default Dusty Rose

// Resize canvas
function resizeCanvas() {
    const parent = canvas.parentElement;
    canvas.width = Math.min(600, parent.clientWidth - 40);
    canvas.height = 400;
    ctx.lineCap = 'round';
    ctx.lineWidth = 5;
    ctx.strokeStyle = color;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas(); // Init

// Drawing Functions
function startDraw(e) {
    isDrawing = true;

    // We need to set the starting point so it doesn't draw a huge line from (0,0)
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    const x = ((e.clientX || e.touches[0].clientX) - rect.left) * scaleX;
    const y = ((e.clientY || e.touches[0].clientY) - rect.top) * scaleY;

    ctx.beginPath();
    ctx.moveTo(x, y);

    draw(e);
}

function endDraw() {
    isDrawing = false;
    ctx.beginPath();
}

function draw(e) {
    if (!isDrawing) return;

    const rect = canvas.getBoundingClientRect();

    // Calculate the scale to account for responsive CSS width vs internal canvas width
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    // Multiply by scale to get accurate internal coordinates
    const x = ((e.clientX || e.touches[0].clientX) - rect.left) * scaleX;
    const y = ((e.clientY || e.touches[0].clientY) - rect.top) * scaleY;

    ctx.lineTo(x, y);
    ctx.strokeStyle = color;
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(x, y);
}

// Events
canvas.addEventListener('mousedown', startDraw);
canvas.addEventListener('mouseup', endDraw);
canvas.addEventListener('mousemove', draw);
// Touch support
canvas.addEventListener('touchstart', (e) => { e.preventDefault(); startDraw(e); });
canvas.addEventListener('touchend', endDraw);
canvas.addEventListener('touchmove', (e) => { e.preventDefault(); draw(e); });

// Controls
document.querySelectorAll('.color-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelector('.color-btn.active').classList.remove('active');
        btn.classList.add('active');
        color = btn.dataset.color;
    });
});

document.getElementById('clear-canvas').addEventListener('click', () => {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
});

document.getElementById('save-canvas').addEventListener('click', () => {
    const link = document.createElement('a');
    link.download = 'my-safe-space.png';
    link.href = canvas.toDataURL();
    link.click();

    // Log functionality
    fetch('/api/calm-session', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'doodle', duration: 0 })
    });
});
