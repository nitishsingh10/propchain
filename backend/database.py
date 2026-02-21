import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "propchain.db")

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    # Properties Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS properties (
            property_id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_wallet TEXT,
            property_name TEXT,
            location_hash TEXT,
            valuation INTEGER,
            total_shares INTEGER,
            share_price INTEGER,
            shares_sold INTEGER DEFAULT 0,
            status INTEGER DEFAULT 0,
            verified_at INTEGER DEFAULT 0,
            listed_at INTEGER DEFAULT 0,
            description TEXT,
            lat REAL,
            lng REAL,
            ai_score INTEGER DEFAULT 0,
            verification_status TEXT DEFAULT 'PENDING',
            min_investment INTEGER DEFAULT 1,
            max_investment INTEGER DEFAULT 1000,
            insurance_rate REAL DEFAULT 1.5,
            yield_pct REAL DEFAULT 0.0,
            images TEXT
        )
    ''')
    
    # Holdings Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS holdings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER,
            investor_address TEXT,
            shares INTEGER DEFAULT 0,
            claimable_rent INTEGER DEFAULT 0,
            total_claimed INTEGER DEFAULT 0
        )
    ''')
    
    # Proposals Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS proposals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER,
            proposer_address TEXT,
            proposal_type INTEGER,
            description TEXT,
            proposed_value INTEGER,
            yes_weight INTEGER DEFAULT 0,
            no_weight INTEGER DEFAULT 0,
            total_shares INTEGER DEFAULT 0,
            status INTEGER DEFAULT 0,
            voting_deadline INTEGER
        )
    ''')
    
    # Votes Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proposal_id INTEGER,
            voter_address TEXT,
            vote_yes BOOLEAN
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize on import
init_db()
