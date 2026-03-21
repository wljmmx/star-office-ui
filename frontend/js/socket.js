/**
 * SocketIO client for real-time agent updates
 */

let socket = null;

function initSocket() {
    // Connect to SocketIO server
    socket = io({
        transports: ['websocket', 'polling'],
        upgrade: false
    });

    // Handle connection
    socket.on('connect', () => {
        console.log('[SocketIO] Connected to server');
        showStatus('connected');
    });

    // Handle disconnection
    socket.on('disconnect', () => {
        console.log('[SocketIO] Disconnected from server');
        showStatus('disconnected');
    });

    // Handle connection error
    socket.on('connect_error', (error) => {
        console.error('[SocketIO] Connection error:', error);
        showStatus('error');
    });

    // Handle agent updates
    socket.on('agents_update', (data) => {
        console.log('[SocketIO] Agents updated:', data.agents);
        updateAgentsUI(data.agents);
    });

    // Subscribe to agent updates
    socket.emit('subscribe_agents');
}

function showStatus(status) {
    const statusEl = document.getElementById('socket-status');
    if (statusEl) {
        statusEl.className = `socket-status status-${status}`;
        statusEl.textContent = status === 'connected' ? '● 在线' : '○ 离线';
    }
}

function updateAgentsUI(agents) {
    // Update agent list in UI
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

// Initialize on page load
if (typeof io !== 'undefined') {
    document.addEventListener('DOMContentLoaded', initSocket);
}
