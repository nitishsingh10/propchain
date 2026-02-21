import { useState, useContext, useEffect } from 'react'
import { WalletContext } from '../App'
import { signTransaction } from '../utils/wallet'
import { api } from '../utils/api'
import { TYPE_ICONS, formatINR } from '../utils/mockData'
import { useToast } from '../components/Toast'

const STATUS_COLORS = {
    ACTIVE: 'badge-active',
    PASSED: 'badge-passed',
    FAILED: 'badge-failed',
    EXECUTED: 'badge-executed',
}

export default function GovernancePage() {
    const { walletAddress, connector } = useContext(WalletContext)
    const toast = useToast()
    const [proposals, setProposals] = useState([])
    const [holdings, setHoldings] = useState([])
    const [votedProposals, setVotedProposals] = useState({})

    const [showCreate, setShowCreate] = useState(false)
    const [votingId, setVotingId] = useState(null)
    const [newProposal, setNewProposal] = useState({
        propertyId: 1, type: 'SELL', description: '', proposedValue: '',
    })

    useEffect(() => {
        if (!walletAddress) return

        Promise.all([
            api.listProposals(0),
            api.getPortfolio(walletAddress)
        ]).then(([props, port]) => {
            setProposals(props)
            setHoldings(port.holdings || [])
        }).catch(console.error)
    }, [walletAddress])

    if (!walletAddress) {
        return (
            <div className="max-w-2xl mx-auto px-6 py-24 text-center animate-fade-in">
                <h1 className="text-2xl font-bold mb-3">Governance</h1>
                <p className="text-white/40 text-sm mb-6">Connect your wallet to participate in governance voting.</p>
                <div className="glass-card p-8 max-w-sm mx-auto">
                    <p className="text-sm text-white/35">Your vote weight is proportional to your share holdings.</p>
                </div>
            </div>
        )
    }

    const totalShares = holdings.reduce((s, h) => s + h.shares, 0)

    const handleVote = async (proposalId, voteType) => {
        setVotingId(proposalId)
        try {
            const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
            const res = await fetch(`${API_BASE}/governance/vote`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    proposal_id: proposalId,
                    voter_address: walletAddress,
                    vote_yes: voteType === 'YES'
                })
            })
            const data = await res.json()
            if (!data.unsigned_txns || data.unsigned_txns.length === 0) throw new Error("Could not generate transaction")

            const base64ToUint8Array = (base64) => {
                const padding = '='.repeat((4 - base64.length % 4) % 4);
                const base64Standard = (base64 + padding).replace(/\-/g, '+').replace(/_/g, '/');
                const binaryString = window.atob(base64Standard)
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

            const algosdk = (await import('algosdk')).default;

            const txnArray = base64ToUint8Array(data.unsigned_txns[0])
            const decodedTxn = algosdk.decodeUnsignedTransaction(txnArray)
            const signedTxns = await signTransaction(connector, decodedTxn)
            if (!signedTxns) throw new Error("Transaction signing failed or was canceled")

            const submitRes = await fetch(`${API_BASE}/submit`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    signed_txn: uint8ArrayToBase64(signedTxns[0])
                })
            })
            const submitData = await submitRes.json()
            if (!submitData.success) throw new Error(submitData.error || "Submission failed")

            await api.recordVote({ proposal_id: proposalId, voter_address: walletAddress, vote_yes: voteType === 'YES' })

            setVotedProposals(prev => ({ ...prev, [proposalId]: voteType }))
            setProposals(prev => prev.map(p =>
                (p.proposal_id || p.id) === proposalId
                    ? { ...p, yes_weight: voteType === 'YES' ? (p.yes_weight || 0) + totalShares : (p.yes_weight || 0), no_weight: voteType === 'NO' ? (p.no_weight || 0) + totalShares : (p.no_weight || 0) }
                    : p
            ))
            toast.success(`Voted ${voteType} on proposal #${proposalId}`, 'Vote Cast')
        } catch (error) {
            console.error('Vote error:', error)
            toast.error(error.message || 'Vote failed')
        } finally {
            setVotingId(null)
        }
    }

    const typeLabels = { 0: 'SELL', 1: 'RENOVATE', 2: 'CHANGE_RENT' }

    const handleCreate = async () => {
        if (!newProposal.description.trim()) {
            toast.error('Please enter a description', 'Missing Field')
            return
        }
        try {
            const proposalTypeMap = { 'SELL': 0, 'RENOVATE': 1, 'CHANGE_RENT': 2 }
            await api.createProposal({
                property_id: Number(newProposal.propertyId),
                proposer_address: walletAddress,
                proposal_type: proposalTypeMap[newProposal.type] || 0,
                description: newProposal.description,
                proposed_value: Number(newProposal.proposedValue) || 0,
                voting_days: 7
            })
            const props = await api.listProposals(0)
            setProposals(props)

            setShowCreate(false)
            setNewProposal({ propertyId: 1, type: 'SELL', description: '', proposedValue: '' })
            toast.success('Your proposal has been submitted for voting', 'Proposal Created')
        } catch (e) {
            toast.error(e.message || "Failed to create proposal")
        }
    }

    return (
        <div className="max-w-5xl mx-auto px-4 sm:px-6 py-12 animate-fade-in">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
                <div>
                    <h1 className="text-3xl font-bold">On-Chain <span className="gradient-text">Governance</span></h1>
                    <p className="text-white/50 mt-1">Vote on property decisions with your shares</p>
                </div>
                <div className="flex items-center gap-3">
                    <div className="glass-card px-4 py-2 text-sm flex items-center gap-2">
                        <span className="text-white/40">Your Weight:</span>
                        <span className="font-semibold gradient-text">{totalShares.toLocaleString()} shares</span>
                    </div>
                    <button onClick={() => setShowCreate(true)} className="btn-primary text-sm !py-2 !px-4">+ New Proposal</button>
                </div>
            </div>

            {/* Proposals */}
            <div className="space-y-4 stagger-children">
                {proposals.map(p => {
                    const pId = p.proposal_id || p.id
                    const totalVotes = (p.yes_weight || 0) + (p.no_weight || 0)
                    const _t = Math.max(totalVotes, p.total_shares || p.totalShares || 1)
                    const yesP = _t > 0 ? ((p.yes_weight || p.yesWeight || 0) / _t * 100).toFixed(1) : '0.0'
                    const noP = _t > 0 ? ((p.no_weight || p.noWeight || 0) / _t * 100).toFixed(1) : '0.0'
                    const hasVoted = votedProposals[pId]
                    const isVoting = votingId === pId
                    const typeLabel = typeof p.type === 'string' ? p.type : (typeLabels[p.proposal_type] || 'PROP')

                    return (
                        <div key={pId} className="glass-card p-6 hover:bg-white/[0.08] transition-all">
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <span className="w-8 h-8 rounded-lg bg-primary-500/15 flex items-center justify-center text-xs font-bold text-primary-200">{typeLabel.charAt(0)}</span>
                                    <div>
                                        <h3 className="font-semibold">{p.description}</h3>
                                        <p className="text-sm text-white/40">
                                            Property #{p.property_id || p.propertyId} • Deadline: {new Date((p.voting_deadline || p.deadline || (Date.now() / 1000 + 86400)) * 1000).toLocaleDateString()}
                                            {(p.proposed_value || p.proposedValue) > 0 && <> • Value: {formatINR(p.proposed_value || p.proposedValue)}</>}
                                        </p>
                                    </div>
                                </div>
                                <span className={STATUS_COLORS[p.status] || 'badge-pending'}>{p.status}</span>
                            </div>

                            {/* Vote Bars */}
                            <div className="space-y-2 mb-4">
                                <div className="flex items-center gap-3">
                                    <span className="text-sm text-white/50 w-8">YES</span>
                                    <div className="flex-1 h-3 bg-white/5 rounded-full overflow-hidden">
                                        <div className="h-full bg-primary-500 rounded-full progress-animate" style={{ width: `${yesP}%` }} />
                                    </div>
                                    <span className="text-sm font-semibold text-primary-400 w-14 text-right">{yesP}%</span>
                                </div>
                                <div className="flex items-center gap-3">
                                    <span className="text-sm text-white/50 w-8">NO</span>
                                    <div className="flex-1 h-3 bg-white/5 rounded-full overflow-hidden">
                                        <div className="h-full bg-red-500 rounded-full progress-animate" style={{ width: `${noP}%` }} />
                                    </div>
                                    <span className="text-sm font-semibold text-red-400 w-14 text-right">{noP}%</span>
                                </div>
                            </div>

                            {p.status === 'ACTIVE' && (
                                <div className="flex gap-3">
                                    {hasVoted ? (
                                        <div className="flex-1 glass-card px-4 py-2.5 text-center text-sm">
                                            You voted <span className={hasVoted === 'YES' ? 'text-primary-400' : 'text-red-400'}>✓ {hasVoted}</span>
                                        </div>
                                    ) : isVoting ? (
                                        <div className="flex-1 glass-card px-4 py-2.5 text-center text-sm flex items-center justify-center gap-2">
                                            <span className="w-4 h-4 border-2 border-primary-500 border-t-transparent rounded-full spin" />
                                            Submitting vote...
                                        </div>
                                    ) : (
                                        <>
                                            <button onClick={() => handleVote(pId, 'YES')} className="btn-primary flex-1 text-sm">Vote YES</button>
                                            <button onClick={() => handleVote(pId, 'NO')} className="btn-danger flex-1 text-sm">Vote NO</button>
                                        </>
                                    )}
                                </div>
                            )}
                        </div>
                    )
                })}
            </div>

            {proposals.length === 0 && (
                <div className="text-center py-20">
                    <h3 className="text-lg font-semibold mb-2">No proposals yet</h3>
                    <p className="text-white/35 text-sm">Be the first to create a governance proposal.</p>
                </div>
            )}

            {/* Create Modal */}
            {showCreate && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={() => setShowCreate(false)}>
                    <div className="glass-card p-8 max-w-md mx-4 animate-fade-in" onClick={e => e.stopPropagation()}>
                        <h3 className="text-xl font-bold mb-4">Create Proposal</h3>
                        <div className="space-y-4">
                            <div>
                                <label className="text-sm text-white/50 mb-1 block">Property ID</label>
                                <input type="number" className="input-field" placeholder="1"
                                    value={newProposal.propertyId} onChange={e => setNewProposal({ ...newProposal, propertyId: e.target.value })} />
                            </div>
                            <div>
                                <label className="text-sm text-white/50 mb-1 block">Type</label>
                                <select className="input-field" value={newProposal.type}
                                    onChange={e => setNewProposal({ ...newProposal, type: e.target.value })}>
                                    <option value="SELL">SELL</option>
                                    <option value="RENOVATE">RENOVATE</option>
                                    <option value="CHANGE_RENT">CHANGE_RENT</option>
                                </select>
                            </div>
                            <div>
                                <label className="text-sm text-white/50 mb-1 block">Description</label>
                                <textarea className="input-field" rows={3} placeholder="Describe your proposal..."
                                    value={newProposal.description} onChange={e => setNewProposal({ ...newProposal, description: e.target.value })} />
                            </div>
                            <div>
                                <label className="text-sm text-white/50 mb-1 block">Proposed Value (₹)</label>
                                <input type="number" className="input-field" placeholder="65000000"
                                    value={newProposal.proposedValue} onChange={e => setNewProposal({ ...newProposal, proposedValue: e.target.value })} />
                            </div>
                            <div className="flex gap-3">
                                <button onClick={() => setShowCreate(false)} className="btn-secondary flex-1">Cancel</button>
                                <button onClick={handleCreate} className="btn-primary flex-1">Submit</button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
