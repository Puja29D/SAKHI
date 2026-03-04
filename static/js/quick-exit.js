document.addEventListener('DOMContentLoaded', function () {
    const quickExitBtn = document.getElementById('quick-exit-btn');

    if (quickExitBtn) {
        quickExitBtn.addEventListener('click', function (e) {
            e.preventDefault();
            // 1. Immediately replace current history state to prevent back button
            window.history.replaceState(null, '', '/');

            // 2. Open Google in current tab
            window.location.href = "https://www.google.com";

            // 3. Optional: Open another tab with weather or news if possible (often blocked by popup blockers)
            // window.open("https://www.weather.com", "_blank");
        });
    }

    // Key binding: ESC key three times to exit quickly
    let escCount = 0;
    document.addEventListener('keydown', function (e) {
        if (e.key === "Escape") {
            escCount++;
            if (escCount >= 3) {
                quickExitBtn.click();
            }
            // Reset counter after 1 second
            setTimeout(() => { escCount = 0; }, 1000);
        }
    });
});
