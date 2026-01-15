async function checkStatus(taskId) {
    try {
        const response = await fetch(`/upload/status/${taskId}`);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Ошибка получения статуса');
        }
        
        // Обновляем прогресс-бар
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        const statusMessage = document.getElementById('statusMessage');
        const chatButtonContainer = document.getElementById('chatButtonContainer');
        const chatButton = document.getElementById('chatButton');
        
        const progress = Math.min(data.progress, 100);
        progressBar.style.width = `${progress}%`;
        progressText.textContent = `${progress}%`;
        
        // Обновляем сообщение в зависимости от статуса
        let message = '';
        let alertClass = 'alert-info';
        
        switch(data.status) {
            case 'pending':
                message = `Обработка на стадии: ${progress}%`;
                break;
            case 'done':
                message = '✅ Документ успешно обработан!';
                alertClass = 'alert-success';
                // Показываем кнопку чата
                chatButtonContainer.style.display = 'block';
                chatButton.href = `/chat/${data.session_id}`;
                break;
            case 'error':
                message = `❌ Ошибка обработки: ${data.error || 'Неизвестная ошибка'}`;
                alertClass = 'alert-danger';
                break;
            default:
                message = `Статус: ${data.status}, прогресс: ${progress}%`;
        }
        
        document.getElementById('statusInfo').className = `alert ${alertClass}`;
        statusMessage.textContent = message;
        
        // Если обработка завершена или произошла ошибка, прекращаем проверку
        if (data.status === 'done' || data.status === 'error') {
            return;
        }
        
        // Продолжаем проверку каждые 2 секунды
        setTimeout(() => checkStatus(taskId), 2000);
        
    } catch (error) {
        console.error('Error checking status:', error);
        const statusInfo = document.getElementById('statusInfo');
        statusInfo.className = 'alert alert-danger';
        document.getElementById('statusMessage').textContent = `❌ Ошибка: ${error.message}. Попробуйте обновить страницу.`;
    }
}