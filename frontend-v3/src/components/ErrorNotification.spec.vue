import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ErrorNotification from './ErrorNotification.vue'

describe('ErrorNotification', () => {
  it('should render error message', () => {
    const wrapper = mount(ErrorNotification, {
      props: { message: 'Test Error' }
    })
    expect(wrapper.text()).toContain('Test Error')
  })

  it('should show reconnection attempt info', () => {
    const wrapper = mount(ErrorNotification, {
      props: { message: 'Test Error', attempt: 2 }
    })
    expect(wrapper.text()).toContain('第 3 次尝试')
  })

  it('should emit close event when close button clicked', async () => {
    const wrapper = mount(ErrorNotification, {
      props: { message: 'Test Error' }
    })
    await wrapper.find('.notification-close').trigger('click')
    expect(wrapper.emitted('close')).toBeTruthy()
  })

  it('should have error-notification class', () => {
    const wrapper = mount(ErrorNotification, {
      props: { message: 'Test Error' }
    })
    expect(wrapper.find('.error-notification').exists()).toBe(true)
  })

  it('should have slide-in animation class', () => {
    const wrapper = mount(ErrorNotification, {
      props: { message: 'Test Error' }
    })
    expect(wrapper.classes()).toContain('slide-in')
  })

  it('should have notification icon', () => {
    const wrapper = mount(ErrorNotification, {
      props: { message: 'Test Error' }
    })
    expect(wrapper.find('.notification-icon').exists()).toBe(true)
  })
})
