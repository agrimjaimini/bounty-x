from supabase import create_client, Client
from fastapi import HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from config import settings
from database_service import database_service

# Security scheme for JWT tokens
security = HTTPBearer()

class AuthService:
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
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")
    
    async def register_user(self, email: str, password: str, username: str) -> Dict[str, Any]:
        """Register a new user with Supabase Auth"""
        try:
            # Register user with Supabase Auth
            auth_response = self.supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            if auth_response.user:
                # Store additional user data in Supabase database
                user_data = {
                    "id": auth_response.user.id,
                    "email": email,
                    "username": username,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                # Insert into profiles table (you'll need to create this in Supabase)
                try:
                    self.supabase.table("profiles").insert(user_data).execute()
                except Exception as e:
                    print(f"Warning: Could not insert into profiles table: {e}")
                
                return {
                    "user_id": auth_response.user.id,
                    "email": email,
                    "username": username,
                    "message": "User registered successfully"
                }
            else:
                raise HTTPException(status_code=400, detail="Failed to register user")
                
        except Exception as e:
            if "User already registered" in str(e):
                raise HTTPException(status_code=400, detail="User already registered")
            raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")
    
    async def login_user(self, email: str, password: str) -> Dict[str, Any]:
        """Login user with Supabase Auth"""
        try:
            # Sign in with Supabase Auth
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user:
                # Create access token
                access_token = self.create_access_token(
                    data={"sub": auth_response.user.id, "email": email}
                )
                
                # Get user profile data
                try:
                    profile_response = self.supabase.table("profiles").select("*").eq("id", auth_response.user.id).execute()
                    username = profile_response.data[0].get("username", "") if profile_response.data else ""
                except:
                    username = ""
                
                return {
                    "access_token": access_token,
                    "token_type": "bearer",
                    "user_id": auth_response.user.id,
                    "email": email,
                    "username": username
                }
            else:
                raise HTTPException(status_code=401, detail="Invalid credentials")
                
        except Exception as e:
            if "Invalid login credentials" in str(e):
                raise HTTPException(status_code=401, detail="Invalid credentials")
            raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
        """Get current authenticated user from JWT token"""
        token = credentials.credentials
        payload = self.verify_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Get user data from Supabase
        try:
            profile_response = self.supabase.table("profiles").select("*").eq("id", user_id).execute()
            if not profile_response.data:
                raise HTTPException(status_code=401, detail="User not found")
            
            user_data = profile_response.data[0]
            
            # Get user's wallet
            wallet = await database_service.get_user_wallet(user_id)
            
            return {
                "id": user_id,
                "email": payload.get("email"),
                "username": user_data.get("username"),
                "xrp_address": wallet.get("wallet_address") if wallet else None,
                "xrp_secret": wallet.get("wallet_secret") if wallet else None,
                "wallet_balance": wallet.get("balance", 0) if wallet else 0
            }
        except Exception as e:
            raise HTTPException(status_code=401, detail="Failed to get user data")

# Initialize auth service
auth_service = AuthService() 