import { useEffect, useState } from 'react'
import axios from 'axios'

const AlertsTable: React.FC = () => {
  const [alerts, setAlerts] = useState<Array<any>>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchAlerts = async () => {
      setLoading(true)
      try {
        const res = await axios.get('http://localhost:8000/alerts')
        setAlerts(res.data)
      } catch (error) {
        console.error('Failed to fetch alerts:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchAlerts()
  }, [])

  if (loading) return <p>Loading alerts...</p>

  return (
    <div>
      <h2>Alerts</h2>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Severity</th>
            <th>Source</th>
            <th>Time</th>
            <th>Acknowledged</th>
          </tr>
        </thead>
        <tbody>
          {alerts.map((alert: any, index: number) => (
            <tr key={alert.id || index}>
              <td>{alert.id}</td>
              <td>{alert.title}</td>
              <td>{alert.severity}</td>
              <td>{alert.source}</td>
              <td>{new Date(alert.timestamp || 0).toLocaleString()}</td>
              <td>{alert.acknowledged ? 'Yes' : 'No'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

const Alerts: React.FC = () => {
  return (
    <div className="alerts-page">
      <AlertsTable />
    </div>
  )
}

export default Alerts