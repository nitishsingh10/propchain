import { useState, createContext } from 'react'
import { Routes, Route } from 'react-router-dom'
import { ToastProvider } from './components/Toast'
import { DemoProvider } from './utils/demoStore'
import Layout from './components/Layout'
import LandingPage from './pages/LandingPage'
import MarketplacePage from './pages/MarketplacePage'
import PropertyDetailPage from './pages/PropertyDetailPage'
import ListPropertyPage from './pages/ListPropertyPage'
import PortfolioPage from './pages/PortfolioPage'
import GovernancePage from './pages/GovernancePage'

export const WalletContext = createContext(null)

export default function App() {
    const [walletAddress, setWalletAddress] = useState(null)
    const [connector, setConnector] = useState(null)

    return (
        <WalletContext.Provider value={{ walletAddress, setWalletAddress, connector, setConnector }}>
            <DemoProvider>
                <ToastProvider>
                    <Layout>
                        <Routes>
                            <Route path="/" element={<LandingPage />} />
                            <Route path="/marketplace" element={<MarketplacePage />} />
                            <Route path="/property/:id" element={<PropertyDetailPage />} />
                            <Route path="/list" element={<ListPropertyPage />} />
                            <Route path="/portfolio" element={<PortfolioPage />} />
                            <Route path="/governance" element={<GovernancePage />} />
                        </Routes>
                    </Layout>
                </ToastProvider>
            </DemoProvider>
        </WalletContext.Provider>
    )
}
