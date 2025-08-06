import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import contextlib

# Database configuration
DB_PATH = "bounties.db"

class DatabaseError(Exception):
    """Custom exception for database operations"""
    pass

@contextlib.contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Initialize the database with required tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create bounties table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bounties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                funder_id INTEGER NOT NULL,
                bounty_name TEXT NOT NULL,
                github_issue_url TEXT NOT NULL,
                funder_address TEXT NOT NULL,
                developer_address TEXT,
                amount REAL NOT NULL,
                escrow_id TEXT,
                escrow_sequence INTEGER,
                escrow_condition TEXT,
                escrow_fulfillment TEXT,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                xrp_address TEXT,
                xrp_secret TEXT,
                xrp_seed TEXT, 
                bounties_created INTEGER DEFAULT 0,
                bounties_accepted INTEGER DEFAULT 0,
                total_xrp_funded REAL DEFAULT 0.0,
                total_xrp_earned REAL DEFAULT 0.0,
                current_xrp_balance REAL DEFAULT 0.0,
                last_updated TEXT NOT NULL
            )
        ''')
        
        conn.commit()

# User Management Functions
def create_user(username: str, password: str, xrp_address: str, xrp_secret: str, xrp_seed: str, balance: float) -> int:
    """Create a new user and return the user ID"""
    try:
        now = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, password, xrp_address, xrp_secret, xrp_seed, current_xrp_balance, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, password, xrp_address, xrp_secret, xrp_seed, balance, now))
            conn.commit()
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        raise DatabaseError("Username already exists")
    except Exception as e:
        raise DatabaseError(f"Failed to create user: {str(e)}")

def get_user_by_credentials(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Get user by username and password"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, password, xrp_address, xrp_secret, xrp_seed, 
                       bounties_created, bounties_accepted, total_xrp_funded, 
                       total_xrp_earned, current_xrp_balance, last_updated
                FROM users 
                WHERE username = ? AND password = ?
            ''', (username, password))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'username': row[1],
                    'password': row[2],
                    'xrp_address': row[3],
                    'xrp_secret': row[4],
                    'xrp_seed': row[5],
                    'bounties_created': row[6],
                    'bounties_accepted': row[7],
                    'total_xrp_funded': row[8],
                    'total_xrp_earned': row[9],
                    'current_xrp_balance': row[10],
                    'last_updated': row[11]
                }
            return None
    except Exception as e:
        raise DatabaseError(f"Failed to get user: {str(e)}")

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, password, xrp_address, xrp_secret, xrp_seed,
                       bounties_created, bounties_accepted, total_xrp_funded, 
                       total_xrp_earned, current_xrp_balance, last_updated
                FROM users 
                WHERE id = ?
            ''', (user_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'username': row[1],
                    'password': row[2],
                    'xrp_address': row[3],
                    'xrp_secret': row[4],
                    'xrp_seed': row[5],
                    'bounties_created': row[6],
                    'bounties_accepted': row[7],
                    'total_xrp_funded': row[8],
                    'total_xrp_earned': row[9],
                    'current_xrp_balance': row[10],
                    'last_updated': row[11]
                }
            return None
    except Exception as e:
        raise DatabaseError(f"Failed to get user: {str(e)}")

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Get user by username"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, username, password, xrp_address, xrp_secret, xrp_seed,
                       bounties_created, bounties_accepted, total_xrp_funded, 
                       total_xrp_earned, current_xrp_balance, last_updated
                FROM users 
                WHERE username = ?
            ''', (username,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'username': row[1],
                    'password': row[2],
                    'xrp_address': row[3],
                    'xrp_secret': row[4],
                    'xrp_seed': row[5],
                    'bounties_created': row[6],
                    'bounties_accepted': row[7],
                    'total_xrp_funded': row[8],
                    'total_xrp_earned': row[9],
                    'current_xrp_balance': row[10],
                    'last_updated': row[11]
                }
            return None
    except Exception as e:
        raise DatabaseError(f"Failed to get user: {str(e)}")

