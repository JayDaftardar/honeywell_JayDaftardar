import { useState } from 'react'
import { Dashboard } from './Dashboard'
import { Analytics } from './Analytics'
import { Tabs } from './components/ui/Tabs'
import './index.css'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')

  return (
    <div className="flex flex-col h-screen">
      <div className="pt-4 px-4 md:px-6 lg:px-8">
        <Tabs activeTab={activeTab} setActiveTab={setActiveTab} />
      </div>
      <div className="flex-1 overflow-auto">
        {activeTab === 'dashboard' ? <Dashboard /> : <Analytics />}
      </div>
    </div>
  )
}

export default App
