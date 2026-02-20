import { useEffect, useRef, useState } from 'react'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { formatINR, formatValuation } from '../utils/mockData'

// Fix Leaflet's default icon path issue with bundlers
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

const STATUS_COLORS = {
    3: '#22c55e',
    0: '#f59e0b',
    4: '#6b7280',
}

function createIcon(color = '#6C63FF', size = 32) {
    return L.divIcon({
        className: 'custom-map-marker',
        html: `<div style="
            width: ${size}px; height: ${size}px; border-radius: 50% 50% 50% 0;
            background: ${color}; border: 3px solid white;
            transform: rotate(-45deg); position: relative;
            box-shadow: 0 4px 12px rgba(0,0,0,0.4);
            animation: markerDrop 0.4s ease-out;
        "><div style="
            width: ${size * 0.3}px; height: ${size * 0.3}px; background: white; border-radius: 50%;
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
        "></div></div>`,
        iconSize: [size, size],
        iconAnchor: [size / 2, size],
        popupAnchor: [0, -size],
    })
}

function createPulseIcon(color = '#6C63FF') {
    return L.divIcon({
        className: 'custom-map-marker',
        html: `<div style="position: relative; width: 40px; height: 40px;">
            <div style="
                width: 40px; height: 40px; border-radius: 50%;
                background: ${color}33;
                animation: pulse-ring 1.5s ease-out infinite;
                position: absolute; top: 0; left: 0;
            "></div>
            <div style="
                width: 18px; height: 18px; border-radius: 50%;
                background: ${color}; border: 3px solid white;
                box-shadow: 0 2px 8px rgba(0,0,0,0.4);
                position: absolute; top: 11px; left: 11px;
            "></div>
        </div>`,
        iconSize: [40, 40],
        iconAnchor: [20, 20],
        popupAnchor: [0, -20],
    })
}

function makePopup(p, clickable = false) {
    const imgHtml = p.images && p.images.length > 0
        ? `<img src="${p.images[0]}" alt="${p.name}" style="width:100%; height:100px; object-fit:cover; border-radius:8px; margin-bottom:8px;" />`
        : ''

    const statusLabel = p.status === 3 ? 'Active' : p.status === 0 ? 'Pending' : 'Sold'
    const statusColor = STATUS_COLORS[p.status] || '#6C63FF'

    return `
        <div style="font-family: Inter, -apple-system, sans-serif; min-width: 220px; max-width: 260px; ${clickable ? 'cursor:pointer;' : ''}">
            ${imgHtml}
            <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:4px;">
                <strong style="font-size:14px; line-height:1.3;">${p.name}</strong>
                <span style="font-size:10px; padding:2px 8px; border-radius:8px; background:${statusColor}22; color:${statusColor}; font-weight:600; white-space:nowrap; margin-left:8px;">${statusLabel}</span>
            </div>
            <div style="font-size:12px; color:#999; margin-bottom:8px;">📍 ${p.location}</div>
            <div style="display:flex; gap:12px; padding-top:6px; border-top:1px solid rgba(255,255,255,0.1);">
                <div>
                    <div style="font-size:13px; color:#6C63FF; font-weight:600;">${formatINR(p.sharePrice)}</div>
                    <div style="font-size:10px; color:#999;">Per Share</div>
                </div>
                <div>
                    <div style="font-size:13px; color:#10b981; font-weight:600;">${p.yield > 0 ? `${p.yield}%` : '—'}</div>
                    <div style="font-size:10px; color:#999;">Yield</div>
                </div>
                <div>
                    <div style="font-size:13px; font-weight:600;">${formatValuation(p.valuation)}</div>
                    <div style="font-size:10px; color:#999;">Value</div>
                </div>
            </div>
            ${clickable ? '<div style="margin-top:8px; font-size:11px; color:#6C63FF; font-weight:500; text-align:center; padding:4px; background:rgba(108,99,255,0.08); border-radius:6px;">View Details →</div>' : ''}
        </div>`
}

// Tile layers for toggling
const TILE_LAYERS = {
    street: {
        url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        label: 'Street',
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    },
    satellite: {
        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        label: 'Satellite',
        attribution: '&copy; Esri, Maxar, Earthstar',
    },
}

/**
 * Single property map — detail page
 */
export function SinglePropertyMap({ property, className = '' }) {
    const mapRef = useRef(null)
    const mapInstance = useRef(null)

    useEffect(() => {
        if (!property?.lat || !property?.lng || !mapRef.current) return
        if (mapInstance.current) return

        const map = L.map(mapRef.current, {
            scrollWheelZoom: false,
            zoomControl: true,
        }).setView([property.lat, property.lng], 16)

        // Add layer control (street + satellite)
        const streetLayer = L.tileLayer(TILE_LAYERS.street.url, { attribution: TILE_LAYERS.street.attribution })
        const satLayer = L.tileLayer(TILE_LAYERS.satellite.url, { attribution: TILE_LAYERS.satellite.attribution })
        streetLayer.addTo(map)

        L.control.layers(
            { [TILE_LAYERS.street.label]: streetLayer, [TILE_LAYERS.satellite.label]: satLayer },
            null,
            { position: 'topright', collapsed: true }
        ).addTo(map)

        // Marker with pulse effect for single property
        const marker = L.marker([property.lat, property.lng], {
            icon: createPulseIcon(STATUS_COLORS[property.status] || '#6C63FF'),
        }).addTo(map)

        marker.bindPopup(makePopup(property), { maxWidth: 280, className: 'custom-popup' })
        marker.openPopup()

        mapInstance.current = map
        setTimeout(() => map.invalidateSize(), 100)

        return () => {
            map.remove()
            mapInstance.current = null
        }
    }, [property])

    if (!property?.lat || !property?.lng) return null

    return (
        <div
            ref={mapRef}
            className={`rounded-xl overflow-hidden border border-white/10 ${className}`}
            style={{ height: '300px', background: '#0a0a19' }}
        />
    )
}

/**
 * Multi-property map — marketplace page
 */
export function MultiPropertyMap({ properties, className = '', onPropertyClick }) {
    const mapRef = useRef(null)
    const mapInstance = useRef(null)

    useEffect(() => {
        const valid = properties.filter(p => p.lat && p.lng)
        if (valid.length === 0 || !mapRef.current) return

        if (mapInstance.current) {
            mapInstance.current.remove()
            mapInstance.current = null
        }

        const center = [
            valid.reduce((s, p) => s + p.lat, 0) / valid.length,
            valid.reduce((s, p) => s + p.lng, 0) / valid.length,
        ]

        const map = L.map(mapRef.current, {
            scrollWheelZoom: true,
            zoomControl: true,
        }).setView(center, 12)

        // Layer toggle
        const streetLayer = L.tileLayer(TILE_LAYERS.street.url, { attribution: TILE_LAYERS.street.attribution })
        const satLayer = L.tileLayer(TILE_LAYERS.satellite.url, { attribution: TILE_LAYERS.satellite.attribution })
        streetLayer.addTo(map)
        L.control.layers(
            { [TILE_LAYERS.street.label]: streetLayer, [TILE_LAYERS.satellite.label]: satLayer },
            null,
            { position: 'topright', collapsed: true }
        ).addTo(map)

        // Stagger marker animations
        valid.forEach((p, i) => {
            setTimeout(() => {
                const marker = L.marker([p.lat, p.lng], {
                    icon: createIcon(STATUS_COLORS[p.status] || '#6C63FF'),
                }).addTo(map)

                marker.bindPopup(makePopup(p, !!onPropertyClick), { maxWidth: 280, className: 'custom-popup' })

                // FlyTo on click
                marker.on('click', () => {
                    map.flyTo([p.lat, p.lng], 14, { duration: 0.8 })
                })

                if (onPropertyClick) {
                    marker.on('popupopen', () => {
                        const popupEl = marker.getPopup().getElement()
                        if (popupEl) {
                            popupEl.querySelector('.leaflet-popup-content').onclick = () => onPropertyClick(p)
                        }
                    })
                }
            }, i * 120) // stagger each marker by 120ms
        })

        const bounds = L.latLngBounds(valid.map(p => [p.lat, p.lng]))
        if (bounds.isValid()) {
            map.fitBounds(bounds, { padding: [50, 50], maxZoom: 14 })
        }

        mapInstance.current = map
        setTimeout(() => map.invalidateSize(), 100)

        return () => {
            map.remove()
            mapInstance.current = null
        }
    }, [properties, onPropertyClick])

    const valid = properties.filter(p => p.lat && p.lng)
    if (valid.length === 0) return null

    return (
        <div
            ref={mapRef}
            className={`rounded-xl overflow-hidden border border-white/10 ${className}`}
            style={{ height: '450px', background: '#0a0a19' }}
        />
    )
}

/**
 * Location Picker Map — for List Property page
 * Shows draggable marker. Map view updates when latLng prop changes.
 * Reverse-geocodes on drag/click to update the address.
 */
export function LocationPickerMap({ latLng, onMapPinChange, className = '' }) {
    const mapRef = useRef(null)
    const mapInstance = useRef(null)
    const markerRef = useRef(null)

    const DEFAULT_LAT = 12.9716
    const DEFAULT_LNG = 77.5946

    // Initialize map once
    useEffect(() => {
        if (!mapRef.current || mapInstance.current) return

        const initLat = latLng?.[0] || DEFAULT_LAT
        const initLng = latLng?.[1] || DEFAULT_LNG

        const map = L.map(mapRef.current, {
            scrollWheelZoom: true,
            zoomControl: true,
        }).setView([initLat, initLng], latLng ? 15 : 12)

        const streetLayer = L.tileLayer(TILE_LAYERS.street.url, { attribution: TILE_LAYERS.street.attribution })
        const satLayer = L.tileLayer(TILE_LAYERS.satellite.url, { attribution: TILE_LAYERS.satellite.attribution })
        streetLayer.addTo(map)
        L.control.layers(
            { [TILE_LAYERS.street.label]: streetLayer, [TILE_LAYERS.satellite.label]: satLayer },
            null,
            { position: 'topright', collapsed: true }
        ).addTo(map)

        const marker = L.marker([initLat, initLng], {
            draggable: true,
            icon: createIcon('#6C63FF', 36),
        }).addTo(map)

        marker.bindPopup('<div style="font-family: Inter, sans-serif; font-size:13px; color:#999;">📍 Drag me or click the map</div>')
        marker.openPopup()

        // Reverse-geocode helper
        const reverseGeocode = async (lat, lng) => {
            try {
                const res = await fetch(
                    `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json&addressdetails=1`,
                    { headers: { 'Accept-Language': 'en' } }
                )
                const data = await res.json()
                if (data.display_name) {
                    const a = data.address || {}
                    const shortAddr = [
                        a.neighbourhood || a.suburb || a.hamlet || '',
                        a.city || a.town || a.village || '',
                        a.state || '',
                    ].filter(Boolean).join(', ')
                    const label = shortAddr || data.display_name
                    marker.bindPopup(`<div style="font-family: Inter, sans-serif; font-size:13px;"><strong>📍 ${label}</strong><br/><span style="color:#999; font-size:11px;">Lat: ${lat.toFixed(4)}° Lng: ${lng.toFixed(4)}°</span></div>`).openPopup()
                    onMapPinChange?.(label, lat, lng)
                    return
                }
            } catch { /* ignore */ }
            onMapPinChange?.('', lat, lng)
        }

        marker.on('dragend', () => {
            const { lat, lng } = marker.getLatLng()
            reverseGeocode(lat, lng)
        })

        map.on('click', (e) => {
            marker.setLatLng(e.latlng)
            reverseGeocode(e.latlng.lat, e.latlng.lng)
        })

        markerRef.current = marker
        mapInstance.current = map
        setTimeout(() => map.invalidateSize(), 100)

        return () => {
            map.remove()
            mapInstance.current = null
            markerRef.current = null
        }
    }, []) // eslint-disable-line react-hooks/exhaustive-deps

    // Fly to new coordinates when parent pushes them (e.g. from autocomplete selection)
    useEffect(() => {
        if (!latLng || !mapInstance.current || !markerRef.current) return
        const [lat, lng] = latLng
        if (!lat || !lng) return

        mapInstance.current.flyTo([lat, lng], 16, { duration: 1 })
        markerRef.current.setLatLng([lat, lng])
        markerRef.current
            .bindPopup(`<div style="font-family: Inter, sans-serif; font-size:13px;"><strong>📍 Selected</strong><br/><span style="color:#999; font-size:11px;">Lat: ${lat.toFixed(4)}° Lng: ${lng.toFixed(4)}°</span></div>`)
            .openPopup()
    }, [latLng?.[0], latLng?.[1]]) // eslint-disable-line react-hooks/exhaustive-deps

    return (
        <div className={`space-y-2 ${className}`}>
            <div
                ref={mapRef}
                className="rounded-xl overflow-hidden border border-white/10"
                style={{ height: '250px', background: '#0a0a19' }}
            />
            <p className="text-xs text-white/30 text-center">
                Click the map or drag the pin to set exact location
            </p>
        </div>
    )
}

/**
 * Address Autocomplete — debounced Nominatim search with dropdown suggestions
 */
