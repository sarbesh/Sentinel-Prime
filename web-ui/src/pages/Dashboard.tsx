import { useEffect, useState } from 'react'
import axios from 'axios'
import { Link } from 'react-router-dom'

const API_URL = 'http://localhost:8000'

const Dashboard = () => {
  const [stats, setStats] = useState({
    devices: 0,
    scans: 0,
    alerts: 0,
    vulnerabilities: 0
  })
  const [loading, setLoading] = useState(true)
  const [recentScans, setRecentScans] = useState([])
  const [recentAlerts, setRecentAlerts] = useState([])

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true)
        const [devicesRes, scansRes, alertsRes, vulnsRes] = await Promise.all([
          axios.get(`${API_URL}/devices`),
          axios.get(`${API_URL}/scans`),
          axios.get(`${API_URL}/alerts`),
          axios.get(`${API_URL}/vulnerabilities`)
        ])
        
        setStats({
          devices: devicesRes.data.length,
          scans: scansRes.data.length,
          alerts: alertsRes.data.length,
          vulnerabilities: vulnsRes.data.length
        })
        
        setRecentScans(scansRes.data.slice(0, 5).map(scan => ({
          id: scan.id,
          target: scan.target,
          type: scan.scan_type,
          status: scan.status,
          completed: scan.completed_at
        })))
        
        setRecentAlerts(alertsRes.data.slice(0, 5).map(alert => ({
          id: alert.id,
          device: alert.device_id,
          severity: alert.severity || 'medium',
          message: alert.message || 'Security alert',
          timestamp: alert.created_at
        })))
      } catch (error) {
        console.error('Failed to fetch stats:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchStats()
  }, [])

  const getSeverityColor = (severity) => {
    switch(severity?.toLowerCase()) {
      case 'critical': return 'danger'
      case 'high': return 'danger'
      case 'medium': return 'warning'
      case 'low': return 'info'
      default: return 'info'
    }
  }

  const getStatusColor = (status) => {
    switch(status?.toLowerCase()) {
      case 'completed': return 'success'
      case 'running': return 'info'
      case 'failed': return 'danger'
      default: return 'info'
    }
  }

  if (loading) {
    return (
      <div className="dashboard">
        <h1>Dashboard</h1>
        <div className="loading" style={{ margin: '2rem auto', display: 'block' }}></div>
      </div>
    )
  }

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Devices</h3>
          <p>{stats.devices}</p>
          <Link to="/devices" className="btn btn-secondary btn-sm" style={{ marginTop: '1rem' }}>
            View Devices →
          </Link>
        </div>
        
        <div className="stat-card">
          <h3>Total Scans</h3>
          <p>{stats.scans}</p>
          <Link to="/scans" className="btn btn-secondary btn-sm" style={{ marginTop: '1rem' }}>
            View Scans →
          </Link>
        </div>
        
        <div className="stat-card">
          <h3>Active Alerts</h3>
          <p>{stats.alerts}</p>
          <Link to="/alerts" className="btn btn-secondary btn-sm" style={{ marginTop: '1rem' }}>
            View Alerts →
          </Link>
        </div>
        
        <div className="stat-card">
          <h3>Vulnerabilities</h3>
          <p>{stats.vulnerabilities}</p>
          <Link to="/vulnerabilities" className="btn btn-secondary btn-sm" style={{ marginTop: '1rem' }}>
            View Details →
          </Link>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))', gap: '2rem' }}>
        {/* Recent Scans */}
        <div className="table-container">
          <div className="table-header">
            <h2>Recent Scans</h2>
            <Link to="/scans" className="btn btn-primary btn-sm">View All</Link>
          </div>
          {recentScans.length > 0 ? (
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Target</th>
                  <th>Type</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {recentScans.map(scan => (
                  <tr key={scan.id}>
                    <td>#{scan.id}</td>
                    <td style={{ fontFamily: 'monospace' }}>{scan.target}</td>
                    <td>{scan.type}</td>
                    <td>
                      <span className={`badge ${getStatusColor(scan.status)}`}>
                        {scan.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon">📊</div>
              <h3>No scans yet</h3>
              <p>Start by creating your first network scan</p>
              <Link to="/scans" className="btn btn-primary" style={{ marginTop: '1rem' }}>
                Create Scan
              </Link>
            </div>
          )}
        </div>

        {/* Recent Alerts */}
        <div className="table-container">
          <div className="table-header">
            <h2>Recent Alerts</h2>
            <Link to="/alerts" className="btn btn-primary btn-sm">View All</Link>
          </div>
          {recentAlerts.length > 0 ? (
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Severity</th>
                  <th>Message</th>
                </tr>
              </thead>
              <tbody>
                {recentAlerts.map(alert => (
                  <tr key={alert.id}>
                    <td>#{alert.id}</td>
                    <td>
                      <span className={`badge ${getSeverityColor(alert.severity)}`}>
                        {alert.severity}
                      </span>
                    </td>
                    <td>{alert.message}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="empty-state">
              <div className="empty-state-icon">✅</div>
              <h3>All Clear!</h3>
              <p>No active security alerts</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Dashboard