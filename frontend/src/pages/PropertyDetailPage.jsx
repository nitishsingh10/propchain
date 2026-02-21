import { useState, useContext } from 'react'
import { useParams, Link } from 'react-router-dom'
import { WalletContext } from '../App'
import { signTransaction } from '../utils/wallet'
import { useDemoStore } from '../utils/demoStore'
import { formatINR } from '../utils/mockData'
import { useToast } from '../components/Toast'
import { SinglePropertyMap } from '../components/PropertyMap'

export default function PropertyDetailPage() {
    const { id } = useParams()
    const { walletAddress, connector } = useContext(WalletContext)
    const { properties, buyShares } = useDemoStore()
    const toast = useToast()

    const p = properties.find(prop => prop.id === Number(id))

    const [qty, setQty] = useState(100)
    const [showModal, setShowModal] = useState(false)
    const [txnState, setTxnState] = useState('idle') // idle | signing | success
    const [selectedImg, setSelectedImg] = useState(0)
    const [txnHash, setTxnHash] = useState('')

    if (!p) {
        return (
            <div className="max-w-2xl mx-auto px-6 py-24 text-center animate-fade-in">
                <h1 className="text-2xl font-bold mb-3">Property Not Found</h1>
                <p className="text-white/40 mb-6 text-sm">The property you're looking for doesn't exist.</p>
                <Link to="/marketplace" className="btn-primary text-sm">← Back to Marketplace</Link>
            </div>
        )
    }

    const totalCost = qty * p.sharePrice
    const insurance = Math.round(totalCost * p.insuranceRate / 100)
    const totalPayment = totalCost + insurance
    const availableShares = p.totalShares - p.sharesSold
    const minQty = Math.min(p.minInvestment, availableShares)
    const maxQty = Math.min(p.maxInvestment, availableShares)

    const handleBuy = async () => {
        setTxnState('signing')
        try {
            const res = await fetch('http://localhost:8000/investments/buy', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    property_id: p.id,
                    investor_address: walletAddress,
                    quantity: qty
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

            // submit to backend
            const submitRes = await fetch('http://localhost:8000/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    signed_txn: uint8ArrayToBase64(signedTxns[0])
                })
            })
            const submitData = await submitRes.json()
            if (!submitData.success) throw new Error(submitData.error || "Submission failed")

            buyShares(p.id, qty)
            setTxnHash(submitData.txid)
            setTxnState('success')
            toast.success(`Successfully purchased ${qty} shares of ${p.name}!`, 'Transaction Confirmed')
        } catch (error) {
            console.error('Transaction error:', error)
            toast.error(error.message || 'Transaction failed')
            setTxnState('idle')
        }
    }

    const resetModal = () => {
        setShowModal(false)
        setTxnState('idle')
    }

    return (
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-12 animate-fade-in">
            {/* Breadcrumb */}
            <div className="flex items-center gap-2 text-sm text-white/40 mb-6">
                <Link to="/marketplace" className="hover:text-white/70 transition-colors">Marketplace</Link>
                <span>›</span>
                <span className="text-white/60">{p.name}</span>
            </div>

            <div className="grid lg:grid-cols-3 gap-8">
                {/* Left: Details */}
                <div className="lg:col-span-2 space-y-6">
                    <div className="glass-card overflow-hidden">
                        {p.images && p.images.length > 0 ? (
                            <div>
                                <div className="h-64 sm:h-80 relative overflow-hidden">
                                    <img
                                        src={p.images[selectedImg]}
                                        alt={p.name}
                                        className="w-full h-full object-cover transition-all duration-500"
                                        key={selectedImg}
                                    />
                                    <div className="absolute inset-0 bg-gradient-to-t from-dark-950/70 via-transparent to-transparent" />
                                    {p.images.length > 1 && (
                                        <div className="absolute bottom-3 right-3 px-2.5 py-1 rounded-lg bg-black/50 text-xs text-white/80 backdrop-blur-sm">
                                            {selectedImg + 1} / {p.images.length}
                                        </div>
                                    )}
                                </div>
                                {p.images.length > 1 && (
                                    <div className="flex gap-2 p-3 overflow-x-auto">
                                        {p.images.map((img, i) => (
                                            <button key={i} onClick={() => setSelectedImg(i)}
                                                className={`w-16 h-12 rounded-lg overflow-hidden shrink-0 transition-all border-2 ${i === selectedImg ? 'border-primary-500 scale-105' : 'border-transparent opacity-60 hover:opacity-100'}`}>
                                                <img src={img} alt="" className="w-full h-full object-cover" />
                                            </button>
                                        ))}
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="h-56 bg-gradient-to-br from-primary-500/10 to-primary-200/10 flex items-center justify-center text-7xl">
                                {p.image}
                            </div>
                        )}
                        <div className="p-6">
                            <div className="flex justify-between items-start mb-2">
                                <h1 className="text-2xl font-bold">{p.name}</h1>
                                <span className={p.status === 3 ? 'badge-active' : p.status === 0 ? 'badge-pending' : 'badge-sold'}>
                                    {p.status === 3 ? 'Active' : p.status === 0 ? 'Pending' : 'Sold'}
                                </span>
                            </div>
                            <p className="text-white/40 text-sm mb-2">{p.location}</p>
                            {p.description && <p className="text-sm text-white/60 leading-relaxed">{p.description}</p>}
                        </div>
                    </div>

                    {/* Stats Grid */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 stagger-children">
                        {[
                            { label: 'Valuation', value: formatINR(p.valuation) },
                            { label: 'Share Price', value: formatINR(p.sharePrice) },
                            { label: 'Est. Yield', value: `${p.yield}%` },
                            { label: 'Available', value: availableShares.toLocaleString() },
                        ].map(s => (
                            <div key={s.label} className="stat-card">
                                <div className="text-lg font-bold text-white mb-1">{s.value}</div>
                                <div className="text-xs text-white/30 font-medium">{s.label}</div>
                            </div>
                        ))}
                    </div>

                    {/* AI Verification */}
                    <div className="glass-card p-6">
                        <h3 className="text-sm font-semibold mb-4 text-white/60 uppercase tracking-wide">AI Verification Report</h3>
                        <div className="flex items-center gap-4 mb-4">
                            <div className="relative w-16 h-16">
                                <svg className="w-16 h-16 -rotate-90" viewBox="0 0 36 36">
                                    <circle cx="18" cy="18" r="15.5" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="3" />
                                    <circle cx="18" cy="18" r="15.5" fill="none" stroke="url(#grad)" strokeWidth="3"
                                        strokeDasharray={`${p.aiScore} ${100 - p.aiScore}`} strokeLinecap="round" />
                                    <defs><linearGradient id="grad"><stop stopColor="#0E6BA8" /><stop offset="1" stopColor="#A6E1FA" /></linearGradient></defs>
                                </svg>
                                <div className="absolute inset-0 flex items-center justify-center text-sm font-bold">{p.aiScore || '—'}</div>
                            </div>
                            <div>
                                <span className={p.verificationStatus === 'APPROVED' ? 'badge-active' : 'badge-pending'}>
                                    {p.verificationStatus}
                                </span>
                                <p className="text-sm text-white/50 mt-1">
                                    {p.verificationStatus === 'APPROVED' ? 'All documents verified by AI oracle' : 'Documents are being processed'}
                                </p>
                            </div>
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                            {Object.entries(p.documents).map(([key, val]) => (
                                <div key={key} className="flex items-center gap-2 text-sm">
                                    <span>{val}</span>
                                    <span className="text-white/40 capitalize">{key.replace(/([A-Z])/g, ' $1')}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* SPV Info */}
                    <div className="glass-card p-6">
                        <h3 className="text-sm font-semibold mb-4 text-white/60 uppercase tracking-wide">SPV Legal Entity</h3>
                        <div className="space-y-2 text-sm">
                            <div className="flex justify-between"><span className="text-white/50">CIN</span><span className="font-mono text-xs">{p.spv.cin}</span></div>
                            <div className="flex justify-between"><span className="text-white/50">PAN</span><span className="font-mono">{p.spv.pan}</span></div>
                            <div className="flex justify-between"><span className="text-white/50">Status</span><span className={p.spv.status === 'ACTIVE' ? 'badge-active' : 'badge-pending'}>{p.spv.status}</span></div>
                        </div>
                    </div>

                    {/* Location Map */}
                    {p.lat && p.lng && (
                        <div className="glass-card p-6">
                            <h3 className="text-sm font-semibold mb-4 text-white/60 uppercase tracking-wide">Property Location</h3>
                            <SinglePropertyMap property={p} />
                            <div className="flex items-center gap-4 mt-3 text-sm text-white/50">
                                <span>Lat: {p.lat.toFixed(4)}°</span>
                                <span>Lng: {p.lng.toFixed(4)}°</span>
                                <a href={`https://www.google.com/maps?q=${p.lat},${p.lng}`}
                                    target="_blank" rel="noopener noreferrer"
                                    className="text-primary-400 hover:text-primary-300 ml-auto transition-colors">
                                    Open in Google Maps ↗
                                </a>
                            </div>
                        </div>
                    )}
                </div>

                {/* Right: Buy Panel */}
                <div className="space-y-6">
                    {p.status === 3 && availableShares > 0 ? (
                        <div className="glass-card p-6 sticky top-20 glow-blue">
                            <h3 className="text-lg font-semibold mb-4">Buy Shares</h3>
                            <div className="space-y-4">
                                <div>
                                    <label className="text-sm text-white/50">Quantity ({minQty}-{maxQty})</label>
                                    <input type="number" min={minQty} max={maxQty} value={qty}
                                        onChange={e => setQty(Math.min(maxQty, Math.max(minQty, +e.target.value)))}
                                        className="input-field mt-1" />
                                    <input type="range" min={minQty} max={maxQty} value={qty}
                                        onChange={e => setQty(+e.target.value)}
                                        className="w-full mt-2 accent-primary-500" />
                                </div>
                                <div className="glass-card p-4 space-y-2 text-sm">
                                    <div className="flex justify-between"><span className="text-white/50">Shares</span><span>{qty.toLocaleString()}</span></div>
                                    <div className="flex justify-between"><span className="text-white/50">Share cost</span><span>{formatINR(totalCost)}</span></div>
                                    <div className="flex justify-between"><span className="text-white/50">Insurance ({p.insuranceRate}%)</span><span>{formatINR(insurance)}</span></div>
                                    <div className="border-t border-white/10 pt-2 flex justify-between font-semibold">
                                        <span>Total</span><span className="gradient-text">{formatINR(totalPayment)}</span>
                                    </div>
                                </div>
                                <button onClick={() => setShowModal(true)}
                                    className="btn-primary w-full" disabled={!walletAddress}>
                                    {walletAddress ? 'Buy Shares →' : 'Connect Wallet First'}
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="glass-card p-6 text-center">
                            <h3 className="font-semibold mb-1">{p.status === 4 ? 'Fully Funded' : 'Pending Verification'}</h3>
                            <p className="text-sm text-white/35">{p.status === 4 ? 'All shares have been sold.' : 'This property is still being verified by the AI oracle.'}</p>
                        </div>
                    )}

                    {/* Funding Progress */}
                    <div className="glass-card p-6">
                        <h3 className="text-sm font-semibold text-white/50 mb-3">Funding Progress</h3>
                        <div className="text-2xl font-bold gradient-text mb-2">{((p.sharesSold / p.totalShares) * 100).toFixed(1)}%</div>
                        <div className="h-1.5 bg-white/[0.06] rounded-full overflow-hidden mb-2">
                            <div className="h-full bg-gradient-to-r from-primary-500 to-primary-200 rounded-full progress-animate"
                                style={{ width: `${(p.sharesSold / p.totalShares) * 100}%` }} />
                        </div>
                        <div className="text-xs text-white/40">{p.sharesSold.toLocaleString()} / {p.totalShares.toLocaleString()} shares sold</div>
                    </div>
                </div>
            </div>

            {/* Buy Modal */}
            {showModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={resetModal}>
                    <div className="glass-card p-8 max-w-md mx-4 glow-blue animate-fade-in" onClick={e => e.stopPropagation()}>
                        {txnState === 'idle' && (
                            <>
                                <h3 className="text-xl font-bold mb-4">Confirm Purchase</h3>
                                <div className="space-y-2 text-sm mb-6">
                                    <div className="flex justify-between"><span className="text-white/50">Property</span><span className="text-right max-w-[200px] truncate">{p.name}</span></div>
                                    <div className="flex justify-between"><span className="text-white/50">Shares</span><span>{qty.toLocaleString()}</span></div>
                                    <div className="flex justify-between"><span className="text-white/50">Insurance</span><span>{formatINR(insurance)}</span></div>
                                    <div className="flex justify-between font-semibold text-lg pt-2 border-t border-white/10">
                                        <span>Total</span><span className="gradient-text">{formatINR(totalPayment)}</span>
                                    </div>
                                </div>
                                <div className="flex gap-3">
                                    <button onClick={resetModal} className="btn-secondary flex-1">Cancel</button>
                                    <button onClick={handleBuy} className="btn-primary flex-1">Sign with Pera</button>
                                </div>
                            </>
                        )}
                        {txnState === 'signing' && (
                            <div className="text-center py-6">
                                <div className="w-12 h-12 border-2 border-primary-500 border-t-transparent rounded-full spin mx-auto mb-4" />
                                <h3 className="text-lg font-semibold mb-2">Processing Transaction</h3>
                                <p className="text-sm text-white/50">Signing with Pera Wallet...</p>
                            </div>
                        )}
                        {txnState === 'success' && (
                            <div className="text-center py-4">
                                <div className="w-10 h-10 rounded-full bg-primary-500/20 flex items-center justify-center text-primary-200 text-lg mx-auto mb-4">✓</div>
                                <h3 className="text-lg font-bold mb-2">Transaction Confirmed!</h3>
                                <p className="text-sm text-white/50 mb-4">You now own {qty} shares of {p.name}</p>
                                <div className="glass-card p-3 text-xs font-mono text-white/40 mb-6 break-all">
                                    TXN: {txnHash}
                                </div>
                                <div className="flex gap-3">
                                    <Link to="/portfolio" className="btn-primary flex-1" onClick={resetModal}>View Portfolio</Link>
                                    <button onClick={resetModal} className="btn-secondary flex-1">Close</button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    )
}
