import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SocketStatus from './SocketStatus.vue'

describe('SocketStatus', () => {
  it('should render socket status component', () => {
    const wrapper = mount(SocketStatus)
    expect(wrapper.exists()).toBe(true)
  })

  it('should have socket-status class', () => {
    const wrapper = mount(SocketStatus)
    expect(wrapper.find('.socket-status').exists()).toBe(true)
  })

  it('should show disconnected status by default', () => {
    const wrapper = mount(SocketStatus)
    expect(wrapper.classes()).toContain('status-disconnected')
  })

  it('should have status indicator', () => {
    const wrapper = mount(SocketStatus)
    expect(wrapper.find('.status-indicator').exists()).toBe(true)
  })

  it('should render status text', () => {
    const wrapper = mount(SocketStatus)
    expect(wrapper.text()).toContain('离线')
  })
})