def get_all_users() -> List[Dict[str, Any]]:
    """Get all users (for debugging)"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id, username, xrp_address FROM users ORDER BY id')
            rows = cursor.fetchall()
            
            return [{
                'id': row[0],
                'username': row[1],
                'xrp_address': row[2]
            } for row in rows]
    except Exception as e:
        raise DatabaseError(f"Failed to get users: {str(e)}")

def update_user_bounty_created(user_id: int, amount: float) -> bool:
    """Update user statistics when a bounty is created"""
    try:
        now = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET bounties_created = bounties_created + 1,
                    total_xrp_funded = total_xrp_funded + ?,
                    last_updated = ?
                WHERE id = ?
            ''', (amount, now, user_id))
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        raise DatabaseError(f"Failed to update user bounty created stats: {str(e)}")

def update_user_bounty_accepted(user_id: int) -> bool:
    """Update user statistics when a bounty is accepted"""
    try:
        now = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET bounties_accepted = bounties_accepted + 1,
                    last_updated = ?
                WHERE id = ?
            ''', (now, user_id))
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        raise DatabaseError(f"Failed to update user bounty accepted stats: {str(e)}")

def update_user_bounty_claimed(user_id: int, amount: float) -> bool:
    """Update user statistics when a bounty is claimed"""
    try:
        now = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET total_xrp_earned = total_xrp_earned + ?,
                    current_xrp_balance = current_xrp_balance + ?,
                    last_updated = ?
                WHERE id = ?
            ''', (amount, amount, now, user_id))
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        raise DatabaseError(f"Failed to update user bounty claimed stats: {str(e)}")

def update_user_xrp_balance(user_id: int, new_balance: float) -> bool:
    """Update user's current XRP balance"""
    try:
        now = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE users 
                SET current_xrp_balance = ?,
                    last_updated = ?
                WHERE id = ?
            ''', (new_balance, now, user_id))
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        raise DatabaseError(f"Failed to update user XRP balance: {str(e)}")

# Bounty Management Functions
def create_bounty(funder_id: int, bounty_name: str, github_issue_url: str, funder_address: str, amount: float) -> int:
    """Create a new bounty and return the bounty ID"""
    try:
        now = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Check if user has sufficient balance
            cursor.execute('SELECT current_xrp_balance FROM users WHERE id = ?', (funder_id,))
            user_balance = cursor.fetchone()
            if not user_balance:
                raise DatabaseError("User not found")
            
            if user_balance[0] < amount:
                raise DatabaseError(f"Insufficient balance. Current: {user_balance[0]} XRP, Required: {amount} XRP")
            
            cursor.execute('''
                INSERT INTO bounties (funder_id, bounty_name, github_issue_url, funder_address, amount, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (funder_id, bounty_name, github_issue_url, funder_address, amount, "open", now, now))
            bounty_id = cursor.lastrowid
            
            # Update funder's statistics (don't decrease balance yet - escrow will handle that)
            cursor.execute('''
                UPDATE users 
                SET bounties_created = bounties_created + 1,
                    total_xrp_funded = total_xrp_funded + ?,
                    last_updated = ?
                WHERE id = ?
            ''', (amount, now, funder_id))
            
            conn.commit()
            return bounty_id
    except Exception as e:
        raise DatabaseError(f"Failed to create bounty: {str(e)}")

def get_bounty_by_id(bounty_id: int) -> Optional[Dict[str, Any]]:
    """Get bounty by ID"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM bounties WHERE id = ?', (bounty_id,))
            row = cursor.fetchone()
            
            if row:
                return {
                    'id': row[0],
                    'funder_id': row[1],
                    'bounty_name': row[2],
                    'github_issue_url': row[3],
                    'funder_address': row[4],
                    'developer_address': row[5],
                    'amount': row[6],
                    'escrow_id': row[7],
                    'escrow_sequence': row[8],
                    'escrow_condition': row[9],
                    'escrow_fulfillment': row[10],
                    'status': row[11],
                    'created_at': row[12],
                    'updated_at': row[13]
                }
            return None
    except Exception as e:
        raise DatabaseError(f"Failed to get bounty: {str(e)}")

def get_all_bounties() -> List[Dict[str, Any]]:
    """Get all bounties"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM bounties ORDER BY created_at DESC')
            rows = cursor.fetchall()
            
            return [{
                'id': row[0],
                'funder_id': row[1],
                'bounty_name': row[2],
                'github_issue_url': row[3],
                'funder_address': row[4],
                'developer_address': row[5],
                'amount': row[6],
                'escrow_id': row[7],
                'escrow_sequence': row[8],
                'escrow_condition': row[9],
                'escrow_fulfillment': row[10],
                'status': row[11],
                'created_at': row[12],
                'updated_at': row[13]
            } for row in rows]
    except Exception as e:
        raise DatabaseError(f"Failed to get bounties: {str(e)}")

def get_bounties_by_status(status: str) -> List[Dict[str, Any]]:
    """Get bounties by status"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM bounties WHERE status = ? ORDER BY created_at DESC', (status,))
            rows = cursor.fetchall()
            
            return [{
                'id': row[0],
                'funder_id': row[1],
                'bounty_name': row[2],
                'github_issue_url': row[3],
                'funder_address': row[4],
                'developer_address': row[5],
                'amount': row[6],
                'escrow_id': row[7],
                'escrow_sequence': row[8],
                'escrow_condition': row[9],
                'escrow_fulfillment': row[10],
                'status': row[11],
                'created_at': row[12],
                'updated_at': row[13]
            } for row in rows]
    except Exception as e:
        raise DatabaseError(f"Failed to get bounties by status: {str(e)}")

def get_bounties_by_funder(funder_id: int) -> List[Dict[str, Any]]:
    """Get bounties by funder ID"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM bounties WHERE funder_id = ? ORDER BY created_at DESC', (funder_id,))
            rows = cursor.fetchall()
            
            return [{
                'id': row[0],
                'funder_id': row[1],
                'bounty_name': row[2],
                'github_issue_url': row[3],
                'funder_address': row[4],
                'developer_address': row[5],
                'amount': row[6],
                'escrow_id': row[7],
                'escrow_sequence': row[8],
                'escrow_condition': row[9],
                'escrow_fulfillment': row[10],
                'status': row[11],
                'created_at': row[12],
                'updated_at': row[13]
            } for row in rows]
    except Exception as e:
        raise DatabaseError(f"Failed to get bounties by funder: {str(e)}")

def get_bounties_by_developer(developer_address: str) -> List[Dict[str, Any]]:
    """Get bounties by developer address"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM bounties WHERE developer_address = ? ORDER BY created_at DESC', (developer_address,))
            rows = cursor.fetchall()
            
            return [{
                'id': row[0],
                'funder_id': row[1],
                'bounty_name': row[2],
                'github_issue_url': row[3],
                'funder_address': row[4],
                'developer_address': row[5],
                'amount': row[6],
                'escrow_id': row[7],
                'escrow_sequence': row[8],
                'escrow_condition': row[9],
                'escrow_fulfillment': row[10],
                'status': row[11],
                'created_at': row[12],
                'updated_at': row[13]
            } for row in rows]
    except Exception as e:
        raise DatabaseError(f"Failed to get bounties by developer: {str(e)}")

def update_bounty_status(bounty_id: int, status: str) -> bool:
    """Update bounty status"""
    try:
        now = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE bounties 
                SET status = ?, updated_at = ? 
                WHERE id = ?
            ''', (status, now, bounty_id))
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        raise DatabaseError(f"Failed to update bounty status: {str(e)}")

def cancel_bounty(bounty_id: int) -> bool:
    """Cancel a bounty and refund the funder"""
    try:
        now = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get bounty details
            cursor.execute('SELECT funder_id, amount, status FROM bounties WHERE id = ?', (bounty_id,))
            bounty = cursor.fetchone()
            
            if not bounty:
                raise DatabaseError("Bounty not found")
            
            if bounty[2] != "open":
                raise DatabaseError("Can only cancel open bounties")
            
            # Update bounty status to cancelled
            cursor.execute('''
                UPDATE bounties 
                SET status = ?, updated_at = ? 
                WHERE id = ?
            ''', ("cancelled", now, bounty_id))
            
            # Refund the funder
            cursor.execute('''
                UPDATE users 
                SET current_xrp_balance = current_xrp_balance + ?,
                    total_xrp_funded = total_xrp_funded - ?,
                    bounties_created = bounties_created - 1,
                    last_updated = ?
                WHERE id = ?
            ''', (bounty[1], bounty[1], now, bounty[0]))  # bounty[1] is amount, bounty[0] is funder_id
            
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        raise DatabaseError(f"Failed to cancel bounty: {str(e)}")

def accept_bounty(bounty_id: int, developer_address: str, escrow_id: str, escrow_sequence: int) -> bool:
    """Accept a bounty by setting developer address and escrow details (time-based escrow)"""
    try:
        now = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get the bounty to find the funder and amount
            cursor.execute('SELECT funder_id, amount FROM bounties WHERE id = ?', (bounty_id,))
            bounty = cursor.fetchone()
            
            if not bounty:
                raise DatabaseError("Bounty not found")
            
            funder_id = bounty[0]
            amount = bounty[1]
            
            cursor.execute('''
                UPDATE bounties 
                SET developer_address = ?, escrow_id = ?, escrow_sequence = ?, escrow_condition = NULL, escrow_fulfillment = NULL, status = ?, updated_at = ? 
                WHERE id = ?
            ''', (developer_address, escrow_id, escrow_sequence, "accepted", now, bounty_id))
            
            # Decrease funder's balance when escrow is created
            cursor.execute('''
                UPDATE users 
                SET current_xrp_balance = current_xrp_balance - ?,
                    last_updated = ?
                WHERE id = ?
            ''', (amount, now, funder_id))
            
            # Update developer's statistics (find user by XRP address)
            cursor.execute('''
                UPDATE users 
                SET bounties_accepted = bounties_accepted + 1,
                    last_updated = ?
                WHERE xrp_address = ?
            ''', (now, developer_address))
            
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        raise DatabaseError(f"Failed to accept bounty: {str(e)}")

def claim_bounty(bounty_id: int) -> bool:
    """Mark bounty as claimed"""
    try:
        now = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get the bounty to find the developer, funder, and amount
            cursor.execute('SELECT developer_address, funder_id, amount FROM bounties WHERE id = ?', (bounty_id,))
            bounty = cursor.fetchone()
            
            if not bounty:
                raise DatabaseError("Bounty not found")
            
            cursor.execute('''
                UPDATE bounties 
                SET status = ?, updated_at = ? 
                WHERE id = ?
            ''', ("claimed", now, bounty_id))
            
            # Update developer's statistics (find user by XRP address)
            if bounty[0]:  # developer_address
                cursor.execute('''
                    UPDATE users 
                    SET total_xrp_earned = total_xrp_earned + ?,
                        last_updated = ?
                    WHERE xrp_address = ?
                ''', (bounty[2], now, bounty[0]))  # bounty[2] is amount
            
            # Note: The escrow system handles the actual XRP transfer on the blockchain
            # The developer's balance will be updated when they sync their wallet
            
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        raise DatabaseError(f"Failed to claim bounty: {str(e)}")

def delete_bounty(bounty_id: int) -> bool:
    """Delete a bounty and refund the funder if it's still open"""
    try:
        now = datetime.now(timezone.utc).isoformat()
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get bounty details before deletion
            cursor.execute('SELECT funder_id, amount, status FROM bounties WHERE id = ?', (bounty_id,))
            bounty = cursor.fetchone()
            
            if not bounty:
                raise DatabaseError("Bounty not found")
            
            # If bounty is still open, refund the funder
            if bounty[2] == "open":  # status is "open"
                cursor.execute('''
                    UPDATE users 
                    SET current_xrp_balance = current_xrp_balance + ?,
                        total_xrp_funded = total_xrp_funded - ?,
                        bounties_created = bounties_created - 1,
                        last_updated = ?
                    WHERE id = ?
                ''', (bounty[1], bounty[1], now, bounty[0]))  # bounty[1] is amount, bounty[0] is funder_id
            
            cursor.execute('DELETE FROM bounties WHERE id = ?', (bounty_id,))
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        raise DatabaseError(f"Failed to delete bounty: {str(e)}")

# Search and Filter Functions
def search_bounties_by_github_url(github_issue_url: str) -> List[Dict[str, Any]]:
    """Search bounties by GitHub issue URL"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM bounties 
                WHERE github_issue_url LIKE ? 
                ORDER BY created_at DESC
            ''', (f'%{github_issue_url}%',))
            rows = cursor.fetchall()
            
            return [{
                'id': row[0],
                'funder_id': row[1],
                'bounty_name': row[2],
                'github_issue_url': row[3],
                'funder_address': row[4],
                'developer_address': row[5],
                'amount': row[6],
                'escrow_id': row[7],
                'escrow_sequence': row[8],
                'escrow_condition': row[9],
                'escrow_fulfillment': row[10],
                'status': row[11],
                'created_at': row[12],
                'updated_at': row[13]
            } for row in rows]
    except Exception as e:
        raise DatabaseError(f"Failed to search bounties: {str(e)}")

def search_bounties_by_name(bounty_name: str) -> List[Dict[str, Any]]:
    """Search bounties by bounty name"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM bounties 
                WHERE bounty_name LIKE ? 
                ORDER BY created_at DESC
            ''', (f'%{bounty_name}%',))
            rows = cursor.fetchall()
            
            return [{
                'id': row[0],
                'funder_id': row[1],
                'bounty_name': row[2],
                'github_issue_url': row[3],
                'funder_address': row[4],
                'developer_address': row[5],
                'amount': row[6],
                'escrow_id': row[7],
                'escrow_sequence': row[8],
                'escrow_condition': row[9],
                'escrow_fulfillment': row[10],
                'status': row[11],
                'created_at': row[12],
                'updated_at': row[13]
            } for row in rows]
    except Exception as e:
        raise DatabaseError(f"Failed to search bounties by name: {str(e)}")

def get_bounties_by_amount_range(min_amount: float, max_amount: float) -> List[Dict[str, Any]]:
    """Get bounties within an amount range"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM bounties 
                WHERE amount BETWEEN ? AND ? 
                ORDER BY amount DESC
            ''', (min_amount, max_amount))
            rows = cursor.fetchall()
            
            return [{
                'id': row[0],
                'funder_id': row[1],
                'bounty_name': row[2],
                'github_issue_url': row[3],
                'funder_address': row[4],
                'developer_address': row[5],
                'amount': row[6],
                'escrow_id': row[7],
                'escrow_sequence': row[8],
                'escrow_condition': row[9],
                'escrow_fulfillment': row[10],
                'status': row[11],
                'created_at': row[12],
                'updated_at': row[13]
            } for row in rows]
    except Exception as e:
        raise DatabaseError(f"Failed to get bounties by amount range: {str(e)}")

