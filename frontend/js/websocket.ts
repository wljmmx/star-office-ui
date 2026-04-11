/**
 * Star Office UI - WebSocket Event Handlers
 * Real-time synchronization with backend
 */

import { Agent, Task, Environment, AgentUpdateEvent, TaskUpdateEvent, EnvironmentUpdateEvent } from './types';

// ==================== Event Handler Registry ====================

interface EventHandler<T = any> {
  (data: T): void;
}

class EventRegistry {
  private handlers: Map<string, Set<EventHandler>> = new Map();

  on<T = any>(event: string, handler: EventHandler<T>): void {
    if (!this.handlers.has(event)) {
      this.handlers.set(event, new Set());
    }
    this.handlers.get(event)!.add(handler as EventHandler);
  }

  off<T = any>(event: string, handler: EventHandler<T>): void {
    const handlers = this.handlers.get(event);
    if (handlers) {
      handlers.delete(handler as EventHandler);
    }
  }

  emit<T = any>(event: string, data: T): void {
    const handlers = this.handlers.get(event);
    if (handlers) {
      handlers.forEach(handler => handler(data));
    }
  }

  clear(): void {
    this.handlers.clear();
  }
}

export const eventRegistry = new EventRegistry();

// ==================== WebSocket Connection ====================

let socket: any = null;
let isConnected = false;

function connectSocket(): void {
  // Use io() for Socket.IO client
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const socketUrl = `${protocol}//${window.location.host}`;

  console.log('[WebSocket] Connecting to:', socketUrl);

  socket = io(socketUrl, {
    transports: ['websocket', 'polling'],
    reconnection: true,
    reconnectionDelay: 1000,
    reconnectionAttempts: 5,
  });

  socket.on('connect', () => {
    console.log('[WebSocket] Connected');
    isConnected = true;
    eventRegistry.emit('connected', {});
    
    // Subscribe to updates
    socket.emit('subscribe_agents');
  });

  socket.on('disconnect', () => {
    console.log('[WebSocket] Disconnected');
    isConnected = false;
    eventRegistry.emit('disconnected', {});
  });

  socket.on('connect_error', (error: any) => {
    console.error('[WebSocket] Connection error:', error);
    eventRegistry.emit('error', { type: 'connection', error: error.message });
  });

  // ==================== Agent Events ====================

  socket.on('agent_update', (data: any) => {
    console.log('[WebSocket] Agent updated:', data);
    eventRegistry.emit('agent_update', data);
  });

  socket.on('agents_sync', (data: any) => {
    console.log('[WebSocket] Agents synced:', data.agents.length, 'agents');
    eventRegistry.emit('agents_sync', data);
  });

  // ==================== Avatar Events ====================

  socket.on('avatar_update', (data: any) => {
    console.log('[WebSocket] Avatar updated:', data);
    eventRegistry.emit('avatar_update', data);
  });

  // ==================== Task Events ====================

  socket.on('task_update', (data: any) => {
    console.log('[WebSocket] Task updated:', data);
    eventRegistry.emit('task_update', data);
  });

  socket.on('task_list_update', (data: any) => {
    console.log('[WebSocket] Task list updated:', data);
    eventRegistry.emit('task_list_update', data);
  });

  // ==================== Environment Events ====================

  socket.on('environment_update', (data: any) => {
    console.log('[WebSocket] Environment updated:', data);
    eventRegistry.emit('environment_update', data);
  });

  // ==================== Desk Events ====================

  socket.on('desk_update', (data: any) => {
    console.log('[WebSocket] Desk updated:', data);
    eventRegistry.emit('desk_update', data);
  });

  // ==================== General Events ====================

  socket.on('state_update', (data: any) => {
    console.log('[WebSocket] State updated:', data);
    eventRegistry.emit('state_update', data);
  });
}

function disconnectSocket(): void {
  if (socket) {
    socket.disconnect();
    socket = null;
    isConnected = false;
    console.log('[WebSocket] Disconnected manually');
  }
}

function subscribe(): void {
  if (socket && isConnected) {
    socket.emit('subscribe_agents');
  }
}

// ==================== Event Helper Functions ====================

export function onAgentUpdate(handler: EventHandler<any>): void {
  eventRegistry.on('agent_update', handler);
}

export function onAgentsSync(handler: EventHandler<any>): void {
  eventRegistry.on('agents_sync', handler);
}

export function onAvatarUpdate(handler: EventHandler<any>): void {
  eventRegistry.on('avatar_update', handler);
}

export function onTaskUpdate(handler: EventHandler<any>): void {
  eventRegistry.on('task_update', handler);
}

export function onTaskListUpdate(handler: EventHandler<any>): void {
  eventRegistry.on('task_list_update', handler);
}

export function onEnvironmentUpdate(handler: EventHandler<any>): void {
  eventRegistry.on('environment_update', handler);
}

export function onDeskUpdate(handler: EventHandler<any>): void {
  eventRegistry.on('desk_update', handler);
}

export function onStateUpdate(handler: EventHandler<any>): void {
  eventRegistry.on('state_update', handler);
}

export function onConnected(handler: EventHandler): void {
  eventRegistry.on('connected', handler);
}

export function onDisconnected(handler: EventHandler): void {
  eventRegistry.on('disconnected', handler);
}

// ==================== Export WebSocket Control ====================

export const websocket = {
  connect: connectSocket,
  disconnect: disconnectSocket,
  subscribe: subscribe,
  isConnected: () => isConnected,
  send: (event: string, data: any) => {
    if (socket && isConnected) {
      socket.emit(event, data);
    }
  },
};
