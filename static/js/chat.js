document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('chatbot-toggle');
    const closeBtn = document.getElementById('chatbot-close');
    const chatWindow = document.getElementById('chatbot-window');
    const inputField = document.getElementById('chatbot-input');
    const sendBtn = document.getElementById('chatbot-send');
    const messagesContainer = document.getElementById('chatbot-messages');

    let isTyping = false;

    // Toggle chat window
    toggleBtn.addEventListener('click', () => {
        chatWindow.classList.toggle('hidden');
        if (!chatWindow.classList.contains('hidden')) {
            inputField.focus();
            scrollToBottom();
        }
    });

    closeBtn.addEventListener('click', () => {
        chatWindow.classList.add('hidden');
    });

    // Send message on button click or Enter key
    sendBtn.addEventListener('click', sendMessage);
    inputField.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    async function sendMessage() {
        const text = inputField.value.trim();
        if (!text || isTyping) return;

        // 1. Add User Message
        appendMessage('user', text);
        inputField.value = '';

        // 2. Show Typing Indicator
        isTyping = true;
        sendBtn.disabled = true;
        const typingIndicator = addTypingIndicator();
        scrollToBottom();

        // 3. Call API
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: text })
            });

            const data = await response.json();

            // Remove typing indicator
            typingIndicator.remove();

            // 4. Add Bot Response
            if (data.status === 'success') {
                appendMessage('bot', data.response, true); // Use simple markdown parsing
            } else {
                appendMessage('bot', data.message || "Sorry, I couldn't reach the server.");
            }
        } catch (error) {
            console.error('Chat API Error:', error);
            typingIndicator.remove();
            appendMessage('bot', "Sorry, I'm having trouble connecting right now. Please try again later.");
        } finally {
            isTyping = false;
            sendBtn.disabled = false;
            inputField.focus();
            scrollToBottom();

            // Re-initialize Lucide icons if markdown returned icons (unlikely but safe)
            if (window.lucide) {
                window.lucide.createIcons();
            }
        }
    }

    function appendMessage(sender, text, parseMarkdown = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;

        if (parseMarkdown) {
            // Very basic markdown parsing for bold, italic, lists (since Gemini returns markdown)
            let formattedText = text
                // Bold
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                // Italic
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                // New lines to br (only if not a list)
                .replace(/\n\n/g, '</p><p>')
                .replace(/\n/g, '<br>');

            // Handle basic bullet lists
            if (formattedText.includes('* ')) {
                formattedText = formattedText.replace(/(?:^|<br>)\* (.*?)(?=<br>|$)/g, '<li>$1</li>');
                formattedText = formattedText.replace(/(<li>.*?<\/li>)/g, '<ul>$1</ul>');
                formattedText = formattedText.replace(/<\/ul><ul>/g, ''); // merge adjacent lists
            }

            msgDiv.innerHTML = `<p>${formattedText}</p>`;
        } else {
            msgDiv.textContent = text;
        }

        messagesContainer.appendChild(msgDiv);
        scrollToBottom();
    }

    function addTypingIndicator() {
        const msgDiv = document.createElement('div');
        msgDiv.className = 'message bot typing';
        msgDiv.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        messagesContainer.appendChild(msgDiv);
        return msgDiv;
    }
});