# Statistics Functions
def get_bounty_statistics() -> Dict[str, Any]:
    """Get overall bounty statistics"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Total bounties
            cursor.execute('SELECT COUNT(*) FROM bounties')
            total_bounties = cursor.fetchone()[0]
            
            # Bounties by status
            cursor.execute('''
                SELECT status, COUNT(*) 
                FROM bounties 
                GROUP BY status
            ''')
            status_counts = dict(cursor.fetchall())
            
            # Get counts for each status
            open_bounties = status_counts.get('open', 0)
            accepted_bounties = status_counts.get('accepted', 0)
            claimed_bounties = status_counts.get('claimed', 0)
            
            # Total amount across all bounties
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) 
                FROM bounties
            ''')
            total_amount = cursor.fetchone()[0]
            
            return {
                'total_bounties': total_bounties,
                'open_bounties': open_bounties,
                'accepted_bounties': accepted_bounties,
                'claimed_bounties': claimed_bounties,
                'total_amount': total_amount,
                'status_counts': status_counts  # Keep for backward compatibility
            }
    except Exception as e:
        raise DatabaseError(f"Failed to get bounty statistics: {str(e)}")

def get_user_statistics(user_id: int) -> Dict[str, Any]:
    """Get statistics for a specific user"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Bounties created by user
            cursor.execute('''
                SELECT COUNT(*) 
                FROM bounties 
                WHERE funder_id = ?
            ''', (user_id,))
            bounties_created = cursor.fetchone()[0]
            
            # Total amount funded by user
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) 
                FROM bounties 
                WHERE funder_id = ?
            ''', (user_id,))
            total_funded = cursor.fetchone()[0]
            
            # Bounties accepted by user
            user = get_user_by_id(user_id)
            if user and user['xrp_address']:
                cursor.execute('''
                    SELECT COUNT(*) 
                    FROM bounties 
                    WHERE developer_address = ?
                ''', (user['xrp_address'],))
                bounties_accepted = cursor.fetchone()[0]
                
                # Total amount earned by user
                cursor.execute('''
                    SELECT COALESCE(SUM(amount), 0) 
                    FROM bounties 
                    WHERE developer_address = ? AND status = 'claimed'
                ''', (user['xrp_address'],))
                total_earned = cursor.fetchone()[0]
            else:
                bounties_accepted = 0
                total_earned = 0
            
            return {
                'bounties_created': bounties_created,
                'total_funded': total_funded,
                'bounties_accepted': bounties_accepted,
                'total_earned': total_earned
            }
    except Exception as e:
        raise DatabaseError(f"Failed to get user statistics: {str(e)}")

def get_platform_statistics() -> Dict[str, Any]:
    """Get comprehensive platform statistics"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # User statistics
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
            
            # Bounty statistics
            cursor.execute('SELECT COUNT(*) FROM bounties')
            total_bounties = cursor.fetchone()[0]
            
            # Bounties by status
            cursor.execute('''
                SELECT status, COUNT(*) 
                FROM bounties 
                GROUP BY status
            ''')
            status_counts = dict(cursor.fetchall())
            
            # Amount statistics
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) 
                FROM bounties
            ''')
            total_amount = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) 
                FROM bounties 
                WHERE status = 'open'
            ''')
            open_amount = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) 
                FROM bounties 
                WHERE status = 'claimed'
            ''')
            claimed_amount = cursor.fetchone()[0]
            
            # User activity statistics
            cursor.execute('''
                SELECT 
                    COALESCE(SUM(bounties_created), 0) as total_created,
                    COALESCE(SUM(bounties_accepted), 0) as total_accepted,
                    COALESCE(SUM(total_xrp_funded), 0) as total_funded,
                    COALESCE(SUM(total_xrp_earned), 0) as total_earned
                FROM users
            ''')
            user_stats = cursor.fetchone()
            
            # Recent activity (last 7 days)
            cursor.execute('''
                SELECT COUNT(*) 
                FROM bounties 
                WHERE created_at >= datetime('now', '-7 days')
            ''')
            recent_bounties = cursor.fetchone()[0]
            
            return {
                'users': {
                    'total_users': total_users,
                    'total_bounties_created': user_stats[0],
                    'total_bounties_accepted': user_stats[1],
                    'total_xrp_funded': user_stats[2],
                    'total_xrp_earned': user_stats[3]
                },
                'bounties': {
                    'total_bounties': total_bounties,
                    'open_bounties': status_counts.get('open', 0),
                    'accepted_bounties': status_counts.get('accepted', 0),
                    'claimed_bounties': status_counts.get('claimed', 0),
                    'recent_bounties': recent_bounties
                },
                'amounts': {
                    'total_amount': total_amount,
                    'open_amount': open_amount,
                    'claimed_amount': claimed_amount
                },
                'status_counts': status_counts
            }
    except Exception as e:
        raise DatabaseError(f"Failed to get platform statistics: {str(e)}")

# Database Maintenance Functions
def cleanup_old_bounties(days_old: int = 30) -> int:
    """Clean up bounties older than specified days"""
    try:
        cutoff_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days_old)
        cutoff_iso = cutoff_date.isoformat()
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM bounties 
                WHERE created_at < ? AND status = 'open'
            ''', (cutoff_iso,))
            conn.commit()
            return cursor.rowcount
    except Exception as e:
        raise DatabaseError(f"Failed to cleanup old bounties: {str(e)}")

def backup_database(backup_path: str) -> bool:
    """Create a backup of the database"""
    try:
        import shutil
        shutil.copy2(DB_PATH, backup_path)
        return True
    except Exception as e:
        raise DatabaseError(f"Failed to backup database: {str(e)}")

def reset_database() -> bool:
    """Reset the database (drop all tables and recreate)"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DROP TABLE IF EXISTS bounties')
            cursor.execute('DROP TABLE IF EXISTS users')
            conn.commit()
        
        init_database()
        return True
    except Exception as e:
        raise DatabaseError(f"Failed to reset database: {str(e)}")

def recalculate_user_statistics() -> Dict[str, int]:
    """Recalculate and update all user statistics from bounty data"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now(timezone.utc).isoformat()
            
            # Reset all user statistics
            cursor.execute('''
                UPDATE users 
                SET bounties_created = 0,
                    bounties_accepted = 0,
                    total_xrp_funded = 0.0,
                    total_xrp_earned = 0.0,
                    last_updated = ?
            ''', (now,))
            
            # Recalculate bounties created and funded by each user
            cursor.execute('''
                UPDATE users 
                SET bounties_created = (
                    SELECT COUNT(*) 
                    FROM bounties 
                    WHERE bounties.funder_id = users.id
                ),
                total_xrp_funded = (
                    SELECT COALESCE(SUM(amount), 0) 
                    FROM bounties 
                    WHERE bounties.funder_id = users.id
                )
            ''')
            
            # Recalculate bounties accepted and earned by each user
            cursor.execute('''
                UPDATE users 
                SET bounties_accepted = (
                    SELECT COUNT(*) 
                    FROM bounties 
                    WHERE bounties.developer_address = users.xrp_address
                ),
                total_xrp_earned = (
                    SELECT COALESCE(SUM(amount), 0) 
                    FROM bounties 
                    WHERE bounties.developer_address = users.xrp_address 
                    AND bounties.status = 'claimed'
                )
            ''')
            
            conn.commit()
            
            # Get summary of updates
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT 
                    SUM(bounties_created) as total_created,
                    SUM(bounties_accepted) as total_accepted,
                    SUM(total_xrp_funded) as total_funded,
                    SUM(total_xrp_earned) as total_earned
                FROM users
            ''')
            summary = cursor.fetchone()
            
            return {
                'users_updated': total_users,
                'total_bounties_created': summary[0] or 0,
                'total_bounties_accepted': summary[1] or 0,
                'total_xrp_funded': summary[2] or 0,
                'total_xrp_earned': summary[3] or 0
            }
    except Exception as e:
        raise DatabaseError(f"Failed to recalculate user statistics: {str(e)}")

# Initialize database when module is imported
init_database()
