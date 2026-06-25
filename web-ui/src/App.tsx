import { Routes, Route, Link, NavLink } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Devices from './pages/Devices'
import Scans from './pages/Scans'
import Alerts from './pages/Alerts'
import Settings from './pages/Settings'
import NotFound from './pages/NotFound'
import './App.css'

function App() {
  return (
    <>
      <nav className="navbar">
        <div className="nav-container">
          <Link to="/" className="nav-logo">
            Sentinel Prime
          </Link>
          <div className="nav-links">
            <NavLink to="/" end className="nav-link">
              Dashboard
            </NavLink>
            <NavLink to="/devices" className="nav-link">
              Devices
            </NavLink>
            <NavLink to="/scans" className="nav-link">
              Scans
            </NavLink>
            <NavLink to="/alerts" className="nav-link">
              Alerts
            </NavLink>
            <NavLink to="/settings" className="nav-link">
              Settings
            </NavLink>
          </div>
        </div>
      </nav>
      <div className="app-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/devices" element={<Devices />} />
          <Route path="/scans" element={<Scans />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/settings" element={<Settings />} />
                  <Route path="*" element={<NotFound />} />
                </Routes>
      </div>
    </>
  )
}

export default App