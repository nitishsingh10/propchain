/**
 * PropChain — Centralized Demo Data Store
 * All pages reference this shared data so actions (buy, vote, claim, list) persist across navigation.
 */

export const PROPERTIES = [
    {
        id: 1, name: 'TechPark Warehouse, Bengaluru', location: 'Whitefield, Bengaluru, Karnataka',
        lat: 12.9698, lng: 77.7500,
        valuation: 50000000, sharePrice: 5000, totalShares: 10000, sharesSold: 7800, status: 3,
        yield: 8.5, minInvestment: 100, maxInvestment: 3000, insuranceRate: 1.5, image: '🏭',
        propertyType: 'Commercial', description: 'Modern warehouse facility in the heart of Whitefield tech corridor with 24/7 security, loading docks, and premium tenants including logistics companies.',
        images: [
            'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=800&h=500&fit=crop',
            'https://images.unsplash.com/photo-1553877522-43269d4ea984?w=800&h=500&fit=crop',
            'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800&h=500&fit=crop',
        ],
        spv: { cin: 'U70100KA2024PTC123456', pan: 'AADCP1234R', status: 'ACTIVE' },
        documents: { saleDeed: '✅ Verified', ec: '✅ Clean (13yr)', taxReceipt: '✅ No dues', aadhaar: '✅ Matched' },
        aiScore: 92, verificationStatus: 'APPROVED',
    },
    {
        id: 2, name: 'HSR Layout Villa, Bengaluru', location: 'HSR Layout, Bengaluru, Karnataka',
        lat: 12.9116, lng: 77.6474,
        valuation: 25000000, sharePrice: 2500, totalShares: 10000, sharesSold: 4200, status: 3,
        yield: 6.2, minInvestment: 50, maxInvestment: 5000, insuranceRate: 1.5, image: '🏡',
        propertyType: 'Residential', description: 'Luxurious 4BHK villa with rooftop garden, private pool, and smart home features in the premium HSR Layout neighborhood.',
        images: [
            'https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=800&h=500&fit=crop',
            'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&h=500&fit=crop',
            'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800&h=500&fit=crop',
        ],
        spv: { cin: 'U70100KA2024PTC234567', pan: 'AADCP2345S', status: 'ACTIVE' },
        documents: { saleDeed: '✅ Verified', ec: '✅ Clean (8yr)', taxReceipt: '✅ No dues', aadhaar: '✅ Matched' },
        aiScore: 88, verificationStatus: 'APPROVED',
    },
    {
        id: 3, name: 'MG Road Office Space', location: 'MG Road, Bengaluru, Karnataka',
        lat: 12.9756, lng: 77.6066,
        valuation: 80000000, sharePrice: 8000, totalShares: 10000, sharesSold: 9500, status: 3,
        yield: 9.1, minInvestment: 50, maxInvestment: 2000, insuranceRate: 1.5, image: '🏢',
        propertyType: 'Commercial', description: 'Premium Grade-A office space on MG Road with panoramic city views, fiber connectivity, and Fortune 500 tenants on long-term leases.',
        images: [
            'https://images.unsplash.com/photo-1497366216548-37526070297c?w=800&h=500&fit=crop',
            'https://images.unsplash.com/photo-1497366811353-6870744d04b2?w=800&h=500&fit=crop',
            'https://images.unsplash.com/photo-1524758631624-e2822e304c36?w=800&h=500&fit=crop',
        ],
        spv: { cin: 'U70100KA2024PTC345678', pan: 'AADCP3456T', status: 'ACTIVE' },
        documents: { saleDeed: '✅ Verified', ec: '✅ Clean (20yr)', taxReceipt: '✅ No dues', aadhaar: '✅ Matched' },
        aiScore: 96, verificationStatus: 'APPROVED',
    },
    {
        id: 4, name: 'Indiranagar Retail Unit', location: 'Indiranagar, Bengaluru, Karnataka',
        lat: 12.9784, lng: 77.6408,
        valuation: 15000000, sharePrice: 1500, totalShares: 10000, sharesSold: 1200, status: 3,
        yield: 7.3, minInvestment: 100, maxInvestment: 5000, insuranceRate: 1.5, image: '🏪',
        propertyType: 'Retail', description: 'High-footfall retail space on 100 Feet Road with established F&B tenants and premium brand neighbors. Ideal for steady rental income.',
        images: [
            'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800&h=500&fit=crop',
            'https://images.unsplash.com/photo-1604719312566-8912e9227c6a?w=800&h=500&fit=crop',
        ],
        spv: { cin: 'U70100KA2024PTC456789', pan: 'AADCP4567U', status: 'ACTIVE' },
        documents: { saleDeed: '✅ Verified', ec: '✅ Clean (5yr)', taxReceipt: '✅ No dues', aadhaar: '✅ Matched' },
        aiScore: 85, verificationStatus: 'APPROVED',
    },
    {
        id: 5, name: 'Koramangala Co-Working', location: 'Koramangala, Bengaluru, Karnataka',
        lat: 12.9352, lng: 77.6245,
        valuation: 35000000, sharePrice: 3500, totalShares: 10000, sharesSold: 0, status: 0,
        yield: 0, minInvestment: 100, maxInvestment: 3000, insuranceRate: 1.5, image: '🏗️',
        propertyType: 'Commercial', description: 'Under-construction co-working hub in Koramangala targeting startup ecosystem. Expected completion Q4 2026.',
        images: [
            'https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=800&h=500&fit=crop',
        ],
        spv: { cin: 'U70100KA2024PTC567890', pan: 'AADCP5678V', status: 'PENDING' },
        documents: { saleDeed: '⏳ Processing', ec: '⏳ Processing', taxReceipt: '⏳ Processing', aadhaar: '⏳ Processing' },
        aiScore: 0, verificationStatus: 'PENDING',
    },
    {
        id: 6, name: 'Electronic City Plot', location: 'Electronic City, Bengaluru, Karnataka',
        lat: 12.8399, lng: 77.6770,
        valuation: 120000000, sharePrice: 12000, totalShares: 10000, sharesSold: 10000, status: 4,
        yield: 10.2, minInvestment: 100, maxInvestment: 1000, insuranceRate: 1.5, image: '🏞️',
        propertyType: 'Land', description: 'Prime 2-acre plot adjacent to Infosys campus in Electronic City Phase 1. Fully sold out – now generating rental returns from temporary leases.',
        images: [
            'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800&h=500&fit=crop',
            'https://images.unsplash.com/photo-1628624747186-a941c476b7ef?w=800&h=500&fit=crop',
        ],
        spv: { cin: 'U70100KA2024PTC678901', pan: 'AADCP6789W', status: 'WOUND_UP' },
        documents: { saleDeed: '✅ Verified', ec: '✅ Clean (15yr)', taxReceipt: '✅ No dues', aadhaar: '✅ Matched' },
        aiScore: 94, verificationStatus: 'APPROVED',
    },
    {
        id: 7, name: 'Bandra Sea-View Penthouse', location: 'Bandra West, Mumbai, Maharashtra',
        lat: 19.0596, lng: 72.8295,
        valuation: 150000000, sharePrice: 15000, totalShares: 10000, sharesSold: 6400, status: 3,
        yield: 7.8, minInvestment: 200, maxInvestment: 2000, insuranceRate: 1.8, image: '🏙️',
        propertyType: 'Residential', description: 'Ultra-luxury 5BHK penthouse with Arabian Sea views, private terrace, infinity pool, and dedicated concierge in Bandra\'s most exclusive tower.',
        images: [
            'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&h=500&fit=crop',
            'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&h=500&fit=crop',
            'https://images.unsplash.com/photo-1613977257363-707ba9348227?w=800&h=500&fit=crop',
        ],
        spv: { cin: 'U70100MH2024PTC789012', pan: 'AADCP7890X', status: 'ACTIVE' },
        documents: { saleDeed: '✅ Verified', ec: '✅ Clean (10yr)', taxReceipt: '✅ No dues', aadhaar: '✅ Matched' },
        aiScore: 91, verificationStatus: 'APPROVED',
    },
    {
        id: 8, name: 'Connaught Place Retail', location: 'Connaught Place, New Delhi',
        lat: 28.6315, lng: 77.2167,
        valuation: 200000000, sharePrice: 20000, totalShares: 10000, sharesSold: 8800, status: 3,
        yield: 11.5, minInvestment: 500, maxInvestment: 1500, insuranceRate: 2.0, image: '🏬',
        propertyType: 'Retail', description: 'Iconic ground-floor showroom in Block A, Connaught Place. Triple-height ceiling, 4,200 sqft carpet area, leased to a luxury international brand.',
        images: [
            'https://images.unsplash.com/photo-1567449303078-57ad995bd329?w=800&h=500&fit=crop',
            'https://images.unsplash.com/photo-1555529733-211c56f52754?w=800&h=500&fit=crop',
        ],
        spv: { cin: 'U70100DL2024PTC890123', pan: 'AADCP8901Y', status: 'ACTIVE' },
        documents: { saleDeed: '✅ Verified', ec: '✅ Clean (25yr)', taxReceipt: '✅ No dues', aadhaar: '✅ Matched' },
        aiScore: 97, verificationStatus: 'APPROVED',
    },
    {
        id: 9, name: 'HITEC City IT Tower', location: 'HITEC City, Hyderabad, Telangana',
        lat: 17.4435, lng: 78.3772,
        valuation: 95000000, sharePrice: 9500, totalShares: 10000, sharesSold: 5100, status: 3,
        yield: 9.8, minInvestment: 100, maxInvestment: 3000, insuranceRate: 1.5, image: '🏢',
        propertyType: 'Commercial', description: 'Full-floor IT office in a SEZ tower at HITEC City. Pre-leased to a Fortune 100 tech company with a 9-year lock-in. 32,000 sqft built-up area.',
        images: [
            'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&h=500&fit=crop',
            'https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=800&h=500&fit=crop',
        ],
        spv: { cin: 'U70100TG2024PTC901234', pan: 'AADCP9012Z', status: 'ACTIVE' },
        documents: { saleDeed: '✅ Verified', ec: '✅ Clean (12yr)', taxReceipt: '✅ No dues', aadhaar: '✅ Matched' },
        aiScore: 93, verificationStatus: 'APPROVED',
    },
    {
        id: 10, name: 'OMR Residential Complex', location: 'Old Mahabalipuram Road, Chennai, TN',
        lat: 12.9165, lng: 80.2271,
        valuation: 40000000, sharePrice: 4000, totalShares: 10000, sharesSold: 3200, status: 3,
        yield: 6.8, minInvestment: 50, maxInvestment: 5000, insuranceRate: 1.3, image: '🏘️',
        propertyType: 'Residential', description: '48-unit gated community on OMR IT corridor with clubhouse, swimming pool, gym, and 24/7 security. Fully occupied with IT professionals.',
        images: [
            'https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=800&h=500&fit=crop',
            'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&h=500&fit=crop',
        ],
        spv: { cin: 'U70100TN2024PTC012345', pan: 'AADCP0123A', status: 'ACTIVE' },
        documents: { saleDeed: '✅ Verified', ec: '✅ Clean (7yr)', taxReceipt: '✅ No dues', aadhaar: '✅ Matched' },
        aiScore: 86, verificationStatus: 'APPROVED',
    },
    {
        id: 11, name: 'Hinjewadi Tech Park Land', location: 'Hinjewadi, Pune, Maharashtra',
        lat: 18.5912, lng: 73.7390,
        valuation: 70000000, sharePrice: 7000, totalShares: 10000, sharesSold: 0, status: 0,
        yield: 0, minInvestment: 100, maxInvestment: 4000, insuranceRate: 1.5, image: '🏞️',
        propertyType: 'Land', description: '5-acre development plot near Hinjewadi IT Park Phase 3. Zoned for mixed-use. Environmental clearance obtained. Expected 3x appreciation in 5 years.',
        images: [
            'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800&h=500&fit=crop',
        ],
        spv: { cin: 'U70100MH2024PTC112233', pan: 'AADCP1122B', status: 'PENDING' },
        documents: { saleDeed: '⏳ Processing', ec: '⏳ Processing', taxReceipt: '✅ No dues', aadhaar: '✅ Matched' },
        aiScore: 0, verificationStatus: 'PENDING',
    },
    {
        id: 12, name: 'Candolim Beach Resort', location: 'Candolim, North Goa',
        lat: 15.5177, lng: 73.7622,
        valuation: 60000000, sharePrice: 6000, totalShares: 10000, sharesSold: 7600, status: 3,
        yield: 12.1, minInvestment: 100, maxInvestment: 2500, insuranceRate: 2.2, image: '🏖️',
        propertyType: 'Mixed Use', description: '12-room boutique beach resort with restaurant, spa, and yoga deck. 200m from Candolim Beach. Peak season occupancy 95%. Revenue-sharing model.',
        images: [
            'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&h=500&fit=crop',
            'https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800&h=500&fit=crop',
            'https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&h=500&fit=crop',
        ],
        spv: { cin: 'U70100GA2024PTC223344', pan: 'AADCP2233C', status: 'ACTIVE' },
        documents: { saleDeed: '✅ Verified', ec: '✅ Clean (18yr)', taxReceipt: '✅ No dues', aadhaar: '✅ Matched' },
        aiScore: 89, verificationStatus: 'APPROVED',
    },
    {
        id: 13, name: 'Jaipur Heritage Haveli', location: 'Amer Road, Jaipur, Rajasthan',
        lat: 26.9535, lng: 75.8514,
        valuation: 30000000, sharePrice: 3000, totalShares: 10000, sharesSold: 4800, status: 3,
        yield: 8.9, minInvestment: 50, maxInvestment: 5000, insuranceRate: 1.8, image: '🏰',
        propertyType: 'Mixed Use', description: 'Restored 200-year-old haveli converted to heritage hotel with 8 luxury suites. Near Amer Fort, rated 4.8★ on travel platforms.',
        images: [
            'https://images.unsplash.com/photo-1587474260584-136574528ed5?w=800&h=500&fit=crop',
            'https://images.unsplash.com/photo-1599661046289-e31897846e41?w=800&h=500&fit=crop',
        ],
        spv: { cin: 'U70100RJ2024PTC334455', pan: 'AADCP3344D', status: 'ACTIVE' },
        documents: { saleDeed: '✅ Verified', ec: '✅ Clean (30yr)', taxReceipt: '✅ No dues', aadhaar: '✅ Matched' },
        aiScore: 87, verificationStatus: 'APPROVED',
    },
    {
        id: 14, name: 'SG Highway Warehouse', location: 'SG Highway, Ahmedabad, Gujarat',
        lat: 23.0225, lng: 72.5714,
        valuation: 45000000, sharePrice: 4500, totalShares: 10000, sharesSold: 6100, status: 3,
        yield: 8.2, minInvestment: 100, maxInvestment: 3000, insuranceRate: 1.4, image: '🏭',
        propertyType: 'Industrial', description: 'Grade-A logistics warehouse on SG Highway with cold-storage facility, 40ft container access, and 3PL tenant on 7-year lease.',
        images: [
            'https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=800&h=500&fit=crop',
            'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800&h=500&fit=crop',
        ],
        spv: { cin: 'U70100GJ2024PTC445566', pan: 'AADCP4455E', status: 'ACTIVE' },
        documents: { saleDeed: '✅ Verified', ec: '✅ Clean (9yr)', taxReceipt: '✅ No dues', aadhaar: '✅ Matched' },
        aiScore: 90, verificationStatus: 'APPROVED',
    },
    {
        id: 15, name: 'Marine Drive Apartment', location: 'Marine Drive, Kochi, Kerala',
        lat: 9.9816, lng: 76.2785,
        valuation: 22000000, sharePrice: 2200, totalShares: 10000, sharesSold: 10000, status: 4,
        yield: 7.1, minInvestment: 50, maxInvestment: 5000, insuranceRate: 1.6, image: '🌊',
        propertyType: 'Residential', description: 'Waterfront 3BHK luxury apartment on Kochi Marine Drive with backwater views, yacht club membership, and smart home automation.',
        images: [
            'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=800&h=500&fit=crop',
            'https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?w=800&h=500&fit=crop',
        ],
        spv: { cin: 'U70100KL2024PTC556677', pan: 'AADCP5566F', status: 'WOUND_UP' },
        documents: { saleDeed: '✅ Verified', ec: '✅ Clean (11yr)', taxReceipt: '✅ No dues', aadhaar: '✅ Matched' },
        aiScore: 88, verificationStatus: 'APPROVED',
    },
    {
        id: 16, name: 'Chandigarh IT Park Office', location: 'IT Park, Chandigarh',
        lat: 30.7046, lng: 76.8011,
        valuation: 55000000, sharePrice: 5500, totalShares: 10000, sharesSold: 2900, status: 3,
        yield: 7.5, minInvestment: 100, maxInvestment: 4000, insuranceRate: 1.3, image: '🏢',
        propertyType: 'Commercial', description: 'Plug-and-play office floor in Chandigarh IT Park Rajiv Gandhi Technology Park. Pre-leased to 3 SaaS startups. 18,000 sqft carpet area.',
        images: [
            'https://images.unsplash.com/photo-1497366811353-6870744d04b2?w=800&h=500&fit=crop',
            'https://images.unsplash.com/photo-1524758631624-e2822e304c36?w=800&h=500&fit=crop',
        ],
        spv: { cin: 'U70100CH2024PTC667788', pan: 'AADCP6677G', status: 'ACTIVE' },
        documents: { saleDeed: '✅ Verified', ec: '✅ Clean (6yr)', taxReceipt: '✅ No dues', aadhaar: '✅ Matched' },
        aiScore: 84, verificationStatus: 'APPROVED',
    },
    {
        id: 17, name: 'Gomti Nagar Mixed-Use', location: 'Gomti Nagar, Lucknow, UP',
        lat: 26.8563, lng: 80.9847,
        valuation: 28000000, sharePrice: 2800, totalShares: 10000, sharesSold: 1800, status: 3,
        yield: 6.5, minInvestment: 50, maxInvestment: 5000, insuranceRate: 1.2, image: '🏗️',
        propertyType: 'Mixed Use', description: 'Ground + 2 mixed-use building in Gomti Nagar Extension. Retail on ground floor, serviced apartments above. High-growth micro-market.',
        images: [
            'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800&h=500&fit=crop',
        ],
        spv: { cin: 'U70100UP2024PTC778899', pan: 'AADCP7788H', status: 'ACTIVE' },
        documents: { saleDeed: '✅ Verified', ec: '✅ Clean (4yr)', taxReceipt: '✅ No dues', aadhaar: '✅ Matched' },
        aiScore: 81, verificationStatus: 'APPROVED',
    },
    {
        id: 18, name: 'Noida Expressway Plot', location: 'Sector 150, Noida, UP',
        lat: 28.4678, lng: 77.5230,
        valuation: 85000000, sharePrice: 8500, totalShares: 10000, sharesSold: 0, status: 0,
        yield: 0, minInvestment: 200, maxInvestment: 2000, insuranceRate: 1.5, image: '🏞️',
        propertyType: 'Land', description: '3-acre prime plot on Noida Expressway near proposed Jewar Airport corridor. RERA registered, clear title. Projected 4x appreciation by 2030.',
        images: [
            'https://images.unsplash.com/photo-1628624747186-a941c476b7ef?w=800&h=500&fit=crop',
        ],
        spv: { cin: 'U70100UP2024PTC889900', pan: 'AADCP8899I', status: 'PENDING' },
        documents: { saleDeed: '⏳ Processing', ec: '⏳ Processing', taxReceipt: '⏳ Processing', aadhaar: '⏳ Processing' },
        aiScore: 0, verificationStatus: 'PENDING',
    },
]

export const INITIAL_PROPOSALS = [
    {
        id: 1, propertyId: 1, type: 'SELL',
        description: 'Sell TechPark Warehouse at 30% premium',
        proposedValue: 65000000, yesWeight: 6800, noWeight: 1200,
        totalShares: 10000, status: 'ACTIVE', deadline: 'Mar 15, 2026',
    },
    {
        id: 2, propertyId: 2, type: 'RENOVATE',
        description: 'Renovate HSR Villa kitchen and exterior',
        proposedValue: 2500000, yesWeight: 7200, noWeight: 800,
        totalShares: 10000, status: 'PASSED', deadline: 'Feb 20, 2026',
    },
    {
        id: 3, propertyId: 3, type: 'CHANGE_RENT',
        description: 'Increase MG Road rent by 15%',
        proposedValue: 1150000, yesWeight: 4500, noWeight: 5500,
        totalShares: 10000, status: 'FAILED', deadline: 'Feb 10, 2026',
    },
]

export const INITIAL_HOLDINGS = [
    { propertyId: 1, name: 'TechPark Warehouse', shares: 500, totalShares: 10000, sharePrice: 5000, yield: 8.5, claimableRent: 12500, totalClaimed: 37500, status: 'ACTIVE' },
    { propertyId: 2, name: 'HSR Layout Villa', shares: 1200, totalShares: 10000, sharePrice: 2500, yield: 6.2, claimableRent: 7200, totalClaimed: 21600, status: 'ACTIVE' },
    { propertyId: 3, name: 'MG Road Office Space', shares: 300, totalShares: 10000, sharePrice: 8000, yield: 9.1, claimableRent: 21000, totalClaimed: 63000, status: 'ACTIVE' },
]

export const PROPERTY_TYPES = ['Residential', 'Commercial', 'Retail', 'Land', 'Industrial', 'Mixed Use']

export const TYPE_ICONS = { SELL: '💰', RENOVATE: '🔧', CHANGE_RENT: '📊', PENALIZE: '⚠️' }

export const STATUS_MAP = {
    0: { label: 'Pending', badge: 'badge-pending' },
    3: { label: 'Active', badge: 'badge-active' },
    4: { label: 'Sold', badge: 'badge-sold' },
}

export function getPropertyById(id) {
    return PROPERTIES.find(p => p.id === Number(id))
}

export function formatINR(num) {
    return `₹${Number(num).toLocaleString('en-IN')}`
}

export function formatValuation(val) {
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(1)}Cr`
    if (val >= 100000) return `₹${(val / 100000).toFixed(0)}L`
    return formatINR(val)
}
