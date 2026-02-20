import { useContext, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { WalletContext } from '../App'
import { connectWallet, disconnectWallet, truncateAddress } from '../utils/wallet'
import { useToast } from './Toast'
import { Building2 } from 'lucide-react'

const NAV_LINKS = [
    { path: '/marketplace', label: 'Marketplace' },
    { path: '/list', label: 'List Property' },
    { path: '/portfolio', label: 'Portfolio' },
    { path: '/governance', label: 'Governance' },
]

export default function Layout({ children }) {
    const { walletAddress, setWalletAddress, setConnector } = useContext(WalletContext)
    const location = useLocation()
    const toast = useToast()
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

    const handleConnect = async () => {
        const result = await connectWallet()
        if (result) {
            setWalletAddress(result.address)
            setConnector(result.connector)
            toast.success(`Connected: ${result.address.slice(0, 6)}...${result.address.slice(-4)}`, 'Wallet Connected')
        }
    }

    const handleDisconnect = async () => {
        await disconnectWallet()
        setWalletAddress(null)
        setConnector(null)
        toast.info('Your wallet has been disconnected.', 'Disconnected')
    }

    return (
        <div className="min-h-screen bg-dark-950">
            {/* Navbar */}
            <nav className="fixed top-0 left-0 right-0 z-50 bg-dark-950/80 backdrop-blur-xl border-b border-white/[0.04]">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
                    <Link to="/" className="flex items-center gap-2.5 group">
                        <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-white shadow-lg shadow-primary-500/20 group-hover:scale-105 transition-transform duration-300">
                            <Building2 size={18} strokeWidth={2.5} />
                        </div>
                        <span className="text-[15px] font-bold text-white/90 tracking-tight group-hover:text-white transition-colors">PropChain</span>
                    </Link>

                    {/* Desktop Nav */}
                    <div className="hidden md:flex items-center gap-1">
                        {NAV_LINKS.map(link => (
                            <Link key={link.path} to={link.path}
                                className={`px-3.5 py-1.5 rounded-lg text-[13px] font-medium transition-all duration-300 ${location.pathname === link.path
                                    ? 'bg-white/[0.08] text-white shadow-sm ring-1 ring-white/[0.05]'
                                    : 'text-white/45 hover:text-white/90 hover:bg-white/[0.04]'
                                    }`}>
                                {link.label}
                            </Link>
                        ))}
                    </div>

                    <div className="flex items-center gap-3">
                        {walletAddress ? (
                            <div className="flex items-center gap-3">
                                <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/[0.03] border border-white/[0.05]">
                                    <span className="w-1.5 h-1.5 rounded-full bg-accent-500 pulse-glow box-shadow-glow-accent" />
                                    <span className="text-xs text-white/60 font-mono tracking-wide">{truncateAddress(walletAddress)}</span>
                                </div>
                                <button onClick={handleDisconnect} className="btn-secondary text-xs !py-1.5 !px-3 hover:bg-white/10 transition-colors">Disconnect</button>
                            </div>
                        ) : (
                            <div className="flex items-center gap-2">
                                <button onClick={handleConnect}
                                    className="btn-primary text-xs !py-1.5 !px-4 shadow-lg shadow-primary-500/20 hover:shadow-primary-500/30 transition-all duration-300">
                                    Connect Wallet
                                </button>
                            </div>
                        )}

                        {/* Mobile Hamburger */}
                        <button
                            className="md:hidden flex flex-col gap-1.5 p-2 hover:bg-white/5 rounded-lg transition-colors"
                            onClick={() => setMobileMenuOpen(true)}>
                            <span className="w-5 h-[1.5px] bg-white/60 rounded-full block transition-all" />
                            <span className="w-5 h-[1.5px] bg-white/60 rounded-full block transition-all" />
                            <span className="w-3.5 h-[1.5px] bg-white/60 rounded-full block transition-all group-hover:w-5" />
                        </button>
                    </div>
                </div>
            </nav>

            {/* Mobile Drawer */}
            {mobileMenuOpen && (
                <div className="fixed inset-0 z-[60] md:hidden">
                    <div className="absolute inset-0 bg-black/60 backdrop-blur-sm transition-opacity" onClick={() => setMobileMenuOpen(false)} />
                    <div className="absolute right-0 top-0 bottom-0 w-72 bg-dark-950 border-l border-white/[0.08] drawer-enter shadow-2xl">
                        <div className="flex items-center justify-between p-5 border-b border-white/[0.06]">
                            <div className="flex items-center gap-2.5">
                                <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-white">
                                    <Building2 size={16} strokeWidth={2.5} />
                                </div>
                                <span className="font-bold text-sm text-white/90">Menu</span>
                            </div>
                            <button onClick={() => setMobileMenuOpen(false)} className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-white/5 text-white/40 hover:text-white transition-all">✕</button>
                        </div>
                        <div className="p-3 space-y-1">
                            {NAV_LINKS.map(link => (
                                <Link key={link.path} to={link.path}
                                    onClick={() => setMobileMenuOpen(false)}
                                    className={`flex items-center px-4 py-3 rounded-xl text-sm font-medium transition-all ${location.pathname === link.path
                                        ? 'bg-primary-500/10 text-primary-400 border border-primary-500/20'
                                        : 'text-white/50 hover:text-white hover:bg-white/[0.04]'
                                        }`}>
                                    {link.label}
                                </Link>
                            ))}
                        </div>
                        {walletAddress && (
                            <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-white/[0.06] bg-black/20">
                                <div className="flex items-center gap-3 px-2">
                                    <span className="w-2 h-2 rounded-full bg-accent-500 pulse-glow" />
                                    <div className="flex flex-col">
                                        <span className="text-[10px] uppercase tracking-wider text-white/30 font-bold">Connected as</span>
                                        <span className="text-xs text-white/80 font-mono">{truncateAddress(walletAddress)}</span>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Main Content */}
            <main className="pt-14 min-h-[calc(100vh-140px)]">{children}</main>

            {/* Footer */}
            <footer className="border-t border-white/[0.04] py-8 px-6 bg-black/20">
                <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
                    <div className="flex items-center gap-2.5 opacity-60 hover:opacity-100 transition-opacity">
                        <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-white shadow-lg shadow-primary-500/10">
                            <Building2 size={14} strokeWidth={2.5} />
                        </div>
                        <span className="text-sm font-medium text-white/50">PropChain Protocol © 2026</span>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-white/30 font-medium">
                        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/[0.02] border border-white/[0.03]">
                            <span className="w-1.5 h-1.5 rounded-full bg-accent-500 shadow-[0_0_8px_rgba(34,197,94,0.4)]" />
                            <span>Algorand Testnet</span>
                        </div>
                        <span className="text-white/10">|</span>
                        <div className="flex items-center gap-1.5 hover:text-white/60 transition-colors">
                            <span>Powered by AI Oracle</span>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    )
}
