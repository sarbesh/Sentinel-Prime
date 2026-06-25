import { useEffect, useRef, useCallback, useState } from 'react'

interface WebSocketMessage {
  type: string
  scan_id?: number
  progress?: number
  status?: string
  details?: string
  results?: any
  alert?: any
  threat?: any
  timestamp?: string
}

interface UseWebSocketOptions {
  autoReconnect?: boolean
  reconnectInterval?: number
  onMessage?: (data: WebSocketMessage) => void
  onError?: (error: Event) => void
  onOpen?: () => void
  onClose?: () => void
}

export function useWebSocket(options: UseWebSocketOptions = {}) {
  const {
    autoReconnect = true,
    reconnectInterval = 3000,
    onMessage,
    onError,
    onOpen,
    onClose
  } = options

  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>()

  const connect = useCallback(() => {
    const wsUrl = `ws://localhost:8000/ws`
    
    try {
      const ws = new WebSocket(wsUrl)
      
      ws.onopen = () => {
        console.log('✅ WebSocket connected')
        setIsConnected(true)
        onOpen?.()
      }

      ws.onmessage = (event) => {
        try {
          const data: WebSocketMessage = JSON.parse(event.data)
          console.log('📨 WebSocket message:', data)
          setLastMessage(data)
          onMessage?.(data)
        } catch (error) {
          console.error('❌ Failed to parse WebSocket message:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error)
        onError?.(error)
      }

      ws.onclose = () => {
        console.log('🔌 WebSocket disconnected')
        setIsConnected(false)
        onClose?.()
        
        if (autoReconnect) {
          console.log(`🔄 Reconnecting in ${reconnectInterval / 1000}s...`)
          reconnectTimeoutRef.current = setTimeout(connect, reconnectInterval)
        }
      }

      wsRef.current = ws
    } catch (error) {
      console.error('❌ Failed to create WebSocket:', error)
      onError?.(error as Event)
      
      if (autoReconnect) {
        reconnectTimeoutRef.current = setTimeout(connect, reconnectInterval)
      }
    }
  }, [autoReconnect, reconnectInterval, onMessage, onError, onOpen, onClose])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    
    setIsConnected(false)
  }, [])

  const subscribeToScan = useCallback((scanId: number) => {
    if (wsRef.current && isConnected) {
      wsRef.current.send(JSON.stringify({
        type: 'subscribe_scan',
        scan_id: scanId
      }))
      console.log(`📡 Subscribed to scan ${scanId}`)
    }
  }, [isConnected])

  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (wsRef.current && isConnected) {
      wsRef.current.send(JSON.stringify(message))
    }
  }, [isConnected])

  useEffect(() => {
    connect()
    
    return () => {
      disconnect()
    }
  }, [connect, disconnect])

  return {
    isConnected,
    lastMessage,
    subscribeToScan,
    sendMessage,
    disconnect
  }
}

// Specialized hook for scan progress
export function useScanProgress(scanId?: number) {
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState('')
  const [details, setDetails] = useState('')
  const [isComplete, setIsComplete] = useState(false)
  const [results, setResults] = useState<any>(null)

  const handleScanMessage = useCallback((message: WebSocketMessage) => {
    if (message.scan_id !== scanId) return

    switch (message.type) {
      case 'scan_progress':
        setProgress(message.progress || 0)
        setStatus(message.status || '')
        setDetails(message.details || '')
        break
      
      case 'scan_complete':
        setProgress(100)
        setStatus('completed')
        setIsComplete(true)
        setResults(message.results)
        break
      
      case 'scan_finished':
        // Broadcast to all clients
        setIsComplete(true)
        break
    }
  }, [scanId])

  const { isConnected, subscribeToScan } = useWebSocket({
    onMessage: handleScanMessage,
    autoReconnect: true
  })

  useEffect(() => {
    if (scanId && isConnected) {
      subscribeToScan(scanId)
    }
  }, [scanId, isConnected, subscribeToScan])

  return {
    isConnected,
    progress,
    status,
    details,
    isComplete,
    results
  }
}

// Specialized hook for security alerts
export function useSecurityAlerts() {
  const [alerts, setAlerts] = useState<any[]>([])
  const [threats, setThreats] = useState<any[]>([])

  const handleMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'security_alert':
        if (message.alert) {
          setAlerts(prev => [message.alert!, ...prev].slice(0, 50)) // Keep last 50
        }
        break
      
      case 'threat_detected':
        if (message.threat) {
          setThreats(prev => [message.threat!, ...prev].slice(0, 20)) // Keep last 20
        }
        break
    }
  }, [])

  const { isConnected } = useWebSocket({
    onMessage: handleMessage,
    autoReconnect: true
  })

  return {
    isConnected,
    alerts,
    threats,
    alertCount: alerts.length,
    threatCount: threats.length
  }
}

export default useWebSocket