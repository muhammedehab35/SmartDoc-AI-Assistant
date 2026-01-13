/**
 * SmartDoc Assistant - Frontend JavaScript
 * Gestion de l'interface utilisateur et communication avec l'API
 */

// ===== CONFIGURATION =====

let CONFIG = {
    apiUrl: localStorage.getItem('smartdoc_api_url') || '',
    userId: localStorage.getItem('smartdoc_user_id') || 'user_marie_123'
};

// ===== INITIALISATION =====

document.addEventListener('DOMContentLoaded', function() {
    console.log('SmartDoc Assistant initialisé');

    // Vérifier la configuration
    if (!CONFIG.apiUrl) {
        console.warn('API URL non configurée');
        setTimeout(() => {
            openConfig();
        }, 1000);
    } else {
        updateStatus('Prêt', 'success');
    }

    // Focus sur l'input
    document.getElementById('userInput').focus();
});

// ===== GESTION DES MESSAGES =====

async function sendMessage() {
    const input = document.getElementById('userInput');
    const message = input.value.trim();

    if (!message) {
        return;
    }

    // Vérifier la configuration
    if (!CONFIG.apiUrl) {
        alert('⚠️ Veuillez configurer l\'URL de l\'API d\'abord (cliquez sur ⚙️)');
        openConfig();
        return;
    }

    // Afficher le message utilisateur
    addMessage(message, 'user');
    input.value = '';

    // Afficher le loading
    showLoading();
    updateStatus('Traitement...', 'loading');

    try {
        const response = await fetch(`${CONFIG.apiUrl}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: CONFIG.userId,
                message: message
            })
        });

        hideLoading();

        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        const data = await response.json();

        // Afficher la réponse
        addMessage(data.response, 'assistant');
        updateStatus('Prêt', 'success');

        // Log pour debug
        console.log('Intent:', data.intent);
        console.log('Agent utilisé:', data.agent_used);

    } catch (error) {
        console.error('Erreur:', error);
        hideLoading();

        addMessage(
            '😔 Désolé, je rencontre une difficulté technique.\n\n' +
            'Vérifiez que:\n' +
            '• L\'URL de l\'API est correcte\n' +
            '• Vous êtes connecté à Internet\n' +
            '• L\'API est bien déployée\n\n' +
            `Erreur: ${error.message}`,
            'assistant',
            true
        );

        updateStatus('Erreur de connexion', 'error');
    }
}

function addMessage(text, type, isError = false) {
    const chatContainer = document.getElementById('chatContainer');

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;

    if (isError) {
        messageDiv.classList.add('error');
    }

    // Icône
    const iconDiv = document.createElement('div');
    iconDiv.className = 'message-icon';
    iconDiv.textContent = type === 'user' ? '👤' : '🤖';

    // Contenu
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    // Convertir les sauts de ligne en paragraphes
    const paragraphs = text.split('\n').filter(p => p.trim());
    paragraphs.forEach(para => {
        const p = document.createElement('p');
        p.textContent = para;
        contentDiv.appendChild(p);
    });

    messageDiv.appendChild(iconDiv);
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);

    // Scroll automatique
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showLoading() {
    const chatContainer = document.getElementById('chatContainer');

    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loadingIndicator';
    loadingDiv.className = 'loading';
    loadingDiv.innerHTML = `
        <div class="message-icon">🤖</div>
        <div class="message-content">
            <span>Je réfléchis</span>
            <div class="loading-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;

    chatContainer.appendChild(loadingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function hideLoading() {
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

// ===== ACTIONS RAPIDES =====

function quickAction(action) {
    const input = document.getElementById('userInput');

    const messages = {
        'medications': 'Quels sont mes médicaments à prendre aujourd\'hui?',
        'appointments': 'Quand est mon prochain rendez-vous?',
        'symptoms': 'Je ne me sens pas très bien, j\'aimerais vous décrire mes symptômes.',
        'help': 'Peux-tu m\'expliquer comment tu peux m\'aider?'
    };

    if (messages[action]) {
        input.value = messages[action];
        sendMessage();
    }
}

// ===== URGENCE =====

async function emergency() {
    const confirmed = confirm(
        '⚠️ ALERTE D\'URGENCE\n\n' +
        'Voulez-vous vraiment déclencher une alerte d\'urgence?\n\n' +
        'Vos contacts d\'urgence seront immédiatement prévenus.'
    );

    if (!confirmed) {
        return;
    }

    const reason = prompt(
        'Que se passe-t-il?\n\n' +
        'Décrivez brièvement votre situation:',
        'J\'ai besoin d\'aide urgente'
    );

    if (!reason) {
        return;
    }

    // Afficher le message d'urgence
    addMessage(`🚨 URGENCE: ${reason}`, 'user');
    showLoading();
    updateStatus('🚨 URGENCE EN COURS', 'error');

    try {
        const response = await fetch(`${CONFIG.apiUrl}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: CONFIG.userId,
                message: `URGENCE: ${reason}`
            })
        });

        hideLoading();

        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }

        const data = await response.json();
        addMessage(data.response, 'assistant');

        // Vibration si disponible
        if (navigator.vibrate) {
            navigator.vibrate([200, 100, 200, 100, 200]);
        }

        // Son d'alerte (si possible)
        playAlertSound();

        updateStatus('Urgence traitée', 'success');

    } catch (error) {
        console.error('Erreur urgence:', error);
        hideLoading();

        // Message de secours même en cas d'erreur
        addMessage(
            '🚨 URGENCE DÉTECTÉE\n\n' +
            'En cas de danger immédiat:\n\n' +
            '📞 Appelez le 15 (SAMU)\n' +
            '📞 Appelez le 18 (Pompiers)\n' +
            '📞 Appelez le 112 (Urgences)\n\n' +
            'Ne restez pas seul(e)!',
            'assistant'
        );

        updateStatus('Erreur - Appelez les urgences!', 'error');
    }
}

function playAlertSound() {
    try {
        // Créer un son simple avec Web Audio API
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);

        oscillator.frequency.value = 800;
        oscillator.type = 'sine';

        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);

        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.5);
    } catch (e) {
        console.log('Son d\'alerte non disponible');
    }
}

// ===== GESTION DU CLAVIER =====

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

// ===== CONFIGURATION =====

function openConfig() {
    const modal = document.getElementById('configModal');
    const apiUrlInput = document.getElementById('apiUrlInput');
    const userIdInput = document.getElementById('userIdInput');

    apiUrlInput.value = CONFIG.apiUrl;
    userIdInput.value = CONFIG.userId;

    modal.style.display = 'block';
}

function closeConfig() {
    const modal = document.getElementById('configModal');
    modal.style.display = 'none';
}

function saveConfig() {
    const apiUrlInput = document.getElementById('apiUrlInput');
    const userIdInput = document.getElementById('userIdInput');

    const apiUrl = apiUrlInput.value.trim();
    const userId = userIdInput.value.trim();

    if (!apiUrl) {
        alert('⚠️ L\'URL de l\'API est requise');
        return;
    }

    if (!userId) {
        alert('⚠️ L\'ID utilisateur est requis');
        return;
    }

    // Valider l'URL
    try {
        new URL(apiUrl);
    } catch (e) {
        alert('⚠️ L\'URL de l\'API n\'est pas valide');
        return;
    }

    // Sauvegarder
    CONFIG.apiUrl = apiUrl;
    CONFIG.userId = userId;

    localStorage.setItem('smartdoc_api_url', apiUrl);
    localStorage.setItem('smartdoc_user_id', userId);

    closeConfig();

    // Message de confirmation
    addMessage(
        `✅ Configuration sauvegardée!\n\n` +
        `API: ${apiUrl}\n` +
        `Utilisateur: ${userId}`,
        'assistant'
    );

    updateStatus('Prêt', 'success');
}

// Fermer le modal en cliquant à l'extérieur
window.onclick = function(event) {
    const modal = document.getElementById('configModal');
    if (event.target === modal) {
        closeConfig();
    }
}

// ===== GESTION DU STATUS =====

function updateStatus(text, type = 'success') {
    const statusText = document.getElementById('statusText');
    const statusDot = document.querySelector('.status-dot');

    statusText.textContent = text;

    // Couleurs selon le type
    const colors = {
        'success': '#48bb78',
        'error': '#f56565',
        'loading': '#ed8936',
        'warning': '#ecc94b'
    };

    if (statusDot) {
        statusDot.style.background = colors[type] || colors.success;
    }
}

// ===== HELPERS =====

function formatMessage(text) {
    // Convertir les emojis et formatage spécial
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>');
}

// ===== MESSAGES D'AIDE =====

const HELP_MESSAGES = {
    medications: "Je peux vous aider avec vos médicaments:\n• Liste de vos médicaments\n• Rappels de prise\n• Informations sur la posologie",
    appointments: "Je peux gérer vos rendez-vous:\n• Prochains rendez-vous\n• Détails des consultations\n• Rappels avant RDV",
    symptoms: "Je peux analyser vos symptômes:\n• Évaluation de la gravité\n• Recommandations\n• Quand consulter un médecin",
    emergency: "En cas d'urgence:\n• J'alerte vos contacts\n• Je vous guide\n• J'enregistre la situation"
};

// ===== EXPORT POUR UTILISATION EXTERNE =====

window.SmartDoc = {
    sendMessage,
    quickAction,
    emergency,
    openConfig,
    updateStatus
};

console.log('SmartDoc Assistant chargé et prêt! 🏥');
