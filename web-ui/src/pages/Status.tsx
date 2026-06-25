import { useEffect, useState } from 'react'
import axios from 'axios'

interface ServiceStatus {
  name: string
  status: 'healthy' | 'unhealthy' | 'unknown'
  port?: number
  url?: string
  responseTime?: number
  details?: string
}

const Status: React.FC = () => {
  const [services, setServices] = useState<ServiceStatus[]>([
    { name: 'Backend API', status: 'unknown', port: 8000, url: 'http://localhost:8000/health' },
    { name: 'Web UI', status: 'unknown', port: 3000, url: 'http://localhost:3000' },
    { name: 'Vector Database', status: 'unknown', port: 5432 },
    { name: 'MCP Server', status: 'unknown', port: 8001, url: 'http://backend:8001/health' },
    { name: 'Network Scanner', status: 'unknown' },
  ])

  const [lastChecked, setLastChecked] = useState<Date>(new Date())
  const [overallStatus, setOverallStatus] = useState<'operational' | 'degraded' | 'down'>('unknown')

  useEffect(() => {
    checkAllServices()
    const interval = setInterval(checkAllServices, 30000) // Check every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const checkAllServices = async () => {
    const updatedServices = await Promise.all(services.map(async (service) => {
      if (!service.url) {
        // For services without HTTP endpoints, assume operational if we can't check
        return { ...service, status: 'unknown' as const, details: 'No health endpoint' }
      }

      const startTime = Date.now()
      try {
        const response = await axios.get(service.url, { timeout: 5000 })
        const responseTime = Date.now() - startTime
        
        if (response.status === 200) {
          return { 
            ...service, 
            status: 'healthy' as const, 
            responseTime,
            details: `Response: ${responseTime}ms`
          }
        } else {
          return { 
            ...service, 
            status: 'unhealthy' as const, 
            details: `HTTP ${response.status}`
          }
        }
      } catch (error: any) {
        return { 
          ...service, 
          status: 'unhealthy' as const, 
          details: error.code === 'ECONNREFUSED' 
            ? 'Connection refused' 
            : error.code === 'ECONNABORTED'
            ? 'Timeout'
            : 'Unreachable'
        }
      }
    }))

    setServices(updatedServices)
    setLastChecked(new Date())

    // Calculate overall status
    const healthyCount = updatedServices.filter(s => s.status === 'healthy').length
    const unhealthyCount = updatedServices.filter(s => s.status === 'unhealthy').length
    
    if (unhealthyCount === 0) {
      setOverallStatus('operational')
    } else if (healthyCount > 0) {
      setOverallStatus('degraded')
    } else {
      setOverallStatus('down')
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return '#22c55e'
      case 'unhealthy': return '#ef4444'
      default: return '#6b7280'
    }
  }

  const getOverallStatusColor = () => {
    switch (overallStatus) {
      case 'operational': return '#22c55e'
      case 'degraded': return '#f59e0b'
      case 'down': return '#ef4444'
      default: return '#6b7280'
    }
  }

  return (
    <div className="status-page">
      <div className="status-header">
        <h1>System Status</h1>
        <div className={`overall-status-badge ${overallStatus}`}>
          <span 
            className="status-indicator" 
            style={{ backgroundColor: getOverallStatusColor() }}
          />
          {overallStatus === 'operational' ? 'All Systems Operational' : 
           overallStatus === 'degraded' ? 'Partial System Degradation' : 
           'System Down'}
        </div>
        <p className="last-checked">
          Last checked: {lastChecked.toLocaleTimeString()}
          <button onClick={checkAllServices} className="refresh-btn">
            Refresh
          </button>
        </p>
      </div>

      <div className="services-grid">
        {services.map((service) => (
          <div key={service.name} className="service-card">
            <div className="service-header">
              <h3>{service.name}</h3>
              <span 
                className="service-status" 
                style={{ color: getStatusColor(service.status) }}
              >
                {service.status === 'healthy' ? '●' : 
                 service.status === 'unhealthy' ? '●' : '●'}
              </span>
            </div>
            
            {service.port && (
              <div className="service-detail">
                <strong>Port:</strong> {service.port}
              </div>
            )}
            
            {service.url && (
              <div className="service-detail">
                <strong>Endpoint:</strong> {service.url}
              </div>
            )}
            
            {service.responseTime && (
              <div className="service-detail">
                <strong>Response Time:</strong> {service.responseTime}ms
              </div>
            )}
            
            {service.details && (
              <div className="service-detail">
                <strong>Status:</strong> {service.details}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="status-footer">
        <p>Sentinel Prime Network Security Monitoring System</p>
        <p>Auto-refresh every 30 seconds</p>
      </div>
    </div>
  )
}

export default Status