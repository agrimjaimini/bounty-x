from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import sqlite3
import re
import requests
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import EscrowCreate, EscrowFinish
from xrpl.transaction import reliable_submission
from xrpl.models.requests import AccountInfo
from xrpl.utils import xrp_to_drops



app = FastAPI()

DB_PATH = "bounties.db"

# Database setup
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS bounties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    github_issue_url TEXT NOT NULL,
    funder_address TEXT NOT NULL,
    developer_address TEXT,
    amount REAL NOT NULL,
    escrow_id TEXT,
    escrow_sequence INTEGER,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
)
''')
conn.commit()

class BountyCreate(BaseModel):
    github_issue_url: str
    funder_address: str
    funder_secret: str  # For demo only; in production, use secure key management
    amount: float
    finish_after: int = 86400  # Default 24 hours in seconds

class BountyAccept(BaseModel):
    developer_address: str
    funder_secret: str  # For demo only; in production, use secure key management
    finish_after: int = 86400  # Default 24 hours in seconds

class BountyClaim(BaseModel):
    merge_request_url: str
    developer_secret: str  # For demo only; in production, use secure key management

class Bounty(BaseModel):
    id: int
    github_issue_url: str
    funder_address: str
    developer_address: Optional[str]
    amount: float
    escrow_id: Optional[str]
    escrow_sequence: Optional[int]
    status: str
    created_at: str
    updated_at: str

@app.post("/bounties/", response_model=Bounty)
def create_bounty(bounty: BountyCreate):
    now = datetime.utcnow().isoformat()
    
    # Insert bounty first
    c.execute('''
        INSERT INTO bounties (github_issue_url, funder_address, amount, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (bounty.github_issue_url, bounty.funder_address, bounty.amount, "open", now, now))
    conn.commit()
    bounty_id = c.lastrowid
    
    # Return the created bounty
    c.execute('SELECT * FROM bounties WHERE id = ?', (bounty_id,))
    row = c.fetchone()
    return Bounty(
        id=row[0], github_issue_url=row[1], funder_address=row[2], developer_address=row[3],
        amount=row[4], escrow_id=row[5], escrow_sequence=row[6], status=row[7], created_at=row[8], updated_at=row[9]
    )

@app.get("/bounties/", response_model=List[Bounty])
def list_bounties():
    c.execute('SELECT * FROM bounties')
    rows = c.fetchall()
    return [Bounty(
        id=row[0], github_issue_url=row[1], funder_address=row[2], developer_address=row[3],
        amount=row[4], escrow_id=row[5], escrow_sequence=row[6], status=row[7], created_at=row[8], updated_at=row[9]
    ) for row in rows]



@app.post("/bounties/{bounty_id}/accept")
def accept_bounty(bounty_id: int, accept: BountyAccept):
    # Get bounty
    c.execute('SELECT * FROM bounties WHERE id = ?', (bounty_id,))
    row = c.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Bounty not found")
    
    bounty = {
        'id': row[0], 'github_issue_url': row[1], 'funder_address': row[2], 
        'developer_address': row[3], 'amount': row[4], 'escrow_id': row[5], 
        'escrow_sequence': row[6], 'status': row[7], 'created_at': row[8], 'updated_at': row[9]
    }
    
    # Check if bounty is available for accepting
    if bounty['status'] != "open":
        raise HTTPException(status_code=400, detail="Bounty is not available for accepting")
    
    if bounty['developer_address']:
        raise HTTPException(status_code=400, detail="Bounty has already been accepted")
    
    # Create escrow on XRPL
    try:
        # XRPL testnet
        client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
        wallet = Wallet(seed=accept.funder_secret, sequence=0)
        
        escrow_tx = EscrowCreate(
            account=bounty['funder_address'],
            amount=str(xrp_to_drops(bounty['amount'])),
            destination=accept.developer_address,
            finish_after=int(datetime.utcnow().timestamp()) + accept.finish_after,
        )
        
        tx_response = reliable_submission(escrow_tx, client, wallet)
        escrow_id = tx_response.result.get("hash")
        escrow_sequence = tx_response.result.get("Sequence")
        
        # Update bounty with escrow ID, sequence, and status
        now = datetime.utcnow().isoformat()
        c.execute('''
            UPDATE bounties 
            SET developer_address = ?, escrow_id = ?, escrow_sequence = ?, status = ?, updated_at = ? 
            WHERE id = ?
        ''', (accept.developer_address, escrow_id, escrow_sequence, "funded", now, bounty_id))
        conn.commit()
        
        return {
            "message": "Bounty accepted and escrow created successfully",
            "bounty_id": bounty_id,
            "developer_address": accept.developer_address,
            "status": "funded",
            "escrow_id": escrow_id,
            "tx_response": tx_response.result
        }
        
    except Exception as e:
        # If escrow creation fails, revert the bounty status
        now = datetime.utcnow().isoformat()
        c.execute('''
            UPDATE bounties 
            SET developer_address = NULL, status = ?, updated_at = ? 
            WHERE id = ?
        ''', ("open", now, bounty_id))
        conn.commit()
        raise HTTPException(status_code=500, detail=f"Failed to create escrow: {str(e)}")

 
    


    
    

def extract_issue_number_from_url(github_issue_url: str) -> Optional[str]:
    """Extract issue number from GitHub issue URL"""
    pattern = r'github\.com/[^/]+/[^/]+/issues/(\d+)'
    match = re.search(pattern, github_issue_url)
    return match.group(1) if match else None

def verify_merge_request_contains_issue(merge_request_url: str, issue_number: str) -> bool:
    """Verify that the merge request contains a reference to the issue number"""
    try:
        # Convert GitHub PR URL to API URL
        api_url = merge_request_url.replace('github.com', 'api.github.com/repos')
        api_url = api_url.replace('/pull/', '/pulls/')
        
        # Get PR details from GitHub API
        response = requests.get(api_url)
        if response.status_code != 200:
            return False
        
        pr_data = response.json()
        
        # Check title and body for issue reference
        title = pr_data.get('title', '')
        body = pr_data.get('body', '')
        
        # Look for issue references like #123, closes #123, fixes #123, etc.
        issue_patterns = [
            rf'#{issue_number}\b',
            rf'closes #{issue_number}\b',
            rf'fixes #{issue_number}\b',
            rf'resolves #{issue_number}\b',
            rf'close #{issue_number}\b',
            rf'fix #{issue_number}\b',
            rf'resolve #{issue_number}\b'
        ]
        
        for pattern in issue_patterns:
            if re.search(pattern, title, re.IGNORECASE) or re.search(pattern, body, re.IGNORECASE):
                return True
        
        return False
        
    except Exception as e:
        print(f"Error verifying merge request: {e}")
        return False

@app.post("/bounties/{bounty_id}/claim")
def claim_bounty(bounty_id: int, claim: BountyClaim):
    # Get bounty
    c.execute('SELECT * FROM bounties WHERE id = ?', (bounty_id,))
    row = c.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Bounty not found")
    
    bounty = {
        'id': row[0], 'github_issue_url': row[1], 'funder_address': row[2], 
        'developer_address': row[3], 'amount': row[4], 'escrow_id': row[5], 
        'escrow_sequence': row[6], 'status': row[7], 'created_at': row[8], 'updated_at': row[9]
    }
    
    # Check if bounty is available for claiming (must be funded)
    if bounty['status'] != "funded":
        raise HTTPException(status_code=400, detail="Bounty is not available for claiming")
    
    # Check if the developer address matches the accepted developer
    if bounty['developer_address'] != claim.developer_address:
        raise HTTPException(status_code=400, detail="Only the accepted developer can claim this bounty")
    
    # Check if escrow exists
    if not bounty['escrow_id']:
        raise HTTPException(status_code=400, detail="No escrow found for this bounty")
    
    # Extract issue number from bounty
    issue_number = extract_issue_number_from_url(bounty['github_issue_url'])
    if not issue_number:
        raise HTTPException(status_code=400, detail="Invalid GitHub issue URL")
    
    # Verify merge request contains issue reference
    if not verify_merge_request_contains_issue(claim.merge_request_url, issue_number):
        raise HTTPException(
            status_code=400, 
            detail="Merge request does not contain a reference to the issue number"
        )
    
    # Fulfill the escrow on XRPL
    try:
        # XRPL testnet
        client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
        developer_wallet = Wallet(seed=claim.developer_secret, sequence=0)
        
        # Create escrow finish transaction
        escrow_finish_tx = EscrowFinish(
            account=claim.developer_address,
            owner=bounty['funder_address'],
            offer_sequence=bounty['escrow_sequence'],
        )
        
        # Submit the transaction
        tx_response = reliable_submission(escrow_finish_tx, client, developer_wallet)
        
        # Update bounty status to claimed
        now = datetime.utcnow().isoformat()
        c.execute('''
            UPDATE bounties 
            SET status = ?, updated_at = ? 
            WHERE id = ?
        ''', ("claimed", now, bounty_id))
        conn.commit()
        
        return {
            "message": "Bounty claimed successfully and escrow fulfilled",
            "bounty_id": bounty_id,
            "developer_address": claim.developer_address,
            "merge_request_url": claim.merge_request_url,
            "status": "claimed",
            "escrow_id": bounty['escrow_id'],
            "tx_response": tx_response.result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fulfill escrow: {str(e)}")

@app.get("/bounties/{bounty_id}", response_model=Bounty)
def get_bounty(bounty_id: int):
    c.execute('SELECT * FROM bounties WHERE id = ?', (bounty_id,))
    row = c.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Bounty not found")
    
    return Bounty(
        id=row[0], github_issue_url=row[1], funder_address=row[2], developer_address=row[3],
        amount=row[4], escrow_id=row[5], escrow_sequence=row[6], status=row[7], created_at=row[8], updated_at=row[9]
    ) 