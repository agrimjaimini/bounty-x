"""FastAPI application for the Bounty-X platform.

Exposes endpoints to register/login users, manage bounties,
handle escrow lifecycle, and provide statistics.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import db
import utils

app = FastAPI(title="Bounty-X API", description="A decentralized bounty platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://agrimjaimini.github.io/bounty-x/",
        "https://18-222-139-25.sslip.io",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db.init_database()

class BountyCreate(BaseModel):
    """Payload to create a new bounty funded by a user."""
    funder_id: int
    bounty_name: str
    description: Optional[str] = None
    github_issue_url: str
    amount: float
    finish_after: int

class BountyAccept(BaseModel):
    """Payload for a developer to accept a bounty and set finish window."""
    developer_address: str
    finish_after: int = 86400

class BountyClaim(BaseModel):
    """Payload to claim a bounty after a PR is merged and verified."""
    merge_request_url: str
    developer_secret_key: str

class Bounty(BaseModel):
    """Response model describing a bounty and its escrow status."""
    id: int
    funder_id: int
    bounty_name: str
    description: Optional[str]
    github_issue_url: str
    funder_address: str
    developer_address: Optional[str]
    amount: float
    escrow_id: Optional[str]
    escrow_sequence: Optional[int]
    escrow_condition: Optional[str]
    escrow_fulfillment: Optional[str]
    status: str
    created_at: str
    updated_at: str

class User(BaseModel):
    """User profile and aggregate statistics."""
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
    """Registration payload with username and password."""
    username: str
    password: str

class UserLogin(BaseModel):
    """Login payload with username and password."""
    username: str
    password: str

class UpdateBalance(BaseModel):
    """Request body to set a user's current XRPL balance."""
    new_balance: float

@app.post("/register")
def register(user: UserRegister):
    """Register a new user and create a funded XRPL testnet wallet."""
    try:
        wallet = utils.create_testnet_account()
        account_info = utils.get_account_info(wallet.classic_address)
        user_id = db.create_user(user.username, user.password, wallet.classic_address, wallet.private_key, wallet.seed, account_info['balance_xrp'])
        
        return {"message": "User registered successfully", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/login")
def login(user: UserLogin):
    """Authenticate a user and return profile metadata."""
    try:
        user_data = db.get_user_by_credentials(user.username, user.password)
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
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
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.post("/bounties/", response_model=Bounty)
def create_bounty(bounty: BountyCreate):
    """Create a new bounty if the funder has sufficient balance."""
    now = datetime.now(timezone.utc).isoformat()

    try:
        user = db.get_user_by_id(bounty.funder_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user['current_xrp_balance'] < bounty.amount:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient balance. Current: {user['current_xrp_balance']} XRP, Required: {bounty.amount} XRP"
            )

        bounty_id = db.create_bounty(
            bounty.funder_id,
            bounty.bounty_name,
            bounty.description or "",
            bounty.github_issue_url,
            user['xrp_address'],
            bounty.amount
        )
        
        return Bounty(
            id=bounty_id,
            funder_id=bounty.funder_id,
            bounty_name=bounty.bounty_name,
            description=bounty.description or None,
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
        raise HTTPException(status_code=500, detail=f"Failed to create bounty: {str(e)}")

@app.get("/bounties/", response_model=List[Bounty])
def list_bounties():
    """Return all bounties ordered by creation time."""
    try:
        bounties = db.get_all_bounties()
        return bounties
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list bounties: {str(e)}")

@app.get("/bounties/search/", response_model=List[Bounty])
def search_bounties(name: str = None, github_url: str = None):
    """Search bounties by name or GitHub issue URL."""
    try:
        if name:
            bounties = db.search_bounties_by_name(name)
        elif github_url:
            bounties = db.search_bounties_by_github_url(github_url)
        else:
            bounties = db.get_all_bounties()
        return bounties
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/bounties/status/{status}", response_model=List[Bounty])
def get_bounties_by_status(status: str):
    """List bounties filtered by status (open, accepted, claimed, cancelled)."""
    try:
        bounties = db.get_bounties_by_status(status)
        return bounties
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get bounties by status: {str(e)}")

@app.get("/bounties/funder/{funder_id}", response_model=List[Bounty])
def get_bounties_by_funder(funder_id: int):
    """List bounties created by a specific funder."""
    try:
        bounties = db.get_bounties_by_funder(funder_id)
        return bounties
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get bounties by funder: {str(e)}")

@app.get("/bounties/developer/{developer_address}", response_model=List[Bounty])
def get_bounties_by_developer(developer_address: str):
    """List bounties associated to a developer XRPL address."""
    try:
        bounties = db.get_bounties_by_developer(developer_address)
        return bounties
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get bounties by developer: {str(e)}")

@app.get("/bounties/statistics")
def get_bounty_statistics():
    """Aggregate counts and totals across all bounties."""
    try:
        stats = db.get_bounty_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@app.get("/platform/statistics")
def get_platform_statistics():
    """Platform-wide statistics (users, bounties, and amounts)."""
    try:
        stats = db.get_platform_statistics()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get platform statistics: {str(e)}")

@app.post("/platform/statistics/recalculate")
def recalculate_statistics():
    """Recompute user aggregates from the bounties table."""
    try:
        result = db.recalculate_user_statistics()
        return {
            "message": "Statistics recalculated successfully",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to recalculate statistics: {str(e)}")

@app.get("/users/{user_id}/statistics")
def get_user_statistics(user_id: int):
    """Return aggregate statistics for a single user."""
    try:
        stats = db.get_user_statistics(user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user statistics: {str(e)}")

@app.post("/bounties/{bounty_id}/accept")
def accept_bounty(bounty_id: int, accept: BountyAccept):
    """Create an escrow and mark a bounty as accepted by a developer."""
    try:
        bounty = db.get_bounty_by_id(bounty_id)
        if not bounty:
            raise HTTPException(status_code=404, detail="Bounty not found")
        
        if bounty['status'] != "open":
            raise HTTPException(status_code=400, detail="Bounty is not open")
        
        user = db.get_user_by_id(bounty['funder_id'])
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user['current_xrp_balance'] < bounty['amount']:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient balance. Current: {user['current_xrp_balance']} XRP, Required: {bounty['amount']} XRP"
            )
        
        if not user['xrp_seed']:
            raise HTTPException(
                status_code=400, 
                detail="User has no XRP seed configured. Please contact support."
            )
        
        developer_secret_key = utils.generate_developer_secret_key()
        
        if not utils.validate_account_for_escrow(user['xrp_seed'], bounty['amount']):
            raise HTTPException(
                status_code=400, 
                detail="Account validation failed. Please ensure your wallet is properly funded with sufficient XRP."
            )
        
        try:
            escrow_response = utils.create_escrow(user['xrp_seed'], accept.developer_address, bounty['amount'], accept.finish_after)
        except Exception as escrow_error:
            error_msg = str(escrow_error)
            if "Insufficient funds" in error_msg:
                raise HTTPException(status_code=400, detail="Insufficient XRP balance to create escrow")
            elif "No permission" in error_msg:
                raise HTTPException(status_code=400, detail="Account permission error. Please ensure your wallet is properly funded.")
            elif "unfunded" in error_msg.lower():
                raise HTTPException(status_code=400, detail="Account is unfunded. Please fund your wallet first.")
            else:
                raise HTTPException(status_code=500, detail=f"Escrow creation failed: {error_msg}")
        
        db.accept_bounty(
            bounty_id, 
            accept.developer_address, 
            escrow_response.result['hash'], 
            escrow_response.result['tx_json']['Sequence'],
            developer_secret_key
        )
        
        return {
            "message": "Bounty accepted successfully", 
            "bounty_id": bounty_id,
            "funder_id": bounty['funder_id'],
            "developer_secret_key": developer_secret_key
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to accept bounty: {str(e)}")

@app.post("/bounties/{bounty_id}/claim")
def claim_bounty(bounty_id: int, claim: BountyClaim):
    """Verify PR and developer key, then finish escrow and mark claimed."""
    try:
        bounty = db.get_bounty_by_id(bounty_id)
        if not bounty:
            raise HTTPException(status_code=404, detail="Bounty not found")
        
        if bounty['status'] != "accepted":
            raise HTTPException(status_code=400, detail="Bounty is not available for claiming")
        
        if not bounty['escrow_id']:
            raise HTTPException(status_code=400, detail="No escrow found for this bounty")
        
        issue_number = utils.extract_issue_number_from_url(bounty['github_issue_url'])
        if not issue_number:
            raise HTTPException(status_code=400, detail="Invalid GitHub issue URL")
        
        if not db.verify_developer_secret_key(bounty_id, claim.developer_secret_key):
            raise HTTPException(
                status_code=400, 
                detail="Invalid developer secret key. Only the developer who accepted this bounty can claim it."
            )
        
        if not utils.verify_merge_request_contains_issue(claim.merge_request_url, issue_number, claim.developer_secret_key):
            raise HTTPException(
                status_code=400, 
                detail="Merge request must contain both the issue number reference and the developer secret key"
            )
        
        escrow_details = utils.get_escrow_transaction(bounty['escrow_id'])
        if not escrow_details:
            raise HTTPException(status_code=400, detail="Could not retrieve escrow transaction details")

        funder = db.get_user_by_id(bounty['funder_id'])
        if not funder:
            raise HTTPException(status_code=404, detail="Funder not found")
        
        try:
            tx_response = utils.finish_time_based_escrow(
                bounty['escrow_sequence'],
                funder['xrp_seed'],
                bounty['funder_address']
            )
            
            db.claim_bounty(bounty_id)
            
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
            raise HTTPException(status_code=500, detail=f"Failed to fulfill time-based escrow: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to claim bounty: {str(e)}")

@app.get("/bounties/{bounty_id}", response_model=Bounty)
def get_bounty(bounty_id: int):
    """Fetch a single bounty by id."""
    try:
        bounty = db.get_bounty_by_id(bounty_id)
        if not bounty:
            raise HTTPException(status_code=404, detail="Bounty not found")
        
        return Bounty(
            id=bounty['id'],
            funder_id=bounty['funder_id'],
            bounty_name=bounty['bounty_name'],
            description=bounty['description'],
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
        raise HTTPException(status_code=500, detail=f"Failed to get bounty: {str(e)}")

@app.post("/bounties/{bounty_id}/cancel")
def cancel_bounty(bounty_id: int):
    """Cancel an open bounty, adjust counters, then delete the record."""
    try:
        success = db.cancel_bounty(bounty_id)
        if not success:
            raise HTTPException(status_code=404, detail="Bounty not found")

        # Remove the cancelled bounty from the table to keep lists clean
        db.delete_bounty(bounty_id)

        return {
            "message": "Bounty cancelled and deleted successfully",
            "bounty_id": bounty_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel bounty: {str(e)}")

@app.get("/users/{user_id}")
def get_user(user_id: int):
    """Get a user's public profile by id."""
    try:
        user = db.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
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
        raise HTTPException(status_code=500, detail=f"Failed to get user: {str(e)}")

@app.get("/users")
def list_users():
    """List basic profiles for all users."""
    try:
        users = db.get_all_users()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list users: {str(e)}")

@app.put("/users/{user_id}/balance")
def update_user_balance(user_id: int, balance_update: UpdateBalance):
    """Set a user's current_xrp_balance value."""
    try:
        success = db.update_user_xrp_balance(user_id, balance_update.new_balance)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": "Balance updated successfully", "user_id": user_id, "new_balance": balance_update.new_balance}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update balance: {str(e)}")

@app.post("/users/{user_id}/fund")
def fund_user_wallet(user_id: int):
    """Fund an existing XRPL testnet wallet via the faucet and update balance."""
    try:
        if not isinstance(user_id, int) or user_id <= 0:
            raise HTTPException(status_code=400, detail="Invalid user ID")
        
        user = db.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if not user['xrp_seed']:
            raise HTTPException(
                status_code=400, 
                detail="User has no XRP seed configured. Please contact support."
            )
        
        if not user['xrp_seed'].startswith('s'):
            raise HTTPException(
                status_code=400, 
                detail="Invalid XRP seed format"
            )
        
        try:
            funding_result = utils.fund_existing_wallet(user['xrp_seed'])
        except Exception as faucet_error:
            raise HTTPException(
                status_code=503, 
                detail="Testnet faucet is currently unavailable. Please try again later."
            )
        
        if not funding_result or 'balance_xrp' not in funding_result:
            raise HTTPException(
                status_code=500, 
                detail="Invalid response from testnet faucet"
            )
        
        try:
            success = db.update_user_xrp_balance(user_id, funding_result['balance_xrp'])
            if not success:
                raise HTTPException(
                    status_code=500, 
                    detail="Failed to update user balance in database"
                )
        except Exception as db_error:
            raise HTTPException(
                status_code=500, 
                detail="Failed to update user balance. Please try again."
            )
        
        return {
            "message": "Wallet funded successfully",
            "user_id": user_id,
            "address": funding_result['address'],
            "balance_drops": funding_result['balance_drops'],
            "balance_xrp": funding_result['balance_xrp']
        }
        
    except HTTPException:
        raise
    except ValueError as ve:
        raise HTTPException(status_code=400, detail="Invalid input data")
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail="An unexpected error occurred. Please try again later."
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)