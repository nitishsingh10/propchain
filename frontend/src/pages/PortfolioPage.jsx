import { useState, useContext } from 'react'
import { Link } from 'react-router-dom'
import { WalletContext } from '../App'
import { signTransaction } from '../utils/wallet'
import { useDemoStore } from '../utils/demoStore'
import { formatINR, formatValuation, STATUS_MAP } from '../utils/mockData'
import { useToast } from '../components/Toast'

export default function PortfolioPage() {
    const { walletAddress, connector } = useContext(WalletContext)
    const { holdings, claimRent, getListedProperties } = useDemoStore()
    const toast = useToast()
    const [claimingId, setClaimingId] = useState(null)
    const [activeTab, setActiveTab] = useState('holdings') // 'holdings' | 'listed'

    const listedProperties = getListedProperties()

    if (!walletAddress) {
        return (
            <div className="max-w-2xl mx-auto px-6 py-24 text-center animate-fade-in">
                <h1 className="text-2xl font-bold mb-3">Your Portfolio</h1>
                <p className="text-white/40 text-sm mb-6">Connect your Pera Wallet to view your real estate portfolio.</p>
                <div className="glass-card p-8 max-w-sm mx-auto">
                    <p className="text-sm text-white/35">Click "Connect Wallet" in the navigation bar to get started.</p>
                </div>
            </div>
        )
    }

    const totalValue = holdings.reduce((s, h) => s + h.shares * h.sharePrice, 0)
    const totalClaimable = holdings.reduce((s, h) => s + h.claimableRent, 0)
    const totalClaimed = holdings.reduce((s, h) => s + h.totalClaimed, 0)
    const avgYield = holdings.length > 0 ? (holdings.reduce((s, h) => s + h.yield, 0) / holdings.length).toFixed(1) : '0.0'

    const handleClaim = async (propertyId, name) => {
        setClaimingId(propertyId)
        try {
            const res = await fetch('http://localhost:8000/rent/claim', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    property_id: propertyId,
                    investor_address: walletAddress
                })
            })
            const data = await res.json()
            if (!data.unsigned_txns || data.unsigned_txns.length === 0) throw new Error("Could not generate transaction")

            const base64ToUint8Array = (base64) => {
                const binaryString = window.atob(base64)
                const len = binaryString.length
                const bytes = new Uint8Array(len)
                for (let i = 0; i < len; i++) { bytes[i] = binaryString.charCodeAt(i) }
                return bytes
            }

            const uint8ArrayToBase64 = (bytes) => {
                let binary = ''
                const len = bytes.byteLength
                for (let i = 0; i < len; i++) { binary += String.fromCharCode(bytes[i]) }
                return window.btoa(binary)
            }

            const txnArray = base64ToUint8Array(data.unsigned_txns[0])
            const signedTxns = await signTransaction(connector, txnArray)
            if (!signedTxns) throw new Error("Transaction signing failed or was canceled")

            const submitRes = await fetch('http://localhost:8000/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    signed_txn: uint8ArrayToBase64(signedTxns[0])
                })
            })
            const submitData = await submitRes.json()
            if (!submitData.success) throw new Error(submitData.error || "Submission failed")

            claimRent(propertyId)
            toast.success(`Rent claimed from ${name}`, 'Rent Received')
        } catch (error) {
            console.error('Claim error:', error)
            toast.error(error.message || 'Claim failed')
        } finally {
            setClaimingId(null)
        }
    }

    return (
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-12 animate-fade-in">
            <h1 className="text-3xl font-bold mb-8">Your <span className="gradient-text">Portfolio</span></h1>

            {/* Summary Cards */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-10 stagger-children">
                {[
                    { label: 'Portfolio Value', value: formatINR(totalValue) },
                    { label: 'Claimable Rent', value: formatINR(totalClaimable), highlight: totalClaimable > 0 },
                    { label: 'Total Earned', value: formatINR(totalClaimed) },
                    { label: 'Listed Properties', value: listedProperties.length.toString() },
                ].map(s => (
                    <div key={s.label} className={`stat-card ${s.highlight ? 'border-primary-500/20' : ''}`}>
                        <div className="text-xl font-bold text-white mb-1">{s.value}</div>
                        <div className="text-xs text-white/30 font-medium tracking-wide">{s.label}</div>
                    </div>
                ))}
            </div>

            {/* Claim All */}
            {totalClaimable > 0 && (
                <div className="glass-card p-4 mb-6 flex flex-col sm:flex-row items-center justify-between gap-4 border-primary-500/10">
                    <div className="flex items-center gap-3">
                        <div className="w-2 h-2 rounded-full bg-primary-400" />
                        <div>
                            <div className="text-sm font-medium">{formatINR(totalClaimable)} claimable rent</div>
                            <div className="text-xs text-white/35">Across {holdings.filter(h => h.claimableRent > 0).length} properties</div>
                        </div>
                    </div>
                </div>
            )}

            {/* Tabs */}
            <div className="flex gap-0.5 mb-6 bg-white/[0.03] rounded-lg p-0.5 w-fit border border-white/[0.04]">
                <button
                    onClick={() => setActiveTab('holdings')}
                    className={`px-4 py-2 rounded-md text-[13px] font-medium transition-all ${activeTab === 'holdings'
                        ? 'bg-white/[0.08] text-white'
                        : 'text-white/40 hover:text-white/60'
                        }`}
                >
                    Holdings ({holdings.length})
                </button>
                <button
                    onClick={() => setActiveTab('listed')}
                    className={`px-4 py-2 rounded-md text-[13px] font-medium transition-all ${activeTab === 'listed'
                        ? 'bg-white/[0.08] text-white'
                        : 'text-white/40 hover:text-white/60'
                        }`}
                >
                    Your Properties ({listedProperties.length})
                </button>
            </div>

            {/* ── Holdings Tab ── */}
            {activeTab === 'holdings' && (
                <>
                    {holdings.length === 0 ? (
                        <div className="glass-card p-12 text-center">
                            <h3 className="text-lg font-semibold mb-2">No Holdings Yet</h3>
                            <p className="text-white/35 mb-6 text-sm">Start investing in fractionalized real estate.</p>
                            <Link to="/marketplace" className="btn-primary text-sm">Explore Marketplace →</Link>
                        </div>
                    ) : (
                        <div className="glass-card overflow-hidden">
                            <div className="p-4 border-b border-white/5 flex justify-between items-center">
                                <h3 className="font-semibold">Holdings ({holdings.length})</h3>
                                <span className="text-xs text-white/30">{holdings.reduce((s, h) => s + h.shares, 0).toLocaleString()} total shares</span>
                            </div>
                            <div className="divide-y divide-white/5">
                                {holdings.map(h => (
                                    <div key={h.propertyId} className="p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-white/[0.03] transition-all">
                                        <div className="flex items-center gap-3">
                                            <div className="w-10 h-10 rounded-lg bg-white/[0.06] flex items-center justify-center text-sm font-semibold text-white/60 shrink-0">
                                                {h.name?.charAt(0) || 'P'}
                                            </div>
                                            <div>
                                                <Link to={`/property/${h.propertyId}`} className="font-semibold hover:text-primary-400 transition-colors">{h.name}</Link>
                                                <div className="text-sm text-white/40">{h.shares.toLocaleString()} shares ({(h.shares / h.totalShares * 100).toFixed(1)}%)</div>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-6 sm:gap-8">
                                            <div className="text-right">
                                                <div className="font-semibold">{formatINR(h.shares * h.sharePrice)}</div>
                                                <div className="text-sm text-primary-400">{h.yield}% yield</div>
                                            </div>
                                            <div className="text-right min-w-[90px]">
                                                <div className="text-xs text-white/50">Claimable</div>
                                                <div className="font-semibold text-primary-400">{formatINR(h.claimableRent)}</div>
                                            </div>
                                            <button
                                                onClick={() => handleClaim(h.propertyId, h.name)}
                                                disabled={h.claimableRent === 0 || claimingId === h.propertyId}
                                                className={`btn-primary text-sm !py-2 !px-4 min-w-[90px] ${h.claimableRent === 0 ? 'opacity-40 cursor-not-allowed' : ''}`}>
                                                {claimingId === h.propertyId ? (
                                                    <span className="flex items-center gap-2 justify-center">
                                                        <span className="w-3 h-3 border border-white border-t-transparent rounded-full spin" /> Claiming...
                                                    </span>
                                                ) : h.claimableRent === 0 ? 'Claimed ✓' : 'Claim'}
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </>
            )}

            {/* ── Listed Properties Tab ── */}
            {activeTab === 'listed' && (
                <>
                    {listedProperties.length === 0 ? (
                        <div className="glass-card p-12 text-center">
                            <h3 className="text-lg font-semibold mb-2">No Properties Listed</h3>
                            <p className="text-white/35 mb-6 text-sm">List your first property to tokenize it on the blockchain.</p>
                            <Link to="/list" className="btn-primary text-sm">List Property →</Link>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {listedProperties.map(p => {
                                const statusInfo = STATUS_MAP[p.status] || STATUS_MAP[0]
                                const soldPct = p.totalShares > 0 ? (p.sharesSold / p.totalShares * 100) : 0
                                const verificationSteps = Object.values(p.documents || {})
                                const verified = verificationSteps.filter(v => v.startsWith('✅')).length
                                const totalSteps = verificationSteps.length || 1

                                return (
                                    <div key={p.id} className="glass-card p-4 hover:bg-white/[0.03] transition-all">
                                        <div className="flex flex-col sm:flex-row gap-4">
                                            {/* Property Image */}
                                            <div className="w-full sm:w-36 h-24 rounded-lg overflow-hidden shrink-0 bg-white/[0.04] flex items-center justify-center">
                                                {p.images && p.images.length > 0 ? (
                                                    <img src={p.images[0]} alt={p.name} className="w-full h-full object-cover" />
                                                ) : (
                                                    <span className="text-4xl">{p.image || '🏢'}</span>
                                                )}
                                            </div>

                                            {/* Property Info */}
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-start justify-between gap-3 mb-2">
                                                    <div>
                                                        <Link to={`/property/${p.id}`} className="font-semibold text-lg hover:text-primary-400 transition-colors">
                                                            {p.name}
                                                        </Link>
                                                        <div className="text-sm text-white/40 flex items-center gap-2 mt-0.5">
                                                            {p.location}
                                                        </div>
                                                    </div>
                                                    <span className={`shrink-0 px-3 py-1 rounded-md text-xs font-medium ${p.status === 3 ? 'bg-primary-500/15 text-primary-200 border border-primary-500/20' :
                                                        p.status === 0 ? 'bg-amber-500/15 text-amber-400 border border-amber-500/20' :
                                                            'bg-white/10 text-white/50 border border-white/10'
                                                        }`}>
                                                        {statusInfo.label}
                                                    </span>
                                                </div>

                                                {/* Stats Row */}
                                                <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm mb-3">
                                                    <div>
                                                        <span className="text-white/40">Valuation </span>
                                                        <span className="font-semibold text-white">{formatValuation(p.valuation)}</span>
                                                    </div>
                                                    <div>
                                                        <span className="text-white/40">Share Price </span>
                                                        <span className="font-semibold text-white">{formatINR(p.sharePrice)}</span>
                                                    </div>
                                                    <div>
                                                        <span className="text-white/40">Type </span>
                                                        <span className="font-semibold text-white">{p.propertyType}</span>
                                                    </div>
                                                    {p.yield > 0 && (
                                                        <div>
                                                            <span className="text-white/40">Yield </span>
                                                            <span className="font-semibold text-primary-400">{p.yield}%</span>
                                                        </div>
                                                    )}
                                                </div>

                                                {/* Progress Bars */}
                                                <div className="grid sm:grid-cols-2 gap-3">
                                                    {/* Share Sales Progress */}
                                                    <div>
                                                        <div className="flex justify-between text-xs mb-1">
                                                            <span className="text-white/40">Shares Sold</span>
                                                            <span className="text-white/60">{p.sharesSold.toLocaleString()} / {p.totalShares.toLocaleString()} ({soldPct.toFixed(0)}%)</span>
                                                        </div>
                                                        <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                                                            <div
                                                                className="h-full rounded-full transition-all duration-500"
                                                                style={{
                                                                    width: `${soldPct}%`,
                                                                    background: soldPct >= 100 ? 'linear-gradient(90deg, #0E6BA8, #A6E1FA)' :
                                                                        soldPct > 50 ? 'linear-gradient(90deg, #0E6BA8, #A6E1FA)' :
                                                                            'linear-gradient(90deg, #0A2472, #0E6BA8)',
                                                                }}
                                                            />
                                                        </div>
                                                    </div>

                                                    {/* Verification Progress */}
                                                    <div>
                                                        <div className="flex justify-between text-xs mb-1">
                                                            <span className="text-white/40">Verification</span>
                                                            <span className="text-white/60">{verified}/{totalSteps} checks passed</span>
                                                        </div>
                                                        <div className="h-2 bg-white/5 rounded-full overflow-hidden">
                                                            <div
                                                                className="h-full rounded-full transition-all duration-500"
                                                                style={{
                                                                    width: `${(verified / totalSteps) * 100}%`,
                                                                    background: verified === totalSteps ? 'linear-gradient(90deg, #0E6BA8, #A6E1FA)' :
                                                                        'linear-gradient(90deg, #f59e0b, #d97706)',
                                                                }}
                                                            />
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )
                            })}
                        </div>
                    )}
                </>
            )}
        </div>
    )
}
