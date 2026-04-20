import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TaskInfo from './TaskInfo.vue'

describe('TaskInfo', () => {
  it('should render task title', () => {
    const wrapper = mount(TaskInfo, {
      props: { title: 'Test Task' }
    })
    expect(wrapper.text()).toContain('Test Task')
  })

  it('should render progress percentage', () => {
    const wrapper = mount(TaskInfo, {
      props: { title: 'Test Task', progress: 75 }
    })
    expect(wrapper.text()).toContain('75%')
  })

  it('should default progress to 0', () => {
    const wrapper = mount(TaskInfo, {
      props: { title: 'Test Task' }
    })
    expect(wrapper.text()).toContain('0%')
  })

  it('should set progress bar width correctly', () => {
    const wrapper = mount(TaskInfo, {
      props: { title: 'Test Task', progress: 30 }
    })
    const progressBar = wrapper.find('.progress-fill')
    expect(progressBar.element.style.width).toBe('30%')
  })

  it('should have task-title class', () => {
    const wrapper = mount(TaskInfo, {
      props: { title: 'Test Task' }
    })
    expect(wrapper.find('.task-title').exists()).toBe(true)
  })

  it('should have progress-bar class', () => {
    const wrapper = mount(TaskInfo, {
      props: { title: 'Test Task' }
    })
    expect(wrapper.find('.progress-bar').exists()).toBe(true)
  })
})
