import { useEffect, useState } from 'react'
import axios from 'axios'

const Settings: React.FC = () => {
  const [settings, setSettings] = useState<Array<any>>([])
  const [loading, setLoading] = useState(true)
  const [autoScan, setAutoScan] = useState(false)

  useEffect(() => {
    const fetchSettings = async () => {
      setLoading(true)
      try {
        const res = await axios.get('http://localhost:8000/settings')
        setSettings(res.data)
        // Find auto_scan setting
        const autoScanSetting = res.data.find((s: any) => s.key === 'auto_scan')
        setAutoScan(autoScanSetting ? autoScanSetting.value === 'true' : false)
      } catch (error) {
        console.error('Failed to fetch settings:', error)
      } finally {
        setLoading(false)
      }
    }
    fetchSettings()
  }, [])

  const toggleAutoScan = async () => {
    try {
      await axios.post('http://localhost:8000/settings', {
        key: 'auto_scan',
        value: (!autoScan).toString(),
        description: 'Automatically scan network'
      })
      setAutoScan(!autoScan)
      // Refresh settings to confirm
      const res = await axios.get('http://localhost:8000/settings')
      const autoScanSetting = res.data.find((s: any) => s.key === 'auto_scan')
      setAutoScan(autoScanSetting ? autoScanSetting.value === 'true' : false)
    } catch (error) {
      console.error('Failed to update setting:', error)
    }
  }

  return (
    <div className="settings-page">
      <h2>Settings</h2>
      <div className="setting-item">
        <label>
          <input
            type="checkbox"
            checked={autoScan}
            onChange={toggleAutoScan}
          />
          Auto-scan network
        </label>
      </div>
      <h3>All Settings</h3>
      <table>
        <thead>
          <tr>
            <th>Key</th>
            <th>Value</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          {settings.map((setting: any, index: number) => (
            <tr key={index}>
              <td>{setting.key}</td>
              <td>{setting.value}</td>
              <td>{setting.description || ''}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default Settings