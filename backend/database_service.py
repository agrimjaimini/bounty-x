from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from datetime import datetime
from config import settings
from fastapi import HTTPException
import uuid

class DatabaseService:
    def __init__(self):
        self._supabase = None
    
    @property
    def supabase(self) -> Client:
        """Lazy initialization of Supabase client"""
        if self._supabase is None:
            if not settings.validate_supabase_config():
                raise HTTPException(status_code=500, detail="Supabase configuration not found. Please check your .env file.")
            self._supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
        return self._supabase
    
    # User Wallet Operations
    async def create_user_wallet(self, user_id: str, wallet_address: str, wallet_secret: str) -> Dict[str, Any]:
        """Create a new user wallet"""
        try:
            wallet_data = {
                "user_id": user_id,
                "wallet_address": wallet_address,
                "wallet_secret": wallet_secret,
                "balance": 0,
                "is_active": True
            }
            
            response = self.supabase.table("user_wallets").insert(wallet_data).execute()
            
            if response.data:
                return response.data[0]
            else:
                raise HTTPException(status_code=500, detail="Failed to create wallet")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    async def get_user_wallet(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user's wallet by user ID"""
        try:
            response = self.supabase.table("user_wallets").select("*").eq("user_id", user_id).eq("is_active", True).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    async def get_wallet_by_address(self, wallet_address: str) -> Optional[Dict[str, Any]]:
        """Get wallet by address"""
        try:
            response = self.supabase.table("user_wallets").select("*").eq("wallet_address", wallet_address).eq("is_active", True).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    async def update_wallet_balance(self, wallet_address: str, new_balance: float) -> Dict[str, Any]:
        """Update wallet balance"""
        try:
            response = self.supabase.table("user_wallets").update({
                "balance": new_balance,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("wallet_address", wallet_address).execute()
            
            if response.data:
                return response.data[0]
            else:
                raise HTTPException(status_code=404, detail="Wallet not found")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Bounty Operations
    async def create_bounty(self, github_issue_url: str, funder_address: str, amount: float) -> Dict[str, Any]:
        """Create a new bounty"""
        try:
            bounty_data = {
                "github_issue_url": github_issue_url,
                "funder_address": funder_address,
                "amount": amount,
                "status": "open"
            }
            
            response = self.supabase.table("bounties").insert(bounty_data).execute()
            
            if response.data:
                return response.data[0]
            else:
                raise HTTPException(status_code=500, detail="Failed to create bounty")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    async def get_bounty(self, bounty_id: str) -> Optional[Dict[str, Any]]:
        """Get bounty by ID"""
        try:
            response = self.supabase.table("bounties").select("*").eq("id", bounty_id).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    async def list_bounties(self) -> List[Dict[str, Any]]:
        """List all bounties"""
        try:
            response = self.supabase.table("bounties").select("*").order("created_at", desc=True).execute()
            return response.data or []
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    async def update_bounty(self, bounty_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update bounty"""
        try:
            response = self.supabase.table("bounties").update(update_data).eq("id", bounty_id).execute()
            
            if response.data:
                return response.data[0]
            else:
                raise HTTPException(status_code=404, detail="Bounty not found")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    async def get_bounties_by_user(self, wallet_address: str) -> List[Dict[str, Any]]:
        """Get bounties by funder or developer address"""
        try:
            response = self.supabase.table("bounties").select("*").or_(f"funder_address.eq.{wallet_address},developer_address.eq.{wallet_address}").execute()
            return response.data or []
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Escrow Transaction Operations
    async def create_escrow_transaction(self, bounty_id: str, transaction_type: str, 
                                      xrpl_tx_hash: str, escrow_id: str, escrow_sequence: int,
                                      amount: float, from_address: str, to_address: str) -> Dict[str, Any]:
        """Create a new escrow transaction record"""
        try:
            escrow_data = {
                "bounty_id": bounty_id,
                "transaction_type": transaction_type,
                "xrpl_tx_hash": xrpl_tx_hash,
                "escrow_id": escrow_id,
                "escrow_sequence": escrow_sequence,
                "amount": amount,
                "from_address": from_address,
                "to_address": to_address,
                "status": "pending"
            }
            
            response = self.supabase.table("escrow_transactions").insert(escrow_data).execute()
            
            if response.data:
                return response.data[0]
            else:
                raise HTTPException(status_code=500, detail="Failed to create escrow transaction")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    async def update_escrow_transaction_status(self, escrow_id: str, status: str) -> Dict[str, Any]:
        """Update escrow transaction status"""
        try:
            update_data = {
                "status": status,
                "confirmed_at": datetime.utcnow().isoformat() if status == "confirmed" else None
            }
            
            response = self.supabase.table("escrow_transactions").update(update_data).eq("escrow_id", escrow_id).execute()
            
            if response.data:
                return response.data[0]
            else:
                raise HTTPException(status_code=404, detail="Escrow transaction not found")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    async def get_escrow_transactions_by_bounty(self, bounty_id: str) -> List[Dict[str, Any]]:
        """Get escrow transactions for a bounty"""
        try:
            response = self.supabase.table("escrow_transactions").select("*").eq("bounty_id", bounty_id).order("created_at", desc=True).execute()
            return response.data or []
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Profile Operations
    async def update_user_profile(self, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile"""
        try:
            response = self.supabase.table("profiles").update(update_data).eq("id", user_id).execute()
            
            if response.data:
                return response.data[0]
            else:
                raise HTTPException(status_code=404, detail="Profile not found")
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile"""
        try:
            response = self.supabase.table("profiles").select("*").eq("id", user_id).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

# Initialize database service
database_service = DatabaseService() 