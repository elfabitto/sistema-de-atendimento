// JavaScript principal do Sistema de Fila de Atendimento

// Utilitários
const Utils = {
    // Mostra notificação toast
    showNotification(message, type = 'info') {
        const colors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            warning: 'bg-yellow-500',
            info: 'bg-blue-500'
        };
        
        const notification = document.createElement('div');
        notification.className = `notification ${colors[type]} text-white px-6 py-4 rounded-lg shadow-lg`;
        notification.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} mr-3"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    },
    
    // Formata tempo em minutos
    formatTime(minutes) {
        if (minutes < 60) {
            return `${Math.floor(minutes)} min`;
        }
        const hours = Math.floor(minutes / 60);
        const mins = Math.floor(minutes % 60);
        return `${hours}h ${mins}min`;
    },
    
    // Formata data
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
};

// Gerenciador de notificações do navegador
const NotificationManager = {
    init() {
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    },
    
    show(title, body, icon = null) {
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: body,
                icon: icon || '/static/icon.png',
                badge: '/static/badge.png'
            });
        }
    }
};

// Timer para atendimentos
class AtendimentoTimer {
    constructor(elementId, timeoutMinutes) {
        this.element = document.getElementById(elementId);
        this.timeoutMinutes = timeoutMinutes;
        this.startTime = new Date();
        this.interval = null;
    }
    
    start() {
        this.update();
        this.interval = setInterval(() => this.update(), 60000); // Atualiza a cada minuto
    }
    
    stop() {
        if (this.interval) {
            clearInterval(this.interval);
        }
    }
    
    update() {
        const now = new Date();
        const elapsed = Math.floor((now - this.startTime) / 60000); // minutos
        const remaining = this.timeoutMinutes - elapsed;
        
        if (this.element) {
            this.element.textContent = `${elapsed} minutos`;
            
            // Muda cor baseado no tempo restante
            if (remaining <= 5) {
                this.element.classList.add('timer-danger');
                this.element.classList.remove('timer-warning');
            } else if (remaining <= 10) {
                this.element.classList.add('timer-warning');
                this.element.classList.remove('timer-danger');
            }
        }
    }
}

// Inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Inicializa notificações
    NotificationManager.init();
    
    // Fecha modais ao clicar fora
    document.addEventListener('click', function(event) {
        const modals = document.querySelectorAll('[id^="modal-"]');
        modals.forEach(modal => {
            if (event.target === modal) {
                modal.classList.add('hidden');
            }
        });
    });
    
    // Fecha modais com ESC
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            const modals = document.querySelectorAll('[id^="modal-"]');
            modals.forEach(modal => {
                modal.classList.add('hidden');
            });
        }
    });
    
    // Auto-hide para mensagens flash
    setTimeout(() => {
        const flashMessages = document.querySelectorAll('[role="alert"]');
        flashMessages.forEach(msg => {
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 300);
        });
    }, 5000);
});

// Exporta utilitários globalmente
window.Utils = Utils;
window.NotificationManager = NotificationManager;
window.AtendimentoTimer = AtendimentoTimer;
