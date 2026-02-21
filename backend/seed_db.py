from database import get_db

mock_properties = [
    {
        "property_id": 1,
        "owner_wallet": "owner_mock_1",
        "property_name": "TechPark Warehouse, Bengaluru",
        "location_hash": "Bengaluru, Karnataka",
        "valuation": 50000000,
        "total_shares": 10000,
        "share_price": 5000,
        "shares_sold": 7900,
        "status": 3,
        "ai_score": 92,
        "verification_status": "APPROVED",
        "min_investment": 10,
        "max_investment": 1000,
        "yield_pct": 8.5,
        "insurance_rate": 1.5,
        "description": "Modern warehouse facility in the heart of Whitefield tech corridor with 24/7 security, loading docks, and premium tenants including logistics companies.",
        "images": '["https://images.unsplash.com/photo-1586528116311-ad8ed7c15902?q=80&w=2670&auto=format&fit=crop", "https://images.unsplash.com/photo-1553413077-190dd305871c?q=80&w=2535&auto=format&fit=crop", "https://images.unsplash.com/photo-1505691938895-1758d7feb511?q=80&w=2670&auto=format&fit=crop"]',
        "lat": 12.9698,
        "lng": 77.7499
    },
    {
        "property_id": 2,
        "owner_wallet": "owner_mock_2",
        "property_name": "HSR Layout Villa, Bengaluru",
        "location_hash": "HSR Layout, Bengaluru",
        "valuation": 25000000,
        "total_shares": 5000,
        "share_price": 5000,
        "shares_sold": 5000,
        "status": 4, # SOLD
        "ai_score": 88,
        "verification_status": "APPROVED",
        "min_investment": 5,
        "max_investment": 500,
        "yield_pct": 6.2,
        "insurance_rate": 1.2,
        "description": "Premium 4BHK villa located in the upscale HSR Layout sector 2. Features include private garden, 2 covered parkings, and smart home automation.",
        "images": '["https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?q=80&w=2675&auto=format&fit=crop", "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?q=80&w=2670&auto=format&fit=crop"]',
        "lat": 12.9081,
        "lng": 77.6476
    },
    {
        "property_id": 3,
        "owner_wallet": "owner_mock_3",
        "property_name": "MG Road Office Space, Bengaluru",
        "location_hash": "MG Road, Bengaluru",
        "valuation": 80000000,
        "total_shares": 20000,
        "share_price": 4000,
        "shares_sold": 12000,
        "status": 3,
        "ai_score": 95,
        "verification_status": "APPROVED",
        "min_investment": 50,
        "max_investment": 2000,
        "yield_pct": 9.1,
        "insurance_rate": 2.0,
        "description": "Grade A commercial office space on MG Road with steady rental income from multinational IT tenants. Includes 10 dedicated parking slots and central HVAC.",
        "images": '["https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=2669&auto=format&fit=crop", "https://images.unsplash.com/photo-1497366754035-f200968a6e72?q=80&w=2669&auto=format&fit=crop", "https://images.unsplash.com/photo-1497366811353-6870744d04b2?q=80&w=2669&auto=format&fit=crop"]',
        "lat": 12.9716,
        "lng": 77.5946
    }
]

def seed():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as count FROM properties")
    if c.fetchone()["count"] == 0:
        for p in mock_properties:
            c.execute('''
                INSERT INTO properties (
                    property_id, owner_wallet, property_name, location_hash, valuation, total_shares,
                    share_price, shares_sold, status, ai_score, verification_status, min_investment,
                    max_investment, yield_pct, insurance_rate, description, images, lat, lng
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
            ''', (
                p["property_id"], p["owner_wallet"], p["property_name"], p["location_hash"], p["valuation"],
                p["total_shares"], p["share_price"], p["shares_sold"], p["status"], p["ai_score"],
                p["verification_status"], p["min_investment"], p["max_investment"], p["yield_pct"],
                p["insurance_rate"], p["description"], p["images"], p.get("lat"), p.get("lng")
            ))
        print("Database seeded with mock properties.")
    else:
        print("Database already contains properties.")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed()
