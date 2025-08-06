from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import db
import utils

app = FastAPI(title="Bounty-X API", description="A decentralized bounty platform")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
print("🚀 Initializing Bounty-X API...")
db.init_database()
print("✅ Database initialized successfully")

# Pydantic models
class BountyCreate(BaseModel):
    funder_id: int
    bounty_name: str
    github_issue_url: str
    amount: float
    finish_after: int # Default 24 hours in seconds

class BountyAccept(BaseModel):
    developer_address: str
    finish_after: int = 86400  # Default 24 hours in seconds

class BountyClaim(BaseModel):
    merge_request_url: str

class Bounty(BaseModel):
    id: int
    funder_id: int
    bounty_name: str
    github_issue_url: str
    funder_address: str
    developer_address: Optional[str]
    amount: float
    escrow_id: Optional[str]
    escrow_sequence: Optional[int]
    escrow_condition: Optional[str]
    escrow_fulfillment: Optional[str]
    status: str  # "open", "accepted", "claimed", "cancelled"
    created_at: str
    updated_at: str

class User(BaseModel):
    id: int
    username: str
    password: str
    xrp_address: Optional[str] = None
    xrp_secret: Optional[str] = None
    xrp_seed: Optional[str] = None
    bounties_created: int = 0
    bounties_accepted: int = 0
    total_xrp_funded: float = 0.0
    total_xrp_earned: float = 0.0
    current_xrp_balance: float = 0.0
    last_updated: str

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UpdateBalance(BaseModel):
    new_balance: float

# User Management Endpoints
@app.post("/register")
def register(user: UserRegister):
    print(f"📝 User registration request received for username: {user.username}")
    print(f"   Password length: {len(user.password)} characters")
    
    try:
        print(f"🔧 Creating testnet wallet...")
        wallet = utils.create_testnet_account()
        print(f"💰 Testnet wallet created for user: {user.username}")
        print(f"   Address: {wallet.classic_address}")
        print(f"   Seed: {wallet.seed[:10]}...")
        
        print(f"💾 Storing user in database...")
        account_info = utils.get_account_info(wallet.classic_address)
        user_id = db.create_user(user.username, user.password, wallet.classic_address, wallet.private_key, wallet.seed, account_info['balance_xrp'])
        print(f"✅ User registered successfully - ID: {user_id}, Username: {user.username}")
        
        return {"message": "User registered successfully", "user_id": user_id}
    except Exception as e:
        print(f"❌ User registration failed for {user.username}: {str(e)}")
        print(f"   Error type: {type(e).__name__}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/login")
def login(user: UserLogin):
    print(f"🔐 Login attempt for username: {user.username}")
    try:
        user_data = db.get_user_by_credentials(user.username, user.password)
        if not user_data:
            print(f"❌ Login failed for username: {user.username} - Invalid credentials")
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        print(f"✅ Login successful for user: {user.username} (ID: {user_data['id']})")
        return {
            "message": "Login successful", 
            "user_id": user_data['id'],
            "username": user_data['username'],
            "xrp_address": user_data['xrp_address'],
            "bounties_created": user_data['bounties_created'],
            "bounties_accepted": user_data['bounties_accepted'],
            "total_xrp_funded": user_data['total_xrp_funded'],
            "total_xrp_earned": user_data['total_xrp_earned'],
            "current_xrp_balance": user_data['current_xrp_balance'],
            "last_updated": user_data['last_updated']
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Login error for {user.username}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

# Bounty Management Endpoints
@app.post("/bounties/", response_model=Bounty)
def create_bounty(bounty: BountyCreate):
    print(f"🎯 Creating new bounty: '{bounty.bounty_name}' by funder ID: {bounty.funder_id}")
    print(f"   Amount: {bounty.amount} XRP, GitHub Issue: {bounty.github_issue_url}")
    
    now = datetime.now(timezone.utc).isoformat()

    try:
        user = db.get_user_by_id(bounty.funder_id)
        if not user:
            print(f"❌ Bounty creation failed - User not found: {bounty.funder_id}")
            raise HTTPException(status_code=404, detail="User not found")

        # Check if user has sufficient balance
        if user['current_xrp_balance'] < bounty.amount:
            print(f"❌ Bounty creation failed - Insufficient balance for user {bounty.funder_id}")
            print(f"   Current balance: {user['current_xrp_balance']} XRP, Required: {bounty.amount} XRP")
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient balance. Current: {user['current_xrp_balance']} XRP, Required: {bounty.amount} XRP"
            )

        bounty_id = db.create_bounty(bounty.funder_id, bounty.bounty_name, bounty.github_issue_url, user['xrp_address'], bounty.amount)
        print(f"✅ Bounty created successfully - ID: {bounty_id}, Name: '{bounty.bounty_name}'")
        print(f"   User balance decreased by {bounty.amount} XRP")
        
        return Bounty(
            id=bounty_id,
            funder_id=bounty.funder_id,
            bounty_name=bounty.bounty_name,
            github_issue_url=bounty.github_issue_url,
            funder_address=user['xrp_address'],
            developer_address=None,
            amount=bounty.amount,
            escrow_id=None,
            escrow_sequence=None,
            escrow_condition=None,
            escrow_fulfillment=None,
            status="open",
            created_at=now,
            updated_at=now
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Bounty creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create bounty: {str(e)}")

@app.get("/bounties/", response_model=List[Bounty])
def list_bounties():
    print("📋 Listing all bounties")
    try:
        bounties = db.get_all_bounties()
        print(f"✅ Retrieved {len(bounties)} bounties")
        return bounties
    except Exception as e:
        print(f"❌ Error listing bounties: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list bounties: {str(e)}")

@app.get("/bounties/search/", response_model=List[Bounty])
def search_bounties(name: str = None, github_url: str = None):
    """Search bounties by name or GitHub URL"""
    print(f"🔍 Searching bounties - Name: {name}, GitHub URL: {github_url}")
    
    try:
        if name:
            bounties = db.search_bounties_by_name(name)
            print(f"✅ Found {len(bounties)} bounties matching name: '{name}'")
        elif github_url:
            bounties = db.search_bounties_by_github_url(github_url)
            print(f"✅ Found {len(bounties)} bounties matching GitHub URL: {github_url}")
        else:
            bounties = db.get_all_bounties()
            print(f"✅ Retrieved all {len(bounties)} bounties (no search criteria)")
        return bounties
    except Exception as e:
        print(f"❌ Error searching bounties: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/bounties/status/{status}", response_model=List[Bounty])
def get_bounties_by_status(status: str):
    """Get bounties by status (open, accepted, claimed)"""
    print(f"📊 Getting bounties by status: {status}")
    try:
        bounties = db.get_bounties_by_status(status)
        print(f"✅ Found {len(bounties)} bounties with status: {status}")
        return bounties
    except Exception as e:
        print(f"❌ Error getting bounties by status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get bounties by status: {str(e)}")

@app.get("/bounties/funder/{funder_id}", response_model=List[Bounty])
def get_bounties_by_funder(funder_id: int):
    """Get bounties by funder ID"""
    print(f"👤 Getting bounties for funder ID: {funder_id}")
    try:
        bounties = db.get_bounties_by_funder(funder_id)
        print(f"✅ Found {len(bounties)} bounties for funder ID: {funder_id}")
        return bounties
    except Exception as e:
        print(f"❌ Error getting bounties by funder: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get bounties by funder: {str(e)}")

@app.get("/bounties/developer/{developer_address}", response_model=List[Bounty])
def get_bounties_by_developer(developer_address: str):
    """Get bounties by developer address"""
    print(f"👨‍💻 Getting bounties for developer address: {developer_address}")
    try:
        bounties = db.get_bounties_by_developer(developer_address)
        print(f"✅ Found {len(bounties)} bounties for developer: {developer_address}")
        return bounties
    except Exception as e:
        print(f"❌ Error getting bounties by developer: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get bounties by developer: {str(e)}")

@app.get("/bounties/statistics")
def get_bounty_statistics():
    """Get overall bounty statistics"""
    print("📈 Getting bounty statistics")
    try:
        stats = db.get_bounty_statistics()
        print(f"✅ Retrieved bounty statistics: {stats}")
        return stats
    except Exception as e:
        print(f"❌ Error getting bounty statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@app.get("/platform/statistics")
def get_platform_statistics():
    """Get comprehensive platform statistics"""
    print("📊 Getting platform statistics")
    try:
        stats = db.get_platform_statistics()
        print(f"✅ Retrieved platform statistics: {stats}")
        return stats
    except Exception as e:
        print(f"❌ Error getting platform statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get platform statistics: {str(e)}")

@app.post("/platform/statistics/recalculate")
def recalculate_statistics():
    """Recalculate and update all user statistics"""
    print("🔄 Recalculating user statistics")
    try:
        result = db.recalculate_user_statistics()
        print(f"✅ Statistics recalculated: {result}")
        return {
            "message": "Statistics recalculated successfully",
            "result": result
        }
    except Exception as e:
        print(f"❌ Error recalculating statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to recalculate statistics: {str(e)}")

@app.get("/users/{user_id}/statistics")
def get_user_statistics(user_id: int):
    """Get user-specific statistics"""
    print(f"📊 Getting statistics for user ID: {user_id}")
    try:
        stats = db.get_user_statistics(user_id)
        print(f"✅ Retrieved user statistics for ID {user_id}: {stats}")
        return stats
    except Exception as e:
        print(f"❌ Error getting user statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get user statistics: {str(e)}")

@app.post("/bounties/{bounty_id}/accept")
def accept_bounty(bounty_id: int, accept: BountyAccept):
    print(f"🤝 Bounty acceptance request for bounty ID: {bounty_id}")
    print(f"   Developer address: {accept.developer_address}")
    print(f"   Finish after: {accept.finish_after} seconds")
    
    try:
        bounty = db.get_bounty_by_id(bounty_id)
        if not bounty:
            print(f"❌ Bounty acceptance failed - Bounty not found: {bounty_id}")
            raise HTTPException(status_code=404, detail="Bounty not found")
        
        if bounty['status'] != "open":
            print(f"❌ Bounty acceptance failed - Bounty {bounty_id} is not open (status: {bounty['status']})")
            raise HTTPException(status_code=400, detail="Bounty is not open")
        
        user = db.get_user_by_id(bounty['funder_id'])
        if not user:
            print(f"❌ Bounty acceptance failed - User not found: {bounty['funder_id']}")
            raise HTTPException(status_code=404, detail="User not found")
        
        print(f"🔐 Creating conditional escrow for bounty {bounty_id}...")
        # Create conditional escrow
        escrow_response = utils.create_escrow(user['xrp_seed'], accept.developer_address, bounty['amount'], accept.finish_after)
        print(f"✅ Conditional escrow created - Hash: {escrow_response.result['hash']}")
        
        # Store escrow details (time-based escrow, no condition/fulfillment)
        db.accept_bounty(
            bounty_id, 
            accept.developer_address, 
            escrow_response.result['hash'], 
            escrow_response.result['tx_json']['Sequence']
        )
        print(f"✅ Bounty {bounty_id} accepted successfully by {accept.developer_address}")
        
        return {
            "message": "Bounty accepted successfully", 
            "bounty_id": bounty_id,
            "funder_id": bounty['funder_id']
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Bounty acceptance error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to accept bounty: {str(e)}")

@app.post("/bounties/{bounty_id}/claim")
def claim_bounty(bounty_id: int, claim: BountyClaim):
    print(f"🏆 Bounty claim request for bounty ID: {bounty_id}")
    print(f"   Merge request URL: {claim.merge_request_url}")
    
    try:
        # Get bounty
        bounty = db.get_bounty_by_id(bounty_id)
        if not bounty:
            print(f"❌ Bounty claim failed - Bounty not found: {bounty_id}")
            raise HTTPException(status_code=404, detail="Bounty not found")
        
        # Check if bounty is available for claiming (must be accepted)
        if bounty['status'] != "accepted":
            print(f"❌ Bounty claim failed - Bounty {bounty_id} is not accepted (status: {bounty['status']})")
            raise HTTPException(status_code=400, detail="Bounty is not available for claiming")
        
        # Check if escrow exists
        if not bounty['escrow_id']:
            print(f"❌ Bounty claim failed - No escrow found for bounty {bounty_id}")
            raise HTTPException(status_code=400, detail="No escrow found for this bounty")
        
        # For time-based escrows, we don't need condition/fulfillment
        # The escrow will be automatically finishable after the finish_after time
        
        # Extract issue number from bounty
        issue_number = utils.extract_issue_number_from_url(bounty['github_issue_url'])
        if not issue_number:
            print(f"❌ Bounty claim failed - Invalid GitHub issue URL: {bounty['github_issue_url']}")
            raise HTTPException(status_code=400, detail="Invalid GitHub issue URL")
        
        print(f"🔍 Verifying merge request contains issue #{issue_number}...")
        # Verify merge request contains issue reference
        if not utils.verify_merge_request_contains_issue(claim.merge_request_url, issue_number):
            print(f"❌ Bounty claim failed - Merge request doesn't reference issue #{issue_number}")
            raise HTTPException(
                status_code=400, 
                detail="Merge request does not contain a reference to the issue number"
            )
        print(f"✅ Merge request verification passed")
        
        # Retrieve escrow transaction details
        print(f"🔍 Retrieving escrow transaction details...")
        escrow_details = utils.get_escrow_transaction(bounty['escrow_id'])
        if not escrow_details:
            print(f"❌ Bounty claim failed - Could not retrieve escrow details for {bounty['escrow_id']}")
            raise HTTPException(status_code=400, detail="Could not retrieve escrow transaction details")
        print(f"✅ Escrow transaction details retrieved")

        funder = db.get_user_by_id(bounty['funder_id'])
        if not funder:
            print(f"❌ Bounty claim failed - Funder not found: {bounty['funder_id']}")
            raise HTTPException(status_code=404, detail="Funder not found")
        
        # Finish the time-based escrow on XRPL
        print(f"💰 Finishing time-based escrow...")
        try:
            # Finish the time-based escrow (no condition/fulfillment needed)
            tx_response = utils.finish_time_based_escrow(
                bounty['escrow_id'],
                bounty['escrow_sequence'],
                funder['xrp_seed'],
                bounty['funder_address']
            )
            print(f"✅ Time-based escrow fulfilled successfully")
            
            # Update bounty status to claimed
            db.claim_bounty(bounty_id)
            print(f"✅ Bounty {bounty_id} claimed successfully")
            
            return {
                "message": "Bounty claimed successfully and time-based escrow fulfilled",
                "bounty_id": bounty_id,
                "funder_id": bounty['funder_id'],
                "developer_address": bounty['developer_address'],
                "merge_request_url": claim.merge_request_url,
                "status": "claimed",
                "escrow_id": bounty['escrow_id'],
                "escrow_details": escrow_details,
                "tx_response": tx_response.result
            }
            
        except Exception as e:
            print(f"❌ Failed to fulfill time-based escrow: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to fulfill time-based escrow: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Bounty claim error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to claim bounty: {str(e)}")

@app.get("/bounties/{bounty_id}", response_model=Bounty)
def get_bounty(bounty_id: int):
    print(f"📄 Getting bounty details for ID: {bounty_id}")
    try:
        bounty = db.get_bounty_by_id(bounty_id)
        if not bounty:
            print(f"❌ Bounty not found: {bounty_id}")
            raise HTTPException(status_code=404, detail="Bounty not found")
        
        print(f"✅ Retrieved bounty details for ID: {bounty_id}")
        return Bounty(
            id=bounty['id'],
            funder_id=bounty['funder_id'],
            bounty_name=bounty['bounty_name'],
            github_issue_url=bounty['github_issue_url'],
            funder_address=bounty['funder_address'],
            developer_address=bounty['developer_address'],
            amount=bounty['amount'],
            escrow_id=bounty['escrow_id'],
            escrow_sequence=bounty['escrow_sequence'],
            escrow_condition=bounty['escrow_condition'],
            escrow_fulfillment=bounty['escrow_fulfillment'],
            status=bounty['status'],
            created_at=bounty['created_at'],
            updated_at=bounty['updated_at']
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting bounty details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get bounty: {str(e)}")

@app.post("/bounties/{bounty_id}/cancel")
def cancel_bounty(bounty_id: int):
    """Cancel a bounty and refund the funder"""
    print(f"❌ Bounty cancellation request for bounty ID: {bounty_id}")
    
    try:
        success = db.cancel_bounty(bounty_id)
        if not success:
            print(f"❌ Bounty cancellation failed - Bounty not found: {bounty_id}")
            raise HTTPException(status_code=404, detail="Bounty not found")
        
        print(f"✅ Bounty {bounty_id} cancelled successfully and funder refunded")
        return {
            "message": "Bounty cancelled successfully and funder refunded",
            "bounty_id": bounty_id
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Bounty cancellation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel bounty: {str(e)}")

@app.get("/users/{user_id}")
def get_user(user_id: int):
    """Get user details by ID (for debugging)"""
    print(f"👤 Getting user details for ID: {user_id}")
    try:
        user = db.get_user_by_id(user_id)
        if not user:
            print(f"❌ User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        print(f"✅ Retrieved user details for ID: {user_id}")
        return {
            "id": user['id'],
            "username": user['username'],
            "xrp_address": user['xrp_address'],
            "bounties_created": user['bounties_created'],
            "bounties_accepted": user['bounties_accepted'],
            "total_xrp_funded": user['total_xrp_funded'],
            "total_xrp_earned": user['total_xrp_earned'],
            "current_xrp_balance": user['current_xrp_balance'],
            "last_updated": user['last_updated']
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error getting user details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")

@app.get("/users")
def list_users():
    """List all users (for debugging)"""
    print("👥 Listing all users")
    try:
        users = db.get_all_users()
        print(f"✅ Retrieved {len(users)} users")
        return users
    except Exception as e:
        print(f"❌ Error listing users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list users: {str(e)}")

@app.put("/users/{user_id}/balance")
def update_user_balance(user_id: int, balance_update: UpdateBalance):
    """Update user's XRP balance"""
    print(f"💰 Updating balance for user ID: {user_id} to {balance_update.new_balance} XRP")
    try:
        success = db.update_user_xrp_balance(user_id, balance_update.new_balance)
        if not success:
            print(f"❌ Failed to update balance - User not found: {user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        
        print(f"✅ Balance updated successfully for user ID: {user_id}")
        return {"message": "Balance updated successfully", "user_id": user_id, "new_balance": balance_update.new_balance}
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error updating user balance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update balance: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Bounty-X API server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)