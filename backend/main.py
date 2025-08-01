from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import re
import requests
from xrpl.clients import JsonRpcClient
from xrpl.wallet import Wallet
from xrpl.models.transactions import EscrowCreate, EscrowFinish, Payment
from xrpl.transaction import reliable_submission
from xrpl.models.requests import AccountInfo
from xrpl.utils import xrp_to_drops

# Import Supabase services
from auth_service import auth_service
from database_service import database_service
from config import settings

app = FastAPI()

def create_funded_testnet_wallet():
    """
    Create a new testnet wallet and fund it with 50 XRP
    Returns: (wallet, address, secret)
    """
    try:
        # Connect to XRPL testnet
        client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
        
        # Create a new wallet
        wallet = Wallet.create()
        
        # Fund the wallet with 50 XRP using the testnet faucet
        # First, we need to get a funded account to send from
        # For demo purposes, we'll use the testnet faucet directly
        
        # Get account info to check if it's funded
        account_info = AccountInfo(account=wallet.classic_address)
        response = client.request(account_info)
        
        # If account is not funded, we need to fund it
        if response.result.get("account_data") is None:
            # Use the testnet faucet to fund the account
            faucet_response = requests.post(
                "https://faucet.altnet.rippletest.net/accounts",
                json={"destination": wallet.classic_address}
            )
            
            if faucet_response.status_code != 200:
                raise Exception("Failed to fund wallet from faucet")
            
            faucet_data = faucet_response.json()
            print(f"Funded wallet {wallet.classic_address} with {faucet_data.get('amount', 'unknown')} XRP")
        
        return wallet, wallet.classic_address, wallet.seed
        
    except Exception as e:
        print(f"Error creating funded wallet: {e}")
        raise e

# Authentication models
class UserRegister(BaseModel):
    email: str
    password: str
    username: str

class UserLogin(BaseModel):
    email: str
    password: str

class User(BaseModel):
    id: str
    email: str
    username: str
    xrp_address: Optional[str]
    wallet_balance: float = 0
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: str
    email: str
    username: str

class BountyCreate(BaseModel):
    github_issue_url: str
    amount: float
    finish_after: int = 86400  # Default 24 hours in seconds

class BountyAccept(BaseModel):
    finish_after: int = 86400  # Default 24 hours in seconds

class BountyClaim(BaseModel):
    merge_request_url: str

class Bounty(BaseModel):
    id: str
    github_issue_url: str
    funder_address: str
    developer_address: Optional[str]
    amount: float
    escrow_id: Optional[str]
    escrow_sequence: Optional[int]
    status: str
    created_at: str
    updated_at: str

class EscrowTransaction(BaseModel):
    id: str
    bounty_id: str
    transaction_type: str
    xrpl_tx_hash: Optional[str]
    escrow_id: Optional[str]
    escrow_sequence: Optional[int]
    amount: float
    from_address: str
    to_address: str
    status: str
    created_at: str
    confirmed_at: Optional[str]

# Authentication endpoints
@app.post("/register", response_model=dict)
async def register_user(user: UserRegister):
    try:
        # Create and fund a testnet wallet
        wallet, address, secret = create_funded_testnet_wallet()
        
        # Register user with Supabase Auth
        result = await auth_service.register_user(
            email=user.email,
            password=user.password,
            username=user.username
        )
        
        # Create user wallet in database
        await database_service.create_user_wallet(
            user_id=result["user_id"],
            wallet_address=address,
            wallet_secret=secret
        )
        
        return {
            **result,
            "xrp_address": address
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to register user: {str(e)}")

@app.post("/login", response_model=TokenResponse)
async def login_user(user: UserLogin):
    try:
        result = await auth_service.login_user(
            email=user.email,
            password=user.password
        )
        return TokenResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.post("/logout")
async def logout_user(current_user: dict = Depends(auth_service.get_current_user)):
    # With JWT tokens, logout is typically handled client-side by removing the token
    # You could implement a token blacklist here if needed
    return {"message": "Logout successful"}

@app.get("/me", response_model=User)
async def get_current_user_info(current_user: dict = Depends(auth_service.get_current_user)):
    return User(
        id=current_user["id"],
        email=current_user["email"],
        username=current_user["username"],
        xrp_address=current_user.get("xrp_address"),
        wallet_balance=current_user.get("wallet_balance", 0),
        created_at=datetime.utcnow().isoformat()  # You might want to get this from the profile
    )

@app.post("/bounties/", response_model=Bounty)
async def create_bounty(bounty: BountyCreate, current_user: dict = Depends(auth_service.get_current_user)):
    # Get user's wallet
    user_wallet = await database_service.get_user_wallet(current_user["id"])
    if not user_wallet:
        raise HTTPException(status_code=400, detail="User wallet not found")
    
    # Create bounty in database
    bounty_data = await database_service.create_bounty(
        github_issue_url=bounty.github_issue_url,
        funder_address=user_wallet["wallet_address"],
        amount=bounty.amount
    )
    
    return Bounty(
        id=bounty_data["id"],
        github_issue_url=bounty_data["github_issue_url"],
        funder_address=bounty_data["funder_address"],
        developer_address=bounty_data.get("developer_address"),
        amount=bounty_data["amount"],
        escrow_id=bounty_data.get("escrow_id"),
        escrow_sequence=bounty_data.get("escrow_sequence"),
        status=bounty_data["status"],
        created_at=bounty_data["created_at"],
        updated_at=bounty_data["updated_at"]
    )

@app.get("/bounties/", response_model=List[Bounty])
async def list_bounties(current_user: dict = Depends(auth_service.get_current_user)):
    bounties_data = await database_service.list_bounties()
    
    return [Bounty(
        id=bounty["id"],
        github_issue_url=bounty["github_issue_url"],
        funder_address=bounty["funder_address"],
        developer_address=bounty.get("developer_address"),
        amount=bounty["amount"],
        escrow_id=bounty.get("escrow_id"),
        escrow_sequence=bounty.get("escrow_sequence"),
        status=bounty["status"],
        created_at=bounty["created_at"],
        updated_at=bounty["updated_at"]
    ) for bounty in bounties_data]

@app.get("/bounties/my", response_model=List[Bounty])
async def get_my_bounties(current_user: dict = Depends(auth_service.get_current_user)):
    # Get user's wallet
    user_wallet = await database_service.get_user_wallet(current_user["id"])
    if not user_wallet:
        raise HTTPException(status_code=400, detail="User wallet not found")
    
    bounties_data = await database_service.get_bounties_by_user(user_wallet["wallet_address"])
    
    return [Bounty(
        id=bounty["id"],
        github_issue_url=bounty["github_issue_url"],
        funder_address=bounty["funder_address"],
        developer_address=bounty.get("developer_address"),
        amount=bounty["amount"],
        escrow_id=bounty.get("escrow_id"),
        escrow_sequence=bounty.get("escrow_sequence"),
        status=bounty["status"],
        created_at=bounty["created_at"],
        updated_at=bounty["updated_at"]
    ) for bounty in bounties_data]

@app.post("/bounties/{bounty_id}/accept")
async def accept_bounty(bounty_id: str, accept: BountyAccept, current_user: dict = Depends(auth_service.get_current_user)):
    # Get bounty
    bounty_data = await database_service.get_bounty(bounty_id)
    if not bounty_data:
        raise HTTPException(status_code=404, detail="Bounty not found")
    
    # Check if bounty is available for accepting
    if bounty_data['status'] != "open":
        raise HTTPException(status_code=400, detail="Bounty is not available for accepting")
    
    if bounty_data['developer_address']:
        raise HTTPException(status_code=400, detail="Bounty has already been accepted")
    
    # Get user's wallet
    user_wallet = await database_service.get_user_wallet(current_user["id"])
    if not user_wallet:
        raise HTTPException(status_code=400, detail="User wallet not found")
    
    # Get funder's wallet
    funder_wallet = await database_service.get_wallet_by_address(bounty_data['funder_address'])
    if not funder_wallet:
        raise HTTPException(status_code=400, detail="Funder wallet not found")
    
    # Create escrow on XRPL
    try:
        # XRPL testnet
        client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
        
        # Use the funder's wallet
        funder_wallet_obj = Wallet(seed=funder_wallet["wallet_secret"], sequence=0)
        
        escrow_tx = EscrowCreate(
            account=bounty_data['funder_address'],
            amount=str(xrp_to_drops(bounty_data['amount'])),
            destination=user_wallet["wallet_address"],
            finish_after=int(datetime.utcnow().timestamp()) + accept.finish_after,
        )
        
        tx_response = reliable_submission(escrow_tx, client, funder_wallet_obj)
        escrow_id = tx_response.result.get("hash")
        escrow_sequence = tx_response.result.get("Sequence")
        
        # Create escrow transaction record
        await database_service.create_escrow_transaction(
            bounty_id=bounty_id,
            transaction_type="create",
            xrpl_tx_hash=escrow_id,
            escrow_id=escrow_id,
            escrow_sequence=escrow_sequence,
            amount=bounty_data['amount'],
            from_address=bounty_data['funder_address'],
            to_address=user_wallet["wallet_address"]
        )
        
        # Update bounty with escrow ID, sequence, and status
        await database_service.update_bounty(bounty_id, {
            "developer_address": user_wallet["wallet_address"],
            "escrow_id": escrow_id,
            "escrow_sequence": escrow_sequence,
            "status": "funded"
        })
        
        return {
            "message": "Bounty accepted and escrow created successfully",
            "bounty_id": bounty_id,
            "developer_address": user_wallet["wallet_address"],
            "status": "funded",
            "escrow_id": escrow_id,
            "tx_response": tx_response.result
        }
        
    except Exception as e:
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
async def claim_bounty(bounty_id: str, claim: BountyClaim, current_user: dict = Depends(auth_service.get_current_user)):
    # Get bounty
    bounty_data = await database_service.get_bounty(bounty_id)
    if not bounty_data:
        raise HTTPException(status_code=404, detail="Bounty not found")
    
    # Check if bounty is available for claiming (must be funded)
    if bounty_data['status'] != "funded":
        raise HTTPException(status_code=400, detail="Bounty is not available for claiming")
    
    # Get user's wallet
    user_wallet = await database_service.get_user_wallet(current_user["id"])
    if not user_wallet:
        raise HTTPException(status_code=400, detail="User wallet not found")
    
    # Check if the developer address matches the accepted developer
    if bounty_data['developer_address'] != user_wallet["wallet_address"]:
        raise HTTPException(status_code=400, detail="Only the accepted developer can claim this bounty")
    
    # Check if escrow exists
    if not bounty_data['escrow_id']:
        raise HTTPException(status_code=400, detail="No escrow found for this bounty")
    
    # Extract issue number from bounty
    issue_number = extract_issue_number_from_url(bounty_data['github_issue_url'])
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
        
        # Use the developer's wallet
        developer_wallet_obj = Wallet(seed=user_wallet["wallet_secret"], sequence=0)
        
        # Create escrow finish transaction
        escrow_finish_tx = EscrowFinish(
            account=user_wallet["wallet_address"],
            owner=bounty_data['funder_address'],
            offer_sequence=bounty_data['escrow_sequence'],
        )
        
        # Submit the transaction
        tx_response = reliable_submission(escrow_finish_tx, client, developer_wallet_obj)
        
        # Create escrow transaction record
        await database_service.create_escrow_transaction(
            bounty_id=bounty_id,
            transaction_type="finish",
            xrpl_tx_hash=tx_response.result.get("hash"),
            escrow_id=bounty_data['escrow_id'],
            escrow_sequence=bounty_data['escrow_sequence'],
            amount=bounty_data['amount'],
            from_address=bounty_data['funder_address'],
            to_address=user_wallet["wallet_address"]
        )
        
        # Update bounty status to claimed
        await database_service.update_bounty(bounty_id, {
            "status": "claimed"
        })
        
        return {
            "message": "Bounty claimed successfully and escrow fulfilled",
            "bounty_id": bounty_id,
            "developer_address": user_wallet["wallet_address"],
            "merge_request_url": claim.merge_request_url,
            "status": "claimed",
            "escrow_id": bounty_data['escrow_id'],
            "tx_response": tx_response.result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fulfill escrow: {str(e)}")

@app.get("/bounties/{bounty_id}", response_model=Bounty)
async def get_bounty(bounty_id: str, current_user: dict = Depends(auth_service.get_current_user)):
    bounty_data = await database_service.get_bounty(bounty_id)
    if not bounty_data:
        raise HTTPException(status_code=404, detail="Bounty not found")
    
    return Bounty(
        id=bounty_data["id"],
        github_issue_url=bounty_data["github_issue_url"],
        funder_address=bounty_data["funder_address"],
        developer_address=bounty_data.get("developer_address"),
        amount=bounty_data["amount"],
        escrow_id=bounty_data.get("escrow_id"),
        escrow_sequence=bounty_data.get("escrow_sequence"),
        status=bounty_data["status"],
        created_at=bounty_data["created_at"],
        updated_at=bounty_data["updated_at"]
    )

@app.get("/bounties/{bounty_id}/transactions", response_model=List[EscrowTransaction])
async def get_bounty_transactions(bounty_id: str, current_user: dict = Depends(auth_service.get_current_user)):
    # Verify bounty exists
    bounty_data = await database_service.get_bounty(bounty_id)
    if not bounty_data:
        raise HTTPException(status_code=404, detail="Bounty not found")
    
    # Get escrow transactions
    transactions_data = await database_service.get_escrow_transactions_by_bounty(bounty_id)
    
    return [EscrowTransaction(
        id=tx["id"],
        bounty_id=tx["bounty_id"],
        transaction_type=tx["transaction_type"],
        xrpl_tx_hash=tx.get("xrpl_tx_hash"),
        escrow_id=tx.get("escrow_id"),
        escrow_sequence=tx.get("escrow_sequence"),
        amount=tx["amount"],
        from_address=tx["from_address"],
        to_address=tx["to_address"],
        status=tx["status"],
        created_at=tx["created_at"],
        confirmed_at=tx.get("confirmed_at")
    ) for tx in transactions_data]

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint to verify the API is running"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Bounty-X API",
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to Bounty-X API",
        "description": "XRPL Testnet Feature Bounty Portal",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "auth": {
                "register": "POST /register",
                "login": "POST /login",
                "logout": "POST /logout",
                "me": "GET /me"
            },
            "bounties": {
                "create": "POST /bounties/",
                "list": "GET /bounties/",
                "my_bounties": "GET /bounties/my",
                "get": "GET /bounties/{id}",
                "accept": "POST /bounties/{id}/accept",
                "claim": "POST /bounties/{id}/claim",
                "transactions": "GET /bounties/{id}/transactions"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    import sys
    import os
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print("🚀 Starting Bounty-X API Server...")
    print(f"📍 Server will be available at: http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🏥 Health Check: http://{host}:{port}/health")
    print()
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Run the FastAPI application
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=True,  # Enable auto-reload for development
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1) 