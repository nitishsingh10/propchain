import { useState, useMemo } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useDemoStore } from '../utils/demoStore'
import { STATUS_MAP, formatINR } from '../utils/mockData'
import { MultiPropertyMap } from '../components/PropertyMap'

const SORT_OPTIONS = [
    { key: 'default', label: 'Default' },
    { key: 'yield', label: 'Highest Yield' },
    { key: 'price-low', label: 'Price: Low → High' },
    { key: 'price-high', label: 'Price: High → Low' },
    { key: 'funding', label: 'Most Funded' },
]

export default function MarketplacePage() {
    const { properties } = useDemoStore()
    const navigate = useNavigate()
    const [filter, setFilter] = useState('all')
    const [search, setSearch] = useState('')
    const [sort, setSort] = useState('default')
    const [viewMode, setViewMode] = useState('grid') // grid | map

    const filtered = useMemo(() => {
        let list = properties

        // Filter by status
        if (filter === 'active') list = list.filter(p => p.status === 3)
        else if (filter === 'pending') list = list.filter(p => p.status === 0)
        else if (filter === 'sold') list = list.filter(p => p.status === 4)

        // Search
        if (search.trim()) {
            const q = search.toLowerCase()
            list = list.filter(p =>
                p.name.toLowerCase().includes(q) || p.location.toLowerCase().includes(q)
            )
        }

        // Sort
        if (sort === 'yield') list = [...list].sort((a, b) => b.yield - a.yield)
        else if (sort === 'price-low') list = [...list].sort((a, b) => a.sharePrice - b.sharePrice)
        else if (sort === 'price-high') list = [...list].sort((a, b) => b.sharePrice - a.sharePrice)
        else if (sort === 'funding') list = [...list].sort((a, b) => (b.sharesSold / b.totalShares) - (a.sharesSold / a.totalShares))

        return list
    }, [properties, filter, search, sort])

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-12 animate-fade-in">
            {/* Header */}
            <div className="flex flex-col gap-4 mb-8">
                <div>
                    <h1 className="text-3xl font-bold">Property <span className="gradient-text">Marketplace</span></h1>
                    <p className="text-white/50 mt-1">Discover AI-verified investment opportunities</p>
                </div>

                {/* Search + Sort */}
                <div className="flex flex-col sm:flex-row gap-3">
                    <div className="relative flex-1">
                        <span className="absolute left-4 top-1/2 -translate-y-1/2 text-white/30 text-sm">⌕</span>
                        <input
                            type="text" placeholder="Search properties..." value={search}
                            onChange={e => setSearch(e.target.value)}
                            className="input-field !pl-11" />
                    </div>
                    <select value={sort} onChange={e => setSort(e.target.value)}
                        className="input-field !w-auto sm:min-w-[180px]">
                        {SORT_OPTIONS.map(o => <option key={o.key} value={o.key}>{o.label}</option>)}
                    </select>
                </div>

                {/* Filter tabs */}
                <div className="flex gap-2 flex-wrap">
                    {['all', 'active', 'pending', 'sold'].map(f => (
                        <button key={f} onClick={() => setFilter(f)}
                            className={`px-4 py-2 rounded-lg text-sm font-medium capitalize transition-all ${filter === f ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30' : 'bg-white/5 text-white/50 hover:bg-white/10'
                                }`}>{f}</button>
                    ))}
                    <span className="text-sm text-white/30 flex items-center ml-2">{filtered.length} properties</span>
                    {/* View Toggle */}
                    <div className="ml-auto flex gap-1 bg-white/5 rounded-lg p-0.5">
                        <button onClick={() => setViewMode('grid')}
                            className={`px-3 py-1.5 rounded-md text-sm transition-all ${viewMode === 'grid' ? 'bg-primary-500/20 text-primary-400' : 'text-white/40 hover:text-white/60'}`}>
                            ▦ Grid
                        </button>
                        <button onClick={() => setViewMode('map')}
                            className={`px-3 py-1.5 rounded-md text-sm transition-all ${viewMode === 'map' ? 'bg-primary-500/20 text-primary-400' : 'text-white/40 hover:text-white/60'}`}>
                            🗺️ Map
                        </button>
                    </div>
                </div>
            </div>

            {/* Content */}
            {filtered.length === 0 ? (
                <div className="text-center py-20">
                    <h3 className="text-lg font-semibold mb-2">No properties found</h3>
                    <p className="text-white/35 text-sm">Try adjusting your search or filters</p>
                </div>
            ) : viewMode === 'map' ? (
                <div className="animate-fade-in">
                    <MultiPropertyMap
                        properties={filtered}
                        onPropertyClick={(p) => navigate(`/property/${p.id}`)}
                    />
                    <p className="text-xs text-white/30 mt-2 text-center">Click a marker for details • Scroll to zoom</p>
                </div>
            ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 stagger-children">
                    {filtered.map(p => {
                        const fundingPct = (p.sharesSold / p.totalShares) * 100
                        return (
                            <Link key={p.id} to={`/property/${p.id}`}
                                className="glass-card hover:bg-white/[0.08] transition-all duration-300 group overflow-hidden hover:shadow-xl hover:shadow-primary-500/5 hover:-translate-y-1">
                                <div className="h-44 relative overflow-hidden">
                                    {p.images && p.images.length > 0 ? (
                                        <img src={p.images[0]} alt={p.name} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" loading="lazy" />
                                    ) : (
                                        <div className="w-full h-full bg-gradient-to-br from-white/5 to-white/0 flex items-center justify-center text-5xl group-hover:scale-110 transition-transform duration-500">
                                            {p.image}
                                        </div>
                                    )}
                                    <div className="absolute inset-0 bg-gradient-to-t from-dark-950/70 via-transparent to-transparent" />
                                    <div className="absolute top-3 right-3">
                                        <span className={STATUS_MAP[p.status]?.badge || 'badge-pending'}>
                                            {STATUS_MAP[p.status]?.label || 'Unknown'}
                                        </span>
                                    </div>
                                    {p.images && p.images.length > 1 && (
                                        <div className="absolute bottom-2 right-2 px-2 py-0.5 rounded-md bg-black/50 text-[10px] text-white/70 backdrop-blur-sm">
                                            {p.images.length} photos
                                        </div>
                                    )}
                                </div>
                                <div className="p-5">
                                    <h3 className="font-semibold text-lg leading-tight mb-1">{p.name}</h3>
                                    <p className="text-sm text-white/35 mb-4">
                                        {p.location.split(',').slice(0, 2).join(',')}
                                    </p>
                                    <div className="grid grid-cols-3 gap-3 text-center">
                                        <div>
                                            <div className="text-sm font-semibold text-primary-400">{formatINR(p.sharePrice)}</div>
                                            <div className="text-xs text-white/40">Per Share</div>
                                        </div>
                                        <div>
                                            <div className="text-sm font-semibold text-primary-200">{p.yield > 0 ? `${p.yield}%` : '—'}</div>
                                            <div className="text-xs text-white/40">Est. Yield</div>
                                        </div>
                                        <div>
                                            <div className="text-sm font-semibold text-white/80">{fundingPct.toFixed(0)}%</div>
                                            <div className="text-xs text-white/40">Funded</div>
                                        </div>
                                    </div>
                                    <div className="mt-4 h-1 bg-white/[0.06] rounded-full overflow-hidden">
                                        <div className="h-full bg-gradient-to-r from-primary-500 to-primary-200 rounded-full progress-animate"
                                            style={{ width: `${fundingPct}%` }} />
                                    </div>
                                </div>
                            </Link>
                        )
                    })}
                </div>
            )}
        </div>
    )
}
