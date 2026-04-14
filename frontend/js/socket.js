/**
 * SocketIO Client Module
 * 
 * Provides real-time communication with the backend server using SocketIO.
 * Features:
 * - Automatic reconnection with exponential backoff
 * - Connection status monitoring
 * - Error handling and UI feedback
 * - Agent state synchronization
 * 
 * @module SocketIOClient
 * @version 2.0.0
 */

// Reconnection configuration with exponential backoff
const RECONNECT_CONFIG = {
    /** Initial reconnection delay in milliseconds */
    INITIAL_DELAY: 1000,
    /** Maximum reconnection delay in milliseconds */
    MAX_DELAY: 30000,
    /** Backoff multiplier for exponential delay */
    BACKOFF_MULTIPLIER: 2,
    /** Maximum number of reconnection attempts (-1 for infinite) */
    MAX_ATTEMPTS: -1,
    /** Randomization factor to prevent thundering herd (0.0-1.0) */
    RANDOMIZATION_FACTOR: 0.5
};

/** @type {Object|null} SocketIO instance */
let socket = null;

/** @type {number} Current reconnection attempt count */
let reconnectAttempts = 0;

/** @type {number|null} Reconnection timeout ID */
let reconnectTimeout = null;

/**
 * Calculate delay for next reconnection attempt using exponential backoff.
 * 
 * Uses the formula: min(initial_delay * (backoff_multiplier ^ attempt), max_delay)
 * With randomization to prevent simultaneous reconnection storms.
 * 
 * @param {number} attempt - Current attempt number (0-indexed)
 * @returns {number} Delay in milliseconds
 */
function calculateReconnectDelay(attempt) {
    const exponentialDelay = RECONNECT_CONFIG.INITIAL_DELAY * 
        Math.pow(RECONNECT_CONFIG.BACKOFF_MULTIPLIER, attempt);
    const randomizedDelay = exponentialDelay * 
        (1 + Math.random() * RECONNECT_CONFIG.RANDOMIZATION_FACTOR);
    return Math.min(randomizedDelay, RECONNECT_CONFIG.MAX_DELAY);
}

/**
 * Display connection error message to user.
 * 
 * Shows an error notification with the error message and attempt count.
 * The notification auto-dismisses after 3 seconds.
 * 
 * @param {string} message - Error message to display
 * @param {number} attempt - Current reconnection attempt number
 */
function showErrorNotification(message, attempt) {
    // Remove existing notification if any
    const existingNotification = document.getElementById('socket-error-notification');
    if (existingNotification) {
        existingNotification.remove();
    }

    // Create notification element
    const notification = document.createElement('div');
    notification.id = 'socket-error-notification';
    notification.className = 'socket-error-notification';
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-icon">⚠️</span>
            <div class="notification-text">
                <strong>${escapeHtml(message)}</strong>
                <p>正在重连... (第 ${attempt + 1} 次尝试)</p>
            </div>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;

    // Append to body
    document.body.appendChild(notification);

    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 3000);
}

/**
 * Escape HTML special characters to prevent XSS attacks.
 * 
 * @param {string} text - Raw text to escape
 * @returns {string} Escaped HTML-safe string
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Initialize SocketIO connection with reconnection support.
 * 
 * Sets up the WebSocket connection with automatic reconnection
 * using exponential backoff strategy. Handles all connection
 * state changes and provides UI feedback.
 */
function initSocket() {
    // Connect to SocketIO server with reconnection options
    socket = io({
        transports: ['websocket', 'polling'],
        upgrade: false,
        reconnection: true,
        reconnectionAttempts: RECONNECT_CONFIG.MAX_ATTEMPTS,
        reconnectionDelay: RECONNECT_CONFIG.INITIAL_DELAY,
        reconnectionDelayMax: RECONNECT_CONFIG.MAX_DELAY,
        randomizeReconnectionDelay: true
    });

    // Handle successful connection
    socket.on('connect', () => {
        console.log('[SocketIO] Connected to server');
        reconnectAttempts = 0;
        showStatus('connected');
        
        // Clear any pending reconnection
        if (reconnectTimeout) {
            clearTimeout(reconnectTimeout);
            reconnectTimeout = null;
        }
        
        // Subscribe to agent updates after connection
        socket.emit('subscribe_agents');
    });

    // Handle disconnection
    socket.on('disconnect', (reason) => {
        console.log('[SocketIO] Disconnected from server:', reason);
        showStatus('disconnected');
        showErrorNotification('已断开连接', reconnectAttempts);
    });

    // Handle connection error
    socket.on('connect_error', (error) => {
        console.error('[SocketIO] Connection error:', error);
        showStatus('error');
        showErrorNotification('连接失败：' + error.message, reconnectAttempts);
    });

    // Handle reconnection attempt
    socket.on('reconnect_attempt', (attemptNumber) => {
        reconnectAttempts = attemptNumber;
        const delay = calculateReconnectDelay(attemptNumber);
        console.log(`[SocketIO] Reconnection attempt ${attemptNumber}, next in ${Math.round(delay)}ms`);
        showStatus('reconnecting');
    });

    // Handle successful reconnection
    socket.on('reconnect', (attemptNumber) => {
        console.log(`[SocketIO] Reconnected after ${attemptNumber} attempts`);
        reconnectAttempts = 0;
        showStatus('connected');
        
        // Resubscribe to updates
        socket.emit('subscribe_agents');
    });

    // Handle reconnection failure (max attempts exceeded)
    socket.on('reconnect_failed', () => {
        console.error('[SocketIO] Reconnection failed after max attempts');
        showStatus('error');
        showErrorNotification('重连失败，请刷新页面', reconnectAttempts);
    });

    // Handle agent updates from server
    socket.on('agents_update', (data) => {
        console.log('[SocketIO] Agents updated:', data.agents);
        updateAgentsUI(data.agents);
    });
}

/**
 * Update socket status indicator in the UI.
 * 
 * Changes the visual state of the connection indicator based on
 * the current socket connection status.
 * 
 * @param {string} status - Connection status: 'connected', 'disconnected', 'reconnecting', or 'error'
 */
function showStatus(status) {
    const statusEl = document.getElementById('socket-status');
    if (statusEl) {
        statusEl.className = `socket-status status-${status}`;
        
        // Status text mapping
        const statusTexts = {
            'connected': '● 在线',
            'disconnected': '○ 离线',
            'reconnecting': '⟳ 重连中',
            'error': '⚠ 错误'
        };
        
        statusEl.textContent = statusTexts[status] || '○ 离线';
    }
}

/**
 * Update the agent list display in the UI.
 * 
 * Renders all agents by clearing the container and creating
 * new agent cards for each agent in the list.
 * 
 * @param {Array} agents - Array of agent objects with properties:
 *   - agentId: string
 *   - name: string
 *   - state: string
 *   - detail: string
 *   - avatar_url: string (optional)
 *   - pixel_character: string (optional)
 */
function updateAgentsUI(agents) {
    const agentContainer = document.getElementById('agent-container');
    if (!agentContainer) return;

    // Clear existing agents
    agentContainer.innerHTML = '';

    // Render each agent
    agents.forEach(agent => {
        const agentEl = createAgentElement(agent);
        agentContainer.appendChild(agentEl);
    });
}

/**
 * Create a DOM element representing a single agent card.
 * 
 * Builds a complete agent card with state badge, name, detail,
 * and optional avatar/pixel character images.
 * 
 * @param {Object} agent - Agent object containing:
 *   - agentId: string - Unique identifier
 *   - name: string - Display name
 *   - state: string - Current state for badge styling
 *   - detail: string - Additional information
 *   - avatar_url: string (optional) - Avatar image URL
 *   - pixel_character: string (optional) - Pixel art character filename
 * @returns {HTMLDivElement} Configured agent card element
 */
function createAgentElement(agent) {
    const div = document.createElement('div');
    div.className = 'agent-card';
    div.dataset.agentId = agent.agentId;

    // State badge
    const stateBadge = document.createElement('span');
    stateBadge.className = `state-badge state-${agent.state}`;
    stateBadge.textContent = agent.state;

    // Name
    const nameEl = document.createElement('h3');
    nameEl.className = 'agent-name';
    nameEl.textContent = agent.name;

    // Detail
    const detailEl = document.createElement('p');
    detailEl.className = 'agent-detail';
    detailEl.textContent = agent.detail || '待命中';

    // Avatar (if available)
    if (agent.avatar_url) {
        const img = document.createElement('img');
        img.src = agent.avatar_url;
        img.className = 'agent-avatar';
        img.alt = agent.name;
        div.appendChild(img);
    }

    // Pixel character (if available)
    if (agent.pixel_character) {
        const pixelImg = document.createElement('img');
        pixelImg.src = `/static/pixels/${agent.pixel_character}`;
        pixelImg.className = 'pixel-character';
        pixelImg.alt = 'Pixel Character';
        div.appendChild(pixelImg);
    }

    div.appendChild(stateBadge);
    div.appendChild(nameEl);
    div.appendChild(detailEl);

    return div;
}

/**
 * Export public API for external modules.
 * 
 * @property {Function} initSocket - Initialize SocketIO connection
 * @property {Function} showStatus - Update status indicator
 * @property {Function} updateAgentsUI - Update agent display
 */

// Initialize on page load
if (typeof io !== 'undefined') {
    document.addEventListener('DOMContentLoaded', initSocket);
}
