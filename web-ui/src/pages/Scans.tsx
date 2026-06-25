import { useEffect, useState } from 'react'
import axios from 'axios'
import { useScanProgress } from '../hooks/useWebSocket'

const API_URL = 'http://localhost:8000'

const Scans = () => {
  const [scans, setScans] = useState([])
  const [loading, setLoading] = useState(true)
  const [scanning, setScanning] = useState(false)
  const [scanTarget, setScanTarget] = useState('192.168.0.1/24')
  const [scanType, setScanType] = useState('ping')
  const [activeScanId, setActiveScanId] = useState<number | null>(null)
  
  const { isConnected, progress, status, details, isComplete, results } = useScanProgress(activeScanId || undefined)

  useEffect(() => { fetchScans() }, [])

  const fetchScans = async () => {
    try {
      const res = await axios.get(`${API_URL}/scans`)
      setScans(res.data)
    } catch (error) { console.error('Failed to fetch scans:', error) }
    finally { setLoading(false) }
  }

  const handleNewScan = async (e: any) => {
    e.preventDefault()
    setScanning(true)
    try {
      const response = await axios.post(`${API_URL}/scans/network`, { target: scanTarget, scan_type: scanType })
      const newScan = response.data
      if (newScan.id) { setActiveScanId(newScan.id) }
    } catch (error: any) {
      console.error('Failed to create scan:', error)
      alert('Failed to create scan. Please try again.')
    } finally { setScanning(false) }
  }

  const getStatusColor = (status: string) => {
    switch(status?.toLowerCase()) {
      case 'completed': return 'success'
      case 'running': return 'info'
      case 'failed': return 'danger'
      default: return 'info'
    }
  }

  return (
    <div className="scans-page">
      <div className="table-header" style={{ marginBottom: '2rem' }}>
        <h1>Network Scans</h1>
        <button onClick={() => document.getElementById('scanForm')?.scrollIntoView({ behavior: 'smooth' })} className="btn btn-primary">+ New Scan</button>
      </div>

      <div id="scanForm" className="table-container" style={{ marginBottom: '2rem' }}>
        <div className="table-header"><h2>Create New Scan</h2></div>
        
        {isConnected && activeScanId && (
          <div style={{ padding: '1rem', background: 'rgba(14, 165, 233, 0.1)', borderBottom: '1px solid rgba(14, 165, 233, 0.3)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '0.875rem', color: 'var(--cyan)' }}>📡 Scan #{activeScanId}: {status || 'Scanning...'}</div>
                <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.1)', borderRadius: '3px', marginTop: '0.5rem' }}>
                  <div style={{ width: `${progress}%`, height: '100%', background: 'linear-gradient(90deg, var(--cyan), var(--blue))' }} />
                </div>
              </div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--cyan)' }}>{Math.round(progress)}%</div>
            </div>
          </div>
        )}
        
        <form onSubmit={handleNewScan} style={{ padding: '2rem', display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: '1rem' }}>
          <input type="text" value={scanTarget} onChange={(e) => setScanTarget(e.target.value)} placeholder="192.168.0.1/24" style={{ padding: '0.75rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.2)', borderRadius: '0.5rem', color: 'white' }} required />
          <select value={scanType} onChange={(e) => setScanType(e.target.value)} style={{ padding: '0.75rem', background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.2)', borderRadius: '0.5rem', color: 'white' }}>
            <option value="ping">Ping Scan</option><option value="quick">Quick Scan</option><option value="deep">Deep Scan</option>
          </select>
          <button type="submit" className="btn btn-primary" disabled={scanning}>{scanning ? 'Scanning...' : 'Start Scan'}</button>
        </form>
      </div>

      <div className="table-container">
        <div className="table-header"><h2>Scan History</h2></div>
        {loading ? <div>Loading...</div> : scans.length === 0 ? <div>No scans yet</div> : (
          <table>
            <thead><tr><th>ID</th><th>Target</th><th>Type</th><th>Status</th><th>Hosts</th><th>Started</th></tr></thead>
            <tbody>
              {scans.map((scan: any) => (
                <tr key={scan.id}>
                  <td>#{scan.id}</td><td>{scan.target}</td><td><span className="badge info">{scan.scan_type}</span></td>
                  <td><span className={`badge ${getStatusColor(scan.status)}`}>{scan.status}</span></td>
                  <td>{scan.hosts_discovered || '-'}</td><td>{new Date(scan.started_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}

export default Scans
