/**
 * PropChain — API Client
 */
const BASE = import.meta.env.VITE_API_URL || ''

async function request(path, options = {}) {
    const res = await fetch(`${BASE}${path}`, {
        headers: { 'Content-Type': 'application/json', ...options.headers },
        ...options,
    })
    if (!res.ok) {
        const err = await res.json().catch(() => ({ error: res.statusText }))
        throw new Error(err.detail || err.error || 'API Error')
    }
    return res.json()
}

export const api = {
    // Properties
    listProperties: (params) => request(`/properties/?${new URLSearchParams(params)}`),
    getProperty: (id) => request(`/properties/${id}`),
    submitProperty: (data) => request('/properties/submit', { method: 'POST', body: JSON.stringify(data) }),
    verifyProperty: async (propertyId, files) => {
        const formData = new FormData()
        files.forEach(f => formData.append('files', f))
        const res = await fetch(`${BASE}/properties/${propertyId}/verify`, { method: 'POST', body: formData })
        if (!res.ok) {
            const err = await res.json().catch(() => ({ error: res.statusText }))
            throw new Error(err.detail || err.error || 'API Error')
        }
        return res.json()
    },
    activateProperty: (id, data) => request(`/properties/${id}/activate`, { method: 'POST', body: JSON.stringify(data) }),

    // Investments
    buyShares: (data) => request('/investments/buy', { method: 'POST', body: JSON.stringify(data) }),
    recordBuy: (data) => request('/investments/record_buy', { method: 'POST', body: JSON.stringify(data) }),
    getPortfolio: (address) => request(`/investments/portfolio/${address}`),
    getHoldings: (pid, addr) => request(`/investments/holdings/${pid}/${addr}`),

    // Rent
    depositRent: (data) => request('/rent/deposit', { method: 'POST', body: JSON.stringify(data) }),
    claimRent: (data) => request('/rent/claim', { method: 'POST', body: JSON.stringify(data) }),
    recordClaim: (data) => request('/rent/record_claim', { method: 'POST', body: JSON.stringify(data) }),
    rentStats: (pid) => request(`/rent/stats/${pid}`),

    // Governance
    createProposal: (data) => request('/governance/propose', { method: 'POST', body: JSON.stringify(data) }),
    castVote: (data) => request('/governance/vote', { method: 'POST', body: JSON.stringify(data) }),
    recordVote: (data) => request('/governance/record_vote', { method: 'POST', body: JSON.stringify(data) }),
    finalizeProposal: (id) => request(`/governance/finalize/${id}`, { method: 'POST' }),
    listProposals: (pid) => request(`/governance/proposals/${pid}`),

    // Settlement
    initiateSettlement: (data) => request('/settlement/initiate', { method: 'POST', body: JSON.stringify(data) }),
    settlementStatus: (pid) => request(`/settlement/status/${pid}`),
}
