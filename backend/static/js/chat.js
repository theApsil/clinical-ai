function initChat(sessionId) {
    const MAX_TEXTAREA_HEIGHT = 200;

    const chatMessages = document.getElementById('chatMessages');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');

    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';

        if (messageInput.scrollHeight <= MAX_TEXTAREA_HEIGHT) {
            messageInput.style.height = messageInput.scrollHeight + 'px';
            messageInput.style.overflowY = 'hidden';
        } else {
            messageInput.style.height = MAX_TEXTAREA_HEIGHT + 'px';
            messageInput.style.overflowY = 'auto';
        }
    });


    // Функция для добавления сообщения в чат
    function addMessage(text, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;

        const now = new Date();
        const timeString = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;

        text

        messageDiv.innerHTML = `
            <div class="message-content">
                <p>${text.replace(/\\n/g, '<br>')}</p>
            </div>
            <div class="message-time">
                ${timeString}
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        return messageDiv;
    }

    // Функция для отправки сообщения
    async function sendMessage() {
        const text = messageInput.value.trim();
        if (!text) return;

        // Добавляем сообщение пользователя
        addMessage(text, true);
        messageInput.value = '';
        messageInput.rows = 1;
        messageInput.style.height = 'auto';
        messageInput.style.overflowY = 'hidden';
        sendButton.disabled = true;

        // Добавляем индикатор загрузки для ответа бота
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'message bot-message loading';
        loadingDiv.innerHTML = `
            <div class="message-content">
                <div class="spinner-border spinner-border-sm" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
            </div>
        `;
        chatMessages.appendChild(loadingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const response = await fetch('/api/v1/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    message: text
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Ошибка отправки сообщения');
            }

            // Удаляем индикатор загрузки
            chatMessages.removeChild(loadingDiv);

            // Добавляем ответ бота
            // addMessage(data.response || data.message || 'Без ответа');
            let botResponseText = 'Без ответа'; // Текст по умолчанию

            if (data.type === "questions" && Array.isArray(data.content)) {
            // Форматируем массив вопросов в читаемый текст
                botResponseText = data.content.join('\n');
            } else if (data.type === "final_decision"){
                botResponseText = data.content;
            } else if (data.response) {
            // Старый формат: поле response
                botResponseText = data.response;
            } else if (data.message) {
            // Старый формат: поле message
                botResponseText = data.message;
            } else {
            // Если формат неизвестен, показываем весь объект для отладки
                console.warn('Неизвестный формат ответа:', data);
                botResponseText = `Неизвестный формат ответа: ${JSON.stringify(data)}`;
            }

            // Добавляем ответ бота
            addMessage(botResponseText);

        } catch (error) {
            console.error('Error sending message:', error);
            // Удаляем индикатор загрузки
            chatMessages.removeChild(loadingDiv);

            // Добавляем сообщение об ошибке
            addMessage(`❌ Ошибка: ${error.message}. Попробуйте снова.`);
        } finally {
            sendButton.disabled = false;
            messageInput.rows = 1;
            messageInput.style.height = 'auto';
            messageInput.style.overflowY = 'hidden';
            messageInput.focus();
        }
    }

    // Обработчики событий
    sendButton.addEventListener('click', sendMessage);
    
messageInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        if (e.shiftKey) {
            return;
        } else {
            e.preventDefault();
            sendMessage();
        }
    }
});

    messageInput.focus();
}