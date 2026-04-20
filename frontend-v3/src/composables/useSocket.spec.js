import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref } from 'vue'
import { useSocket } from './useSocket'

// Mock socket.io-client
vi.mock('socket.io-client', () => {
  return {
    default: vi.fn(() => ({
      on: vi.fn(),
      emit: vi.fn(),
      disconnect: vi.fn()
    }))
  }
})

describe('useSocket', () => {
  let socketResult

  beforeEach(() => {
    socketResult = useSocket()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('should initialize with empty agents array', () => {
    expect(socketResult.agents.value).toEqual([])
  })

  it('should initialize with loading true', () => {
    expect(socketResult.loading.value).toBe(true)
  })

  it('should initialize with isConnected false', () => {
    expect(socketResult.isConnected.value).toBe(false)
  })

  it('should initialize with error null', () => {
    expect(socketResult.error.value).toBe(null)
  })

  it('should have connect method', () => {
    expect(typeof socketResult.connect).toBe('function')
  })

  it('should have clearError method', () => {
    expect(typeof socketResult.clearError).toBe('function')
  })

  it('should have fetchAgents method', () => {
    expect(typeof socketResult.fetchAgents).toBe('function')
  })

  it('should have updateStatus method', () => {
    expect(typeof socketResult.updateStatus).toBe('function')
  })

  it('clearError should set error to null', () => {
    socketResult.error.value = { message: 'test error' }
    socketResult.clearError()
    expect(socketResult.error.value).toBe(null)
  })

  it('updateStatus should return correct status text', () => {
    expect(socketResult.updateStatus('connected')).toBe('● 在线')
    expect(socketResult.updateStatus('disconnected')).toBe('○ 离线')
    expect(socketResult.updateStatus('reconnecting')).toBe('⟳ 重连中')
    expect(socketResult.updateStatus('error')).toBe('⚠ 错误')
  })
})