export function AddressAutocomplete({ value, onChange, onSelect, placeholder, className = '', error }) {
    const [suggestions, setSuggestions] = useState([])
    const [showDropdown, setShowDropdown] = useState(false)
    const [activeIdx, setActiveIdx] = useState(-1)
    const [loading, setLoading] = useState(false)
    const debounceRef = useRef(null)
    const wrapperRef = useRef(null)

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClick = (e) => {
            if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
                setShowDropdown(false)
            }
        }
        document.addEventListener('mousedown', handleClick)
        return () => document.removeEventListener('mousedown', handleClick)
    }, [])

    const search = (query) => {
        if (debounceRef.current) clearTimeout(debounceRef.current)
        if (!query || query.length < 2) {
            setSuggestions([])
            setShowDropdown(false)
            return
        }

        setLoading(true)
        debounceRef.current = setTimeout(async () => {
            try {
                const q = encodeURIComponent(query + ', India')
                const res = await fetch(
                    `https://nominatim.openstreetmap.org/search?q=${q}&format=json&limit=5&addressdetails=1`,
                    { headers: { 'Accept-Language': 'en' } }
                )
                const data = await res.json()
                const results = data.map(item => {
                    const a = item.address || {}
                    const short = [
                        a.neighbourhood || a.suburb || a.hamlet || '',
                        a.city || a.town || a.village || '',
                        a.state || '',
                    ].filter(Boolean).join(', ')
                    return {
                        display: short || item.display_name,
                        full: item.display_name,
                        lat: parseFloat(item.lat),
                        lng: parseFloat(item.lon),
                    }
                })
                setSuggestions(results)
                setShowDropdown(results.length > 0)
                setActiveIdx(-1)
            } catch {
                setSuggestions([])
                setShowDropdown(false)
            } finally {
                setLoading(false)
            }
        }, 400)
    }

    const handleInputChange = (e) => {
        const val = e.target.value
        onChange(val)
        search(val)
    }

    const handleSelect = (suggestion) => {
        onChange(suggestion.display)
        onSelect(suggestion.display, suggestion.lat, suggestion.lng)
        setShowDropdown(false)
        setSuggestions([])
    }

    const handleKeyDown = (e) => {
        if (!showDropdown || suggestions.length === 0) return

        if (e.key === 'ArrowDown') {
            e.preventDefault()
            setActiveIdx(prev => (prev < suggestions.length - 1 ? prev + 1 : 0))
        } else if (e.key === 'ArrowUp') {
            e.preventDefault()
            setActiveIdx(prev => (prev > 0 ? prev - 1 : suggestions.length - 1))
        } else if (e.key === 'Enter' && activeIdx >= 0) {
            e.preventDefault()
            handleSelect(suggestions[activeIdx])
        } else if (e.key === 'Escape') {
            setShowDropdown(false)
        }
    }

    return (
        <div ref={wrapperRef} className="relative">
            <div className="relative">
                <input
                    className={`input-field pr-8 ${error ? '!border-red-500/50' : ''} ${className}`}
                    placeholder={placeholder}
                    value={value}
                    onChange={handleInputChange}
                    onKeyDown={handleKeyDown}
                    onFocus={() => { if (suggestions.length > 0) setShowDropdown(true) }}
                    autoComplete="off"
                />
                {loading && (
                    <div className="absolute right-3 top-1/2 -translate-y-1/2">
                        <div className="w-4 h-4 border-2 border-primary-500 border-t-transparent rounded-full spin" />
                    </div>
                )}
                {!loading && value && (
                    <div className="absolute right-3 top-1/2 -translate-y-1/2 text-white/20 text-xs">
                        🔍
                    </div>
                )}
            </div>

            {showDropdown && suggestions.length > 0 && (
                <div className="absolute z-[9999] w-full mt-1 bg-[#1a1a2e] border border-white/10 rounded-xl shadow-2xl overflow-hidden max-h-[220px] overflow-y-auto">
                    {suggestions.map((s, i) => (
                        <button
                            key={i}
                            className={`w-full text-left px-4 py-3 text-sm transition-colors border-b border-white/5 last:border-0 ${i === activeIdx
                                ? 'bg-primary-500/20 text-white'
                                : 'text-white/70 hover:bg-white/5 hover:text-white'
                                }`}
                            onClick={() => handleSelect(s)}
                            onMouseEnter={() => setActiveIdx(i)}
                        >
                            <div className="flex items-start gap-2">
                                <span className="text-primary-400 mt-0.5 shrink-0">📍</span>
                                <div className="min-w-0">
                                    <div className="font-medium text-[13px] truncate">{s.display}</div>
                                    <div className="text-[11px] text-white/30 truncate">{s.full}</div>
                                </div>
                            </div>
                        </button>
                    ))}
                </div>
            )}
        </div>
    )
}

