"""XRPL utility helpers for Bounty-X.

Includes testnet wallet management, escrow create/finish,
GitHub PR verification, and account info helpers.
"""

from xrpl.wallet import generate_faucet_wallet, Wallet
from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import EscrowCreate, EscrowFinish, Payment
from xrpl.models.requests import AccountInfo
from xrpl.utils import xrp_to_drops
from datetime import datetime
from xrpl.transaction import submit_and_wait
from xrpl.utils import datetime_to_ripple_time
from os import urandom
import re
import requests
from typing import Optional
import hashlib
import secrets
import string

def generate_developer_secret_key() -> str:
    """Create a short random key developers include in PRs for verification."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))

def create_testnet_account():
    """Create and fund a new XRPL testnet wallet via faucet."""
    client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
    wallet = generate_faucet_wallet(client, debug=True)
    return wallet



def add_seconds(numOfSeconds):
    """Return XRPL ripple-time timestamp after adding seconds to now."""
    from datetime import timedelta
    new_date = datetime.now() + timedelta(seconds=int(numOfSeconds))
    new_date = datetime_to_ripple_time(new_date)
    return new_date

def create_escrow(funder_seed: str, developer_address: str, amount: float, finish_after: int, max_retries: int = 3):
    """Create a time-based escrow from funder to developer, retrying transient errors."""
    client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
    wallet = Wallet.from_seed(funder_seed)
    
    try:
        account_info = get_account_info(wallet.classic_address)
        if not account_info:
            raise Exception("Could not retrieve account information")
    except Exception as e:
        pass
    
    cancel_date = add_seconds(finish_after)
    finish_date = add_seconds(finish_after)

    escrow_tx = EscrowCreate(
        account=wallet.classic_address,
        amount=str(xrp_to_drops(amount)),
        destination=developer_address,
        cancel_after=cancel_date,
        finish_after=finish_date
    )
    
    last_error = None
    for attempt in range(max_retries):
        try:
            response = submit_and_wait(escrow_tx, client, wallet)
            return response
        except Exception as e:
            last_error = e
            
            if any(error_code in str(e) for error_code in ["tecUNFUNDED_PAYMENT", "tecNO_PERMISSION", "tecPATH_DRY", "tecUNFUNDED"]):
                break
            
            if attempt < max_retries - 1:
                import time
                time.sleep(1)
    
    error_msg = str(last_error)
    if "tecUNFUNDED_PAYMENT" in error_msg:
        raise Exception("Insufficient funds to create escrow")
    elif "tecNO_PERMISSION" in error_msg:
        raise Exception("No permission to create escrow - account may not be properly funded")
    elif "tecPATH_DRY" in error_msg:
        raise Exception("No path found for payment")
    elif "tecUNFUNDED" in error_msg:
        raise Exception("Account is unfunded")
    else:
        raise Exception(f"Failed to create escrow after {max_retries} attempts: {error_msg}")

def get_escrow_transaction(escrow_id: str) -> Optional[dict]:
    """Fetch a transaction by hash and return XRPL response payload."""
    try:
        client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
        
        from xrpl.models.requests import Tx
        tx_request = Tx(transaction=escrow_id)
        response = client.request(tx_request)
        
        if response.is_successful():
            return response.result
        else:
            return None
            
    except Exception as e:
        return None

def finish_time_based_escrow(escrow_sequence: int, finisher_seed: str, owner_address: str):
    """Submit EscrowFinish to release a time-based escrow."""
    try:
        client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
        finisher_wallet = Wallet.from_seed(finisher_seed)
        
        escrow_finish_tx = EscrowFinish(
            account=finisher_wallet.classic_address,
            owner=owner_address,
            offer_sequence=escrow_sequence
        )
        
        response = submit_and_wait(escrow_finish_tx, client, finisher_wallet)
        return response
        
    except Exception as e:
        raise e

def extract_issue_number_from_url(github_issue_url: str) -> Optional[str]:
    """Return the GitHub issue number from a typical issue URL."""
    pattern = r'github\.com/[^/]+/[^/]+/issues/(\d+)'
    match = re.search(pattern, github_issue_url)
    return match.group(1) if match else None

def verify_merge_request_contains_issue(merge_request_url: str, issue_number: str, developer_secret_key: str = None) -> bool:
    """Check a PR title/body contains the issue reference and optional secret key."""
    try:
        api_url = merge_request_url.replace('github.com', 'api.github.com/repos')
        api_url = api_url.replace('/pull/', '/pulls/')
        
        response = requests.get(api_url)
        if response.status_code != 200:
            return False
        
        pr_data = response.json()
        
        title = pr_data.get('title', '')
        body = pr_data.get('body', '')
        
        issue_patterns = [
            rf'bounty-x{issue_number}\b',
            rf'#{issue_number}\b',
            rf'closes #{issue_number}\b',
            rf'fixes #{issue_number}\b',
            rf'resolves #{issue_number}\b',
            rf'close #{issue_number}\b',
            rf'fix #{issue_number}\b',
            rf'resolve #{issue_number}\b'
        ]
        
        issue_found = False
        for pattern in issue_patterns:
            if re.search(pattern, title, re.IGNORECASE) or re.search(pattern, body, re.IGNORECASE):
                issue_found = True
                break
        
        if not issue_found:
            return False
        
        if developer_secret_key:
            secret_key_found = developer_secret_key in title or developer_secret_key in body
            return secret_key_found
        
        return True
        
    except Exception as e:
        return False

def fund_wallet(address: str, amount: float):
    """Deprecated helper (kept for reference). Use fund_existing_wallet instead."""
    client = JsonRpcClient("https://s.altnet.rippletest.net:51234")
    acct_info = AccountInfo(
        account=address,
        ledger_index="validated",
        strict=True,
    )
    response = client.request(acct_info)

def get_account_info(address: str) -> Optional[dict]:
    """Return balance and account fields for a classic XRPL address."""
    try:
        client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
        
        account_info_request = AccountInfo(
            account=address,
            ledger_index="validated",
            strict=True
        )
        
        response = client.request(account_info_request)
        
        if response.is_successful():
            account_data = response.result["account_data"]
            
            balance_drops = int(account_data["Balance"])
            balance_xrp = balance_drops / 1_000_000
            
            account_info = {
                "address": address,
                "balance_drops": str(balance_drops),
                "balance_xrp": balance_xrp,
                "sequence": account_data.get("Sequence", 0),
                "flags": account_data.get("Flags", 0),
                "owner_count": account_data.get("OwnerCount", 0),
                "transfer_rate": account_data.get("TransferRate", 0),
                "domain": account_data.get("Domain", ""),
                "email_hash": account_data.get("EmailHash", ""),
                "message_key": account_data.get("MessageKey", ""),
                "regular_key": account_data.get("RegularKey", ""),
                "tick_size": account_data.get("TickSize", 0),
                "ledger_current_index": response.result.get("ledger_current_index", 0),
                "validated": response.result.get("validated", False)
            }
            
            return account_info
        else:
            return None
            
    except Exception as e:
        return None

def fund_existing_wallet(seed: str):
    """Fund an existing testnet wallet via faucet and return new balance."""
    try:
        client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
        existing = Wallet.from_seed(seed)
        funded = generate_faucet_wallet(client, existing)
        
        if isinstance(funded, dict):
            address = funded.get('address', existing.classic_address)
        else:
            address = funded.classic_address
        
        from xrpl.models.requests import AccountInfo
        balance_request = AccountInfo(
            account=address,
            ledger_index="validated",
            strict=True
        )
        balance_response = client.request(balance_request)
        
        if not balance_response.is_successful():
            raise Exception(f"Failed to get account info: {balance_response.result}")
        
        balance = balance_response.result["account_data"]["Balance"]
        
        return {
            "address": address,
            "balance_drops": balance,
            "balance_xrp": int(balance) / 1_000_000
        }
    except Exception as e:
        raise e

def validate_account_for_escrow(seed: str, amount: float) -> bool:
    """Basic preflight to ensure seed account has enough XRP for escrow and reserve."""
    try:
        client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
        wallet = Wallet.from_seed(seed)
        
        account_info = get_account_info(wallet.classic_address)
        if not account_info:
            return False
        
        balance_xrp = account_info['balance_xrp']
        
        required_amount = amount + 0.01
        if balance_xrp < required_amount:
            return False
        
        if balance_xrp < 20:
            return False
        
        return True
        
    except Exception as e:
        return False
