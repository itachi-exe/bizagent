import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Landing from './pages/Landing'
import Dashboard from './pages/Dashboard'
import BotSettings from './pages/BotSettings'
import UploadDatabase from './pages/UploadDatabase'

export default function App() {
  return <BrowserRouter><Routes>
    <Route path="/" element={<Landing />} />
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/settings/bot" element={<BotSettings />} />
    <Route path="/settings/upload" element={<UploadDatabase />} />
  </Routes></BrowserRouter>
}
