document.addEventListener('DOMContentLoaded', function () {
    const tabs = document.querySelectorAll('.tab-btn');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));

            // Add active to clicked
            tab.classList.add('active');

            // Show content
            const targetId = tab.getAttribute('data-tab');
            document.getElementById(targetId).classList.add('active');
        });
    });

    // Accordion functionality for "Read More"
    const expandBtns = document.querySelectorAll('.expand-btn');
    expandBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            const content = this.nextElementSibling;
            if (content.style.display === 'block') {
                content.style.display = 'none';
                this.textContent = 'Read More';
            } else {
                content.style.display = 'block';
                this.textContent = 'Show Less';
            }
        });
    });
});
