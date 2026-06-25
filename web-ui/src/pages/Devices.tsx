import { useEffect, useState } from 'react'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

const Devices = () => {
  const [devices, setDevices] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    const fetchDevices = async () => {
      try {
        const res = await axios.get(`${API_URL}/devices`)
        setDevices(res.data)
      } catch (error) {
        console.error('Failed to fetch devices:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchDevices()
  }, [])

  const filteredDevices = devices.filter(device => {
    if (filter === 'all') return true
    return device.status === filter
  })

  const getStatusColor = (status) => {
    return status === 'online' ? 'success' : 'danger'
  }

  return (
    <div className="devices-page">
      <div className="table-header" style={{ marginBottom: '2rem', animation: 'slideInLeft 0.5s ease-out' }}>
        <h1>Network Devices</h1>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <select 
            value={filter} 
            onChange={(e) => setFilter(e.target.value)}
            className="btn btn-secondary btn-sm"
            style={{ background: 'rgba(255,255,255,0.1)', color: 'white', border: '1px solid rgba(255,255,255,0.2)', padding: '0.5rem 1rem', borderRadius: '0.5rem', cursor: 'pointer' }}
          >
            <option value="all">All Devices</option>
            <option value="online">Online</option>
            <option value="offline">Offline</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading" style={{ margin: '4rem auto', display: 'block' }}></div>
      ) : filteredDevices.length > 0 ? (
        <div className="table-container" style={{ animation: 'slideUp 0.6s ease-out 0.2s both' }}>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>IP Address</th>
                <th>MAC Address</th>
                <th>Type</th>
                <th>Vendor</th>
                <th>Status</th>
                <th>Last Seen</th>
              </tr>
            </thead>
            <tbody>
              {filteredDevices.map((device) => (
                <tr key={device.id} style={{ animation: 'fadeIn 0.3s ease-out' }}>
                  <td>#{device.id}</td>
                  <td style={{ fontWeight: '600' }}>{device.name || 'Unknown'}</td>
                  <td style={{ fontFamily: 'monospace', color: 'var(--primary-light)' }}>
                    {device.ip_address}
                  </td>
                  <td style={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>
                    {device.mac_address || 'N/A'}
                  </td>
                  <td>{device.type || 'Unknown'}</td>
                  <td>{device.vendor || 'Unknown'}</td>
                  <td>
                    <span className={`badge ${getStatusColor(device.status)}`}>
                      {device.status}
                    </span>
                  </td>
                  <td style={{ fontSize: '0.875rem', color: 'var(--gray-light)' }}>
                    {new Date(device.last_seen).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty-state" style={{ animation: 'fadeIn 0.5s ease-out' }}>
          <div className="empty-state-icon">🔍</div>
          <h3>No devices found</h3>
          <p>Run a network scan to discover devices</p>
        </div>
      )}
    </div>
  )
}

export default Devices