 

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, timezone
import db
from utils import xrpl_utils
from utils import github_utils
from xrpl.utils import datetime_to_ripple_time

app = FastAPI(title="Bounty-X API", description="A decentralized bounty platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://agrimjaimini.github.io",
        "http://localhost:3000",
    ],
    allow_origin_regex=r"^https://agrimjaimini\.github\.io$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db.init_database()

class BountyCreate(BaseModel):
    funder_id: int
    bounty_name: str
    description: Optional[str] = None
    github_issue_url: str
    amount: float
    time_limit_seconds: int

class BountyAccept(BaseModel):
    developer_address: str

class BountyClaim(BaseModel):
    merge_request_url: str

class BountyBoost(BaseModel):
    contributor_id: int
    amount: float

class BountyContribution(BaseModel):
    id: int
    bounty_id: int
    contributor_id: int
    contributor_address: str
    amount: float
    escrow_id: Optional[str] = None
    escrow_sequence: Optional[int] = None
    created_at: str
    updated_at: str

class Bounty(BaseModel):
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
    developer_secret_key: Optional[str] = None
    status: str
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

@app.post("/register")
def register(user: UserRegister):
    try:
        wallet = xrpl_utils.create_testnet_account()
        account_info = xrpl_utils.get_account_info(wallet.classic_address)
        user_id = db.create_user(user.username, user.password, wallet.classic_address, wallet.private_key, wallet.seed, account_info['balance_xrp'])
        
        return {"message": "User registered successfully", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/login")
def login(user: UserLogin):
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
            bounty.amount,
            int(bounty.time_limit_seconds)
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

@app.get("/bounties/contributor/{user_id}", response_model=List[Bounty])
def get_bounties_by_contributor(user_id: int):
    """List bounties that a given user has contributed to (boosted)."""
    try:
        bounties = db.get_bounties_by_contributor(user_id)
        return bounties
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get bounties by contributor: {str(e)}")

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
    """Create conditional escrows per-contributor and mark a bounty as accepted."""
    try:
        bounty_public = db.get_bounty_by_id(bounty_id)
        bounty = db.get_bounty_internal_by_id(bounty_id)
        if not bounty:
            raise HTTPException(status_code=404, detail="Bounty not found")
        
        if bounty['status'] != "open":
            raise HTTPException(status_code=400, detail="Bounty is not open")
        
        # Build contributions list (supports legacy single-funder path if none found)
        contributions = db.get_contributions_by_bounty(bounty_id)
        if not contributions:
            # Fallback to legacy single-funder contribution synthesized from bounty
            funder_user = db.get_user_by_id(bounty['funder_id'])
            if not funder_user:
                raise HTTPException(status_code=404, detail="User not found")
            contributions = [{
                'id': -1,
                'bounty_id': bounty_id,
                'contributor_id': funder_user['id'],
                'contributor_address': funder_user['xrp_address'],
                'amount': bounty['amount'],
            }]

        # Validate each contributor has sufficient balance and a seed
        contributor_cache: Dict[int, Dict] = {}
        for c in contributions:
            user = db.get_user_by_id(c['contributor_id'])
            if not user:
                raise HTTPException(status_code=404, detail=f"Contributor {c['contributor_id']} not found")
            if not user.get('xrp_seed'):
                raise HTTPException(status_code=400, detail=f"Contributor {user['username']} has no XRP seed configured")
            if user['current_xrp_balance'] < float(c['amount']):
                raise HTTPException(status_code=400, detail=f"Contributor {user['username']} has insufficient balance for escrow")
            if not xrpl_utils.validate_account_for_escrow(user['xrp_seed'], float(c['amount'])):
                raise HTTPException(status_code=400, detail=f"Contributor {user['username']}: XRPL account validation failed")
            contributor_cache[c['contributor_id']] = user
        
        # For conditional escrow, use the bounty's time limit as CancelAfter window; fallback to 1 day if missing
        cancel_after_seconds = int(bounty.get('time_limit_seconds') or 86400)
        cancel_after_seconds = min(max(cancel_after_seconds, 600), 60 * 60 * 24 * 30)

        # Generate on-chain condition and server-held fulfillment/preimage (shared by all escrows)
        condition_hex, fulfillment_hex, preimage_hex = xrpl_utils.generate_condition_and_fulfillment()

        developer_secret_key = github_utils.generate_developer_secret_key()

        # Create an escrow per contribution
        contribution_escrows: List[Dict[str, any]] = []
        balance_deductions: List[Dict[str, any]] = []
        first_escrow_id = None
        first_escrow_seq = None
        for c in contributions:
            u = contributor_cache[c['contributor_id']]
            try:
                esc = xrpl_utils.create_conditional_escrow(
                    u['xrp_seed'],
                    accept.developer_address,
                    float(c['amount']),
                    cancel_after_seconds,
                    condition_hex
                )
            except Exception as escrow_error:
                error_msg = str(escrow_error)
                if "Insufficient" in error_msg:
                    raise HTTPException(status_code=400, detail=f"{u['username']}: Insufficient XRP to create escrow")
                elif "No permission" in error_msg:
                    raise HTTPException(status_code=400, detail=f"{u['username']}: Account permission error")
                else:
                    raise HTTPException(status_code=500, detail=f"Escrow creation failed for {u['username']}: {error_msg}")

            escrow_id = esc.result['hash']
            escrow_seq = esc.result['tx_json']['Sequence']
            contribution_escrows.append({
                'contribution_id': c['id'],
                'escrow_id': escrow_id,
                'escrow_sequence': escrow_seq,
            })
            balance_deductions.append({'user_id': u['id'], 'amount': float(c['amount'])})
            if first_escrow_id is None:
                first_escrow_id = escrow_id
                first_escrow_seq = escrow_seq

        # Record acceptance and update contribution escrow metadata and balances atomically
        db.accept_bounty_multi(
            bounty_id,
            accept.developer_address,
            first_escrow_id,
            first_escrow_seq,
            developer_secret_key,
            condition_hex,
            fulfillment_hex,
            preimage_hex,
            contribution_escrows,
            balance_deductions
        )
        
        return {
            "message": "Bounty accepted successfully", 
            "bounty_id": bounty_id,
            "funder_id": bounty['funder_id'],
            "developer_secret_key": developer_secret_key,
            "cancel_after_seconds": cancel_after_seconds
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to accept bounty: {str(e)}")

@app.post("/bounties/{bounty_id}/claim")
def claim_bounty(bounty_id: int, claim: BountyClaim):
    """Verify PR and developer key, then finish escrow(s) and mark claimed."""
    try:
        bounty = db.get_bounty_by_id(bounty_id)
        if not bounty:
            raise HTTPException(status_code=404, detail="Bounty not found")
        
        if bounty['status'] != "accepted":
            raise HTTPException(status_code=400, detail="Bounty is not available for claiming")
        
        # Multi-contrib: escrows are recorded on contributions; legacy: on bounty
        
        issue_number = github_utils.extract_issue_number_from_url(bounty['github_issue_url'])
        if not issue_number:
            raise HTTPException(status_code=400, detail="Invalid GitHub issue URL")
        
        # Fetch the stored developer secret key and verify it is present in the PR
        stored_dev_key = db.get_developer_secret_key(bounty_id)
        if not stored_dev_key:
            raise HTTPException(status_code=400, detail="No developer secret key found for this bounty")

        if not github_utils.verify_merge_request_contains_issue(claim.merge_request_url, issue_number, stored_dev_key):
            raise HTTPException(
                status_code=400, 
                detail="Merge request must contain both the issue number reference and the developer secret key"
            )
        
        # Fetch internal to get fulfillment
        internal = db.get_bounty_internal_by_id(bounty_id)
        if not internal or not internal.get('escrow_fulfillment'):
            raise HTTPException(status_code=400, detail="No escrow fulfillment available")

        try:
            # Determine contributions with escrows
            contributions = db.get_contributions_by_bounty(bounty_id)
            tx_results = []
            if contributions:
                for c in contributions:
                    if not c.get('escrow_sequence'):
                        continue
                    contributor = db.get_user_by_id(c['contributor_id'])
                    if not contributor or not contributor.get('xrp_seed'):
                        continue
                    tx_response = xrpl_utils.finish_conditional_escrow(
                        owner_address=c['contributor_address'],
                        offer_sequence=c['escrow_sequence'],
                        finisher_seed=contributor['xrp_seed'],
                        fulfillment_hex=internal['escrow_fulfillment']
                    )
                    tx_results.append(tx_response.result)
            else:
                # Legacy single-escrow path on bounty
                funder = db.get_user_by_id(bounty['funder_id'])
                if not funder:
                    raise HTTPException(status_code=404, detail="Funder not found")
                tx_response = xrpl_utils.finish_conditional_escrow(
                    owner_address=bounty['funder_address'],
                    offer_sequence=bounty['escrow_sequence'],
                    finisher_seed=funder['xrp_seed'],
                    fulfillment_hex=internal['escrow_fulfillment']
                )
                tx_results.append(tx_response.result)

            db.claim_bounty(bounty_id)
            
            return {
                "message": "Bounty claimed successfully and escrow(s) fulfilled",
                "bounty_id": bounty_id,
                "funder_id": bounty['funder_id'],
                "developer_address": bounty['developer_address'],
                "merge_request_url": claim.merge_request_url,
                "status": "claimed",
                "tx_results": tx_results
            }
            
        except Exception as e:
            error_msg = str(e)
            # Could not finish escrow; likely condition/permission issue
            if "tecNO_PERMISSION" in error_msg or "No permission" in error_msg:
                raise HTTPException(status_code=400, detail="Escrow cannot be finished at this time. Verify the fulfillment and try again later.")

            raise HTTPException(status_code=500, detail=f"Failed to fulfill time-based escrow: {error_msg}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to claim bounty: {str(e)}")

@app.post("/bounties/{bounty_id}/boost")
def boost_bounty(bounty_id: int, boost: BountyBoost):
    """Add additional funds to an existing open bounty by another user."""
    try:
        bounty = db.get_bounty_by_id(bounty_id)
        if not bounty:
            raise HTTPException(status_code=404, detail="Bounty not found")
        if bounty['status'] != 'open':
            raise HTTPException(status_code=400, detail="Can only boost an open bounty")

        # Disallow creator boosting by requirement; relax if desired
        if boost.contributor_id == bounty['funder_id']:
            raise HTTPException(status_code=400, detail="Creator cannot boost their own bounty")

        if boost.amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be positive")

        user = db.get_user_by_id(boost.contributor_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user['current_xrp_balance'] < boost.amount:
            raise HTTPException(status_code=400, detail="Insufficient balance to pledge this amount")

        contribution_id = db.add_contribution(bounty_id, boost.contributor_id, float(boost.amount))
        updated = db.get_bounty_by_id(bounty_id)
        return {
            "message": "Boost added",
            "bounty_id": bounty_id,
            "contribution_id": contribution_id,
            "new_amount": updated['amount'] if updated else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to boost bounty: {str(e)}")

@app.get("/bounties/{bounty_id}/contributions", response_model=List[BountyContribution])
def get_bounty_contributions(bounty_id: int):
    """List contributions for a bounty, including escrow identifiers if created."""
    try:
        bounty = db.get_bounty_by_id(bounty_id)
        if not bounty:
            raise HTTPException(status_code=404, detail="Bounty not found")
        contributions = db.get_contributions_by_bounty(bounty_id)
        return contributions
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get contributions: {str(e)}")

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
            developer_secret_key=bounty['developer_secret_key'],
            status=bounty['status'],
            created_at=bounty['created_at'],
            updated_at=bounty['updated_at']
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get bounty: {str(e)}")

@app.get("/bounties/{bounty_id}/developer-secret")
def get_bounty_developer_secret(bounty_id: int, user_id: int):
    """Return the developer secret key only if the caller is the assigned developer."""
    try:
        bounty = db.get_bounty_internal_by_id(bounty_id)
        if not bounty:
            raise HTTPException(status_code=404, detail="Bounty not found")

        # Must be accepted and have a developer assigned
        if not bounty.get('developer_address'):
            raise HTTPException(status_code=400, detail="No developer assigned for this bounty")

        user = db.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.get('xrp_address') != bounty.get('developer_address'):
            raise HTTPException(status_code=403, detail="Forbidden: Not the assigned developer")

        dev_key = db.get_developer_secret_key(bounty_id)
        if not dev_key:
            raise HTTPException(status_code=404, detail="Developer secret key not found")

        return {"developer_secret_key": dev_key}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get developer secret: {str(e)}")

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
            funding_result = xrpl_utils.fund_existing_wallet(user['xrp_seed'])
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