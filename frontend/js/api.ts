/**
 * Star Office UI - API Service Layer
 * Handles all HTTP requests to backend API
 */

import { API_ENDPOINTS } from './types';

// ==================== Base API Functions ====================

async function request(endpoint: string, options: RequestInit = {}) {
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };

  const mergedHeaders = {
    ...defaultHeaders,
    ...(options.headers || {}),
  };

  try {
    const response = await fetch(endpoint, {
      ...options,
      headers: mergedHeaders,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.msg || `HTTP error ${response.status}`);
    }

    return data;
  } catch (error) {
    console.error(`API request failed: ${endpoint}`, error);
    throw error;
  }
}

// ==================== Agent APIs ====================

export const agentAPI = {
  getAll: async () => {
    const data = await request(API_ENDPOINTS.agents);
    return data.agents;
  },

  getById: async (agentId: string) => {
    const data = await request(`${API_ENDPOINTS.agents}/${agentId}`);
    return data.agent;
  },

  updateStatus: async (agentId: string, state: string) => {
    const data = await request(`${API_ENDPOINTS.agents}/${agentId}/status`, {
      method: 'POST',
      body: JSON.stringify({ state }),
    });
    return data;
  },
};

// ==================== Avatar APIs ====================

export const avatarAPI = {
  getAllTypes: async () => {
    const data = await request(API_ENDPOINTS.avatars);
    return {
      avatarTypes: data.avatar_types,
      defaultAvatars: data.default_avatars,
    };
  },

  getByAgent: async (agentId: string) => {
    const data = await request(API_ENDPOINTS.avatarByAgent(agentId));
    return {
      avatar: data.avatar,
      display: data.display,
    };
  },

  update: async (agentId: string, avatarData: object) => {
    const data = await request(API_ENDPOINTS.avatarByAgent(agentId), {
      method: 'PUT',
      body: JSON.stringify(avatarData),
    });
    return data;
  },

  generate: async (agentId: string) => {
    const data = await request(API_ENDPOINTS.generateAvatar(agentId), {
      method: 'POST',
    });
    return data.avatar;
  },
};

// ==================== Environment APIs ====================

export const environmentAPI = {
  getAll: async () => {
    const data = await request(API_ENDPOINTS.environments);
    return data.environments;
  },

  getById: async (envId: string) => {
    const data = await request(API_ENDPOINTS.environmentById(envId));
    return data.environment;
  },

  create: async (envData: object) => {
    const data = await request(API_ENDPOINTS.environments, {
      method: 'POST',
      body: JSON.stringify(envData),
    });
    return data.environment;
  },

  update: async (envId: string, envData: object) => {
    const data = await request(API_ENDPOINTS.environmentById(envId), {
      method: 'PUT',
      body: JSON.stringify(envData),
    });
    return data;
  },

  activate: async (envId: string) => {
    const data = await request(API_ENDPOINTS.activateEnvironment(envId), {
      method: 'POST',
    });
    return data;
  },

  getThemes: async () => {
    const data = await request(API_ENDPOINTS.themes);
    return data.themes;
  },
};

// ==================== Desk APIs ====================

export const deskAPI = {
  getAll: async () => {
    const data = await request(API_ENDPOINTS.desks);
    return data.desks;
  },

  assign: async (agentId: string, deskNumber: number) => {
    const data = await request(API_ENDPOINTS.deskByAgent(agentId), {
      method: 'POST',
      body: JSON.stringify({ desk_number: deskNumber }),
    });
    return data.desk;
  },

  unassign: async (agentId: string) => {
    const data = await request(API_ENDPOINTS.deskByAgent(agentId), {
      method: 'DELETE',
    });
    return data;
  },
};

// ==================== Task APIs ====================

export const taskAPI = {
  getAll: async () => {
    const data = await request(API_ENDPOINTS.tasks);
    return data.tasks;
  },

  getById: async (taskId: string) => {
    const data = await request(API_ENDPOINTS.taskById(taskId));
    return data.task;
  },

  getByAgent: async (agentId: string) => {
    const data = await request(API_ENDPOINTS.tasksByAgent(agentId));
    return data.tasks;
  },

  getByList: async (listId: string) => {
    const data = await request(API_ENDPOINTS.tasksByList(listId));
    return data.tasks;
  },

  create: async (taskData: object) => {
    const data = await request(API_ENDPOINTS.tasks, {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
    return data.task;
  },

  update: async (taskId: string, taskData: object) => {
    const data = await request(API_ENDPOINTS.taskById(taskId), {
      method: 'PUT',
      body: JSON.stringify(taskData),
    });
    return data;
  },

  delete: async (taskId: string) => {
    const data = await request(API_ENDPOINTS.taskById(taskId), {
      method: 'DELETE',
    });
    return data;
  },

  completeChecklistItem: async (taskId: string, itemId: string) => {
    const data = await request(`${API_ENDPOINTS.taskById(taskId)}/checklist/${itemId}/complete`, {
      method: 'POST',
    });
    return data.checklist;
  },
};

// ==================== Task List APIs ====================

export const taskListAPI = {
  getAll: async () => {
    const data = await request(API_ENDPOINTS.taskLists);
    return data.lists;
  },
};

// ==================== State API ====================

export const stateAPI = {
  get: async () => {
    const data = await request(API_ENDPOINTS.state);
    return data;
  },
};

// ==================== Export all APIs ====================

export const api = {
  agents: agentAPI,
  avatars: avatarAPI,
  environments: environmentAPI,
  desks: deskAPI,
  tasks: taskAPI,
  taskLists: taskListAPI,
  state: stateAPI,
};
