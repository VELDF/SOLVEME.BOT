document.addEventListener('DOMContentLoaded', () => {
    const body = document.body;
    const mainContent = document.getElementById('main-content');
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const suggestionButtons = document.querySelectorAll('.suggestion-btn');
    const resetBtn = document.getElementById('reset-chat-btn');
    const scrollToTopBtn = document.getElementById('scroll-to-top-btn');
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');

    let conversationHistory = [];
    const MAX_HISTORY_LENGTH = 6;

    function addMessage(text, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);
        const contentHtml = marked.parse(text);
        messageElement.innerHTML = contentHtml;
        if (sender === 'bot') {
            const copyBtn = document.createElement('button');
            copyBtn.className = 'copy-btn';
            copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i>';
            copyBtn.title = 'Copiar texto';
            copyBtn.onclick = () => {
                const textToCopy = new DOMParser().parseFromString(contentHtml, 'text/html').body.textContent || "";
                navigator.clipboard.writeText(textToCopy).then(() => {
                    copyBtn.innerHTML = '<i class="fa-solid fa-check"></i>';
                    setTimeout(() => { copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i>'; }, 2000);
                });
            };
            messageElement.appendChild(copyBtn);
        }
        chatBox.appendChild(messageElement);
        mainContent.scrollTop = mainContent.scrollHeight;
        return messageElement;
    }

    async function handleSendMessage() {
        const prompt = userInput.value.trim();
        if (!prompt) return;
        if (!body.classList.contains('chat-active')) { body.classList.add('chat-active'); }
        addMessage(prompt, 'user');
        conversationHistory.push({ role: 'user', content: prompt });
        userInput.value = '';
        userInput.focus();
        const botMessageElement = addMessage('<div class="typing-indicator"><span></span><span></span><span></span></div>', 'bot');
        try {
            const historyToSend = conversationHistory.slice(-MAX_HISTORY_LENGTH - 1, -1);
            const response = await fetch('http://127.0.0.1:8000/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: prompt, history: historyToSend }),
            });
            if (!response.ok) throw new Error('Erro de rede.');
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullResponse = "";
            let firstChunk = true;
            while (true) {
                const { value, done } = await reader.read();
                if (done) break;
                if (firstChunk) { botMessageElement.innerHTML = ''; firstChunk = false; }
                fullResponse += decoder.decode(value, { stream: true });
                botMessageElement.innerHTML = marked.parse(fullResponse + '▌');
                mainContent.scrollTop = mainContent.scrollHeight;
            }
            const finalHtml = marked.parse(fullResponse);
            botMessageElement.innerHTML = finalHtml;
            const copyBtn = document.createElement('button');
            copyBtn.className = 'copy-btn';
            copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i>';
            copyBtn.title = 'Copiar texto';
            copyBtn.onclick = () => {
                navigator.clipboard.writeText(fullResponse).then(() => {
                    copyBtn.innerHTML = '<i class="fa-solid fa-check"></i>';
                    setTimeout(() => { copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i>'; }, 2000);
                });
            };
            botMessageElement.appendChild(copyBtn);
            conversationHistory.push({ role: 'assistant', content: fullResponse });
        } catch (error) {
            console.error('Erro:', error);
            botMessageElement.innerHTML = "Desculpe, ocorreu um erro.";
        }
    }

    function resetChat() {
        chatBox.innerHTML = '';
        body.classList.remove('chat-active');
        conversationHistory = [];
    }

    function scrollToTop() { mainContent.scrollTo({ top: 0, behavior: 'smooth' }); }
    function handleScroll() { scrollToTopBtn.style.display = mainContent.scrollTop > 300 ? 'flex' : 'none'; }
    function searchMessages() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        chatBox.querySelectorAll('mark.highlight').forEach(el => { el.outerHTML = el.innerHTML; });
        if (!searchTerm) return;
        const messages = chatBox.querySelectorAll('.message');
        messages.forEach(message => {
            const text = message.innerText.toLowerCase();
            if (text.includes(searchTerm)) {
                const regex = new RegExp(searchTerm, 'gi');
                const contentDiv = message.querySelector('.message-content') || message;
                contentDiv.innerHTML = contentDiv.innerHTML.replace(regex, `<mark class="highlight">$&</mark>`);
            }
        });
    }

    sendBtn.addEventListener('click', handleSendMessage);
    userInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); handleSendMessage(); } });
    resetBtn.addEventListener('click', resetChat);
    scrollToTopBtn.addEventListener('click', scrollToTop);
    mainContent.addEventListener('scroll', handleScroll);
    searchBtn.addEventListener('click', searchMessages);
    searchInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') searchMessages(); });
    suggestionButtons.forEach(button => {
        button.addEventListener('click', () => {
            userInput.value = button.textContent;
            handleSendMessage();
        });
    });
});