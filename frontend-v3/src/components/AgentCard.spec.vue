import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AgentCard from './AgentCard.vue'

describe('AgentCard', () => {
  const mockAgent = {
    agentId: 'test-agent-1',
    name: 'Test Agent',
    role: 'Developer',
    state: 'idle',
    task_title: 'Testing',
    task_progress: 50,
    updated_at: new Date().toISOString(),
    avatar_url: 'https://example.com/avatar.png'
  }

  it('should render agent name', () => {
    const wrapper = mount(AgentCard, {
      props: { agent: mockAgent }
    })
    expect(wrapper.text()).toContain('Test Agent')
  })

  it('should render agent role', () => {
    const wrapper = mount(AgentCard, {
      props: { agent: mockAgent }
    })
    expect(wrapper.text()).toContain('Developer')
  })

  it('should render agent state', () => {
    const wrapper = mount(AgentCard, {
      props: { agent: mockAgent }
    })
    expect(wrapper.text()).toContain('idle')
  })

  it('should have correct state class', () => {
    const wrapper = mount(AgentCard, {
      props: { agent: mockAgent }
    })
    expect(wrapper.find('.agent-state').classes()).toContain('state-idle')
  })

  it('should render task info when task exists', () => {
    const wrapper = mount(AgentCard, {
      props: { agent: mockAgent }
    })
    expect(wrapper.find('.task-title').exists()).toBe(true)
    expect(wrapper.text()).toContain('Testing')
  })

  it('should render progress bar', () => {
    const wrapper = mount(AgentCard, {
      props: { agent: mockAgent }
    })
    const progressBar = wrapper.find('.progress-fill')
    expect(progressBar.exists()).toBe(true)
    expect(progressBar.element.style.width).toBe('50%')
  })

  it('should use default avatar when avatar_url is not provided', () => {
    const agentWithoutAvatar = { ...mockAgent, avatar_url: undefined }
    const wrapper = mount(AgentCard, {
      props: { agent: agentWithoutAvatar }
    })
    const img = wrapper.find('.agent-avatar')
    expect(img.attributes('src')).toContain('dicebear')
  })
})
