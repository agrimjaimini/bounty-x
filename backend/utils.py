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

def create_testnet_account():
    client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
    wallet = generate_faucet_wallet(client, debug=True)

    return wallet

def generate_condition():
    """Generate a simple preimage condition using xrpl-py's built-in functionality"""
    # Generate a random 32-byte preimage
    preimage = urandom(32)
    
    # Create SHA256 hash of the preimage (this is the condition)
    condition = hashlib.sha256(preimage).hexdigest().upper()
    
    # The fulfillment is the original preimage
    fulfillment = preimage.hex().upper()
    
    return condition, fulfillment

def add_seconds(numOfSeconds):
    new_date = datetime.now()
    new_date = datetime_to_ripple_time(new_date)
    new_date = new_date + int(numOfSeconds)
    return new_date

def create_escrow(funder_seed: str, developer_address: str, amount: float, finish_after: int):
    """Create a time-based escrow that's immediately finishable but auto-cancels after time"""
    client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
    wallet = Wallet.from_seed(funder_seed)
    
    # Calculate dates
    cancel_date = add_seconds(finish_after)  # Cancel after the specified time
    finish_date = add_seconds(1)  # Finish after 1 second (effectively immediate)

    escrow_tx = EscrowCreate(
        account=wallet.classic_address,
        amount=str(xrp_to_drops(amount)),
        destination=developer_address,
        cancel_after=cancel_date,
        finish_after=finish_date
        # finish_after set to 1 second for immediate finishability
        # No condition parameter - using time-based escrow
    )
    
    try:
        response = submit_and_wait(escrow_tx, client, wallet)
        # For time-based escrows, we don't need condition/fulfillment
        # The response object is immutable, so we'll handle this in the calling code
        return response
    except Exception as e:
        print(f"Error creating time-based escrow: {e}")
        raise e

def get_escrow_transaction(escrow_id: str) -> Optional[dict]:
    """Retrieve escrow transaction details from XRPL"""
    try:
        client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
        
        # Get transaction details
        from xrpl.models.requests import Tx
        tx_request = Tx(transaction=escrow_id)
        response = client.request(tx_request)
        
        if response.is_successful():
            return response.result
        else:
            print(f"Failed to get escrow transaction: {response.result}")
            return None
            
    except Exception as e:
        print(f"Error retrieving escrow transaction: {e}")
        return None

def finish_time_based_escrow(escrow_id: str, escrow_sequence: int, finisher_seed: str, owner_address: str):
    """Finish a time-based escrow transaction"""
    try:
        client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
        finisher_wallet = Wallet.from_seed(finisher_seed)
        
        # Create time-based escrow finish transaction (no condition/fulfillment needed)
        escrow_finish_tx = EscrowFinish(
            account=finisher_wallet.classic_address,
            owner=owner_address,
            offer_sequence=escrow_sequence
            # No condition or fulfillment for time-based escrows
        )
        
        # Submit the transaction
        response = submit_and_wait(escrow_finish_tx, client, finisher_wallet)
        return response
        
    except Exception as e:
        print(f"Error finishing time-based escrow: {e}")
        raise e

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
            rf'bounty-x{issue_number}\b',
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

def fund_wallet(address: str, amount: float):
    client = JsonRpcClient("https://s.altnet.rippletest.net:51234")
    acct_info = AccountInfo(
        account=address,
        ledger_index="validated",
        strict=True,
    )
    response = client.request(acct_info)
    print("Balance:", response.result["account_data"]["Balance"], "drops")

def get_account_info(address: str) -> Optional[dict]:
    try:
        client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
        
        # Create account info request
        account_info_request = AccountInfo(
            account=address,
            ledger_index="validated",
            strict=True
        )
        
        # Make the request
        response = client.request(account_info_request)
        
        if response.is_successful():
            account_data = response.result["account_data"]
            
            # Convert balance from drops to XRP for readability
            balance_drops = int(account_data["Balance"])
            balance_xrp = balance_drops / 1_000_000  # 1 XRP = 1,000,000 drops
            
            # Format the response
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
            print(f"Failed to get account info: {response.result}")
            return None
            
    except Exception as e:
        print(f"Error retrieving account info: {e}")
        return None

