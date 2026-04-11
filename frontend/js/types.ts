/**
 * Star Office UI - TypeScript Type Definitions
 * Integration types for Avatar, Environment, and Task List systems
 */

// ==================== Avatar Types ====================

export interface AvatarConfig {
  avatar_type: string;  // pixel, emoji, image, 3d
  avatar_data?: string;
  pixel_character?: string;
  avatar_url?: string;
}

export interface DisplayAvatar {
  type: string;
  data: string | object | null;
}

// ==================== Environment Types ====================

export interface Environment {
  id: string;
  name: string;
  description: string;
  theme: string;
  background_image?: string;
  layout_config?: object;
  settings?: object;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ThemeConfig {
  primary_color: string;
  secondary_color: string;
  background_color: string;
  text_color: string;
}

export interface AgentDesk {
  id: string;
  agent_id: string;
  desk_number: number;
  position_x: number;
  position_y: number;
  assigned_at: string;
  agent_name?: string;
}

// ==================== Task List Types ====================

export interface TaskChecklistItem {
  id: string;
  title: string;
  completed: boolean;
  completed_at?: string;
  order: number;
}

export interface TaskList {
  id: string;
  name: string;
  description: string;
  color: string;
  icon: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ChecklistProgress {
  total: number;
  completed: number;
  percentage: number;
}

// ==================== Extended Agent Type ====================

export interface Agent {
  agentId: string;
  name: string;
  type: string;
  state: string;
  detail: string;
  area: string;
  capabilities: string;
  address: string;
  task_id?: string;
  task_name?: string;
  task_status?: string;
  updated_at: string;
  isMain: boolean;
  pixel_character?: string;
  avatar_url?: string;
  role: string;
  // New avatar fields
  avatar_type?: string;
  avatar_data?: string;
  // New desk field
  desk_number?: number;
}

// ==================== Extended Task Type ====================

export interface Task {
  taskId: string;
  name: string;
  description: string;
  status: string;
  project_id?: string;
  assigned_agent?: string;
  priority: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  // New task list fields
  list_id?: string;
  position: number;
  checklist?: TaskChecklistItem[];
  checklist_progress?: ChecklistProgress;
}

// ==================== API Response Types ====================

export interface ApiResponse<T> {
  ok: boolean;
  msg?: string;
  data?: T;
}

export interface AgentsResponse {
  ok: boolean;
  agents: Agent[];
}

export interface TasksResponse {
  ok: boolean;
  tasks: Task[];
}

export interface AvatarResponse {
  ok: boolean;
  agent_id: string;
  avatar: AvatarConfig;
  display: DisplayAvatar;
}

export interface EnvironmentsResponse {
  ok: boolean;
  environments: Environment[];
}

export interface DesksResponse {
  ok: boolean;
  desks: AgentDesk[];
}

export interface TaskListsResponse {
  ok: boolean;
  lists: TaskList[];
}

// ==================== WebSocket Event Types ====================

export interface WebSocketEvent {
  type: string;
  payload: object;
  timestamp: string;
}

export interface AgentUpdateEvent {
  type: 'agent_update';
  payload: {
    agent_id: string;
    state?: string;
    area?: string;
    avatar_type?: string;
    desk_number?: number;
  };
}

export interface TaskUpdateEvent {
  type: 'task_update';
  payload: {
    task_id: string;
    list_id?: string;
    position?: number;
    status?: string;
    checklist?: TaskChecklistItem[];
  };
}

export interface EnvironmentUpdateEvent {
  type: 'environment_update';
  payload: {
    environment_id: string;
    theme?: string;
    settings?: object;
  };
}

// ==================== State Management ====================

export interface AppState {
  agents: Map<string, Agent>;
  tasks: Map<string, Task>;
  environments: Map<string, Environment>;
  activeEnvironment: Environment | null;
  desks: Map<string, AgentDesk>;
  taskLists: TaskList[];
  lastSyncTime: string;
}

// ==================== Constants ====================

export const AGENT_STATES = [
  'idle',
  'writing',
  'researching',
  'executing',
  'syncing',
  'error'
] as const;

export const AVATAR_TYPES = [
  { id: 'pixel', name: '像素风格', description: '简单像素化角色' },
  { id: 'emoji', name: '表情符号', description: '使用 emoji 作为头像' },
  { id: 'image', name: '图片', description: '自定义图片头像' },
  { id: '3d', name: '3D 模型', description: '3D 角色模型' },
] as const;

export const DEFAULT_TASK_LISTS = [
  { id: 'backlog', name: '待办事项', color: '#6b7280', icon: '📋' },
  { id: 'in_progress', name: '进行中', color: '#3b82f6', icon: '🔄' },
  { id: 'review', name: '待审核', color: '#f59e0b', icon: '🔍' },
  { id: 'done', name: '已完成', color: '#10b981', icon: '✅' },
] as const;

export const THEMES = {
  default: {
    primary_color: '#3b82f6',
    secondary_color: '#10b981',
    background_color: '#f3f4f6',
    text_color: '#1f2937',
  },
  dark: {
    primary_color: '#60a5fa',
    secondary_color: '#34d399',
    background_color: '#1f2937',
    text_color: '#f9fafb',
  },
  cyberpunk: {
    primary_color: '#f472b6',
    secondary_color: '#22d3ee',
    background_color: '#0f172a',
    text_color: '#e2e8f0',
  },
} as const;

// ==================== API Endpoints ====================

export const API_ENDPOINTS = {
  // Existing endpoints
  agents: '/api/agents',
  tasks: '/api/tasks',
  state: '/api/state',
  assets: '/api/assets',
  config: '/api/config',
  
  // New avatar endpoints
  avatars: '/api/avatars',
  avatarByAgent: (agentId: string) => `/api/avatars/${agentId}`,
  generateAvatar: (agentId: string) => `/api/avatars/generate/${agentId}`,
  
  // New environment endpoints
  environments: '/api/environments',
  environmentById: (envId: string) => `/api/environments/${envId}`,
  activateEnvironment: (envId: string) => `/api/environments/${envId}/activate`,
  themes: '/api/environments/themes',
  
  // New desk endpoints
  desks: '/api/environments/desks',
  deskByAgent: (agentId: string) => `/api/environments/desks/${agentId}`,
  
  // New task list endpoints
  taskLists: '/api/tasks/lists',
  tasksByList: (listId: string) => `/api/tasks/list/${listId}`,
  tasksByAgent: (agentId: string) => `/api/tasks/agent/${agentId}`,
  taskById: (taskId: string) => `/api/tasks/${taskId}`,
} as const;
