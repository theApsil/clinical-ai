async function checkStatus(taskId) {
    try {
        const response = await fetch(`/api/v1/upload/status/${taskId}`);

        const rawText = await response.text();
        let data;

        try {
            data = JSON.parse(rawText);
        } catch (e) {
            console.error("RAW RESPONSE:", rawText);
            throw new Error("Сервер вернул некорректный ответ");
        }

        if (!response.ok) {
            throw new Error(data.detail || 'Ошибка получения статуса');
        }

        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        const statusMessage = document.getElementById('statusMessage');
        const statusInfo = document.getElementById('statusInfo');
        const chatButtonContainer = document.getElementById('chatButtonContainer');
        const chatButton = document.getElementById('chatButton');

        const progress = Math.min(Number(data.progress) || 0, 100);

        if (progressBar) progressBar.style.width = `${progress}%`;
        if (progressText) progressText.textContent = `${progress}%`;

        let message = '';
        let alertClass = 'alert-info';

        switch (data.status) {
            case 'pending':
                message = `⏳ Обработка документа: ${progress}%`;
                break;

            case 'done':
                message = '✅ Документ успешно обработан';
                alertClass = 'alert-success';

                if (chatButtonContainer && chatButton) {
                    chatButtonContainer.style.display = 'block';
                    chatButton.href = `/chat/${data.session_id}`;
                }
                break;

            case 'error':
                message = `❌ Ошибка обработки: ${data.error || 'Неизвестная ошибка'}`;
                alertClass = 'alert-danger';
                break;

            default:
                message = `Статус: ${data.status || 'unknown'}`;
        }

        if (statusInfo) statusInfo.className = `alert ${alertClass}`;
        if (statusMessage) statusMessage.textContent = message;

        // ❗ Останавливаем polling
        if (data.status === 'done' || data.status === 'error') {
            return;
        }

        setTimeout(() => checkStatus(taskId), 2000);

    } catch (error) {
        console.error('Error checking status:', error);

        const statusInfo = document.getElementById('statusInfo');
        const statusMessage = document.getElementById('statusMessage');

        if (statusInfo) statusInfo.className = 'alert alert-danger';
        if (statusMessage) {
            statusMessage.textContent =
                `❌ Ошибка: ${error.message}. Попробуйте обновить страницу.`;
        }
    }
}
