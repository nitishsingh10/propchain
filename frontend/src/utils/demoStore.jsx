import { createContext, useContext, useState, useEffect } from 'react'
import { PROPERTIES, INITIAL_HOLDINGS, INITIAL_PROPOSALS } from './mockData'

const DemoContext = createContext(null)

export function DemoProvider({ children }) {
    // Initialize state from mock data
    const [properties, setProperties] = useState(PROPERTIES)
    const [holdings, setHoldings] = useState(INITIAL_HOLDINGS)
    const [proposals, setProposals] = useState(INITIAL_PROPOSALS)
    const [balance, setBalance] = useState(100000) // Mock wallet balance

    // --- Actions ---

    // Invest in a property (Buy Shares)
    const invest = (propertyId, amount) => {
        const property = properties.find(p => p.id === Number(propertyId))
        if (!property) return false

        const sharesToBuy = Math.floor(amount / property.sharePrice)
        if (sharesToBuy <= 0) return false

        // Update holdings
        setHoldings(prev => {
            const existing = prev.find(h => h.propertyId === property.id)
            if (existing) {
                return prev.map(h => h.propertyId === property.id
                    ? { ...h, shares: h.shares + sharesToBuy }
                    : h)
            } else {
                return [...prev, {
                    propertyId: property.id,
                    name: property.name,
                    shares: sharesToBuy,
                    totalShares: property.totalShares,
                    sharePrice: property.sharePrice,
                    yield: property.yield,
                    claimableRent: 0,
                    totalClaimed: 0,
                    status: 'ACTIVE'
                }]
            }
        })

        // Update property stats (mock)
        setProperties(prev => prev.map(p => p.id === Number(propertyId)
            ? { ...p, sharesSold: Math.min(p.sharesSold + sharesToBuy, p.totalShares) }
            : p))

        return true
    }

    // Buy shares of a property (by quantity)
    const buyShares = (propertyId, qty) => {
        const property = properties.find(p => p.id === Number(propertyId))
        if (!property || qty <= 0) return false

        // Update holdings
        setHoldings(prev => {
            const existing = prev.find(h => h.propertyId === property.id)
            if (existing) {
                return prev.map(h => h.propertyId === property.id
                    ? { ...h, shares: h.shares + qty }
                    : h)
            } else {
                return [...prev, {
                    propertyId: property.id,
                    name: property.name,
                    shares: qty,
                    totalShares: property.totalShares,
                    sharePrice: property.sharePrice,
                    yield: property.yield,
                    claimableRent: 0,
                    totalClaimed: 0,
                    status: 'ACTIVE'
                }]
            }
        })

        // Update property stats
        setProperties(prev => prev.map(p => p.id === Number(propertyId)
            ? { ...p, sharesSold: Math.min(p.sharesSold + qty, p.totalShares) }
            : p))

        return true
    }

    // List a new property
    const listProperty = (newProp) => {
        const id = properties.length + 1
        const propWithId = { ...newProp, id, status: 0, verificationStatus: 'PENDING', documents: {} }
        setProperties(prev => [...prev, propWithId])
        return id
    }

    // Claim rent for a holding
    const claimRent = (propertyId) => {
        setHoldings(prev => prev.map(h => {
            if (h.propertyId === propertyId) {
                setBalance(b => b + h.claimableRent)
                return { ...h, totalClaimed: h.totalClaimed + h.claimableRent, claimableRent: 0 }
            }
            return h
        }))
    }

    // Get properties listed by the current user (mock: pending ones or specific IDs)
    const getListedProperties = () => {
        // Return properties that are in 'Pending' state or added dynamically
        return properties.filter(p => p.status === 0 || p.id > 20)
    }

    // Vote on a proposal
    const vote = (proposalId, support) => {
        setProposals(prev => prev.map(p => {
            if (p.id === proposalId) {
                return {
                    ...p,
                    yesWeight: support ? p.yesWeight + 100 : p.yesWeight,
                    noWeight: !support ? p.noWeight + 100 : p.noWeight
                }
            }
            return p
        }))
    }

    return (
        <DemoContext.Provider value={{
            properties,
            holdings,
            proposals,
            balance,
            invest,
            buyShares,
            listProperty,
            claimRent,
            getListedProperties,
            vote
        }}>
            {children}
        </DemoContext.Provider>
    )
}

export const useDemoStore = () => {
    const context = useContext(DemoContext)
    if (!context) {
        throw new Error('useDemoStore must be used within a DemoProvider')
    }
    return context
}
