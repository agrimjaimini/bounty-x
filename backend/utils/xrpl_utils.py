from typing import Optional, Tuple
from xrpl.wallet import generate_faucet_wallet, Wallet
from xrpl.clients import JsonRpcClient
from xrpl.models.transactions import EscrowCreate, EscrowFinish
from xrpl.models.requests import AccountInfo
from xrpl.utils import xrp_to_drops, datetime_to_ripple_time
from xrpl.transaction import submit_and_wait
from datetime import datetime

from cryptoconditions import PreimageSha256
import secrets


def create_testnet_account():
    client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
    wallet = generate_faucet_wallet(client, debug=True)
    return wallet


def add_seconds(numOfSeconds):
    from datetime import timedelta
    new_date = datetime.now() + timedelta(seconds=int(numOfSeconds))
    new_date = datetime_to_ripple_time(new_date)
    return new_date



def generate_condition_and_fulfillment() -> Tuple[str, str, str]:
    preimage = secrets.token_bytes(32)
    fulfillment = PreimageSha256(preimage)
    condition_hex = fulfillment.condition_binary.hex()
    fulfillment_hex = fulfillment.serialize_binary().hex()
    preimage_hex = preimage.hex()
    return condition_hex, fulfillment_hex, preimage_hex


def create_conditional_escrow(
    funder_seed: str,
    developer_address: str,
    amount: float,
    cancel_after_seconds: int,
    condition_hex: str,
):
    client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
    wallet = Wallet.from_seed(funder_seed)
    cancel_after = add_seconds(cancel_after_seconds)

    escrow_tx = EscrowCreate(
        account=wallet.classic_address,
        amount=str(xrp_to_drops(amount)),
        destination=developer_address,
        cancel_after=cancel_after,
        condition=condition_hex,
    )

    response = submit_and_wait(escrow_tx, client, wallet)
    return response


def get_escrow_transaction(escrow_id: str) -> Optional[dict]:
    try:
        client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
        from xrpl.models.requests import Tx

        tx_request = Tx(transaction=escrow_id)
        response = client.request(tx_request)
        return response.result if response.is_successful() else None
    except Exception:
        return None



def finish_conditional_escrow(
    owner_address: str,
    offer_sequence: int,
    finisher_seed: str,
    fulfillment_hex: str,
    condition_hex: str,
):
    try:
        client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
        finisher_wallet = Wallet.from_seed(finisher_seed)
        finish_tx = EscrowFinish(
            account=finisher_wallet.classic_address,
            owner=owner_address,
            offer_sequence=offer_sequence,
            fulfillment=fulfillment_hex,
            condition=condition_hex,
        )
        response = submit_and_wait(finish_tx, client, finisher_wallet)
        return response
    except Exception as e:
        raise e


def get_account_info(address: str) -> Optional[dict]:
    try:
        client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
        account_info_request = AccountInfo(
            account=address,
            ledger_index="validated",
            strict=True,
        )
        response = client.request(account_info_request)
        if not response.is_successful():
            return None
        account_data = response.result["account_data"]
        balance_drops = int(account_data["Balance"])
        balance_xrp = balance_drops / 1_000_000
        return {
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
            "validated": response.result.get("validated", False),
        }
    except Exception:
        return None


def fund_existing_wallet(seed: str):
    try:
        client = JsonRpcClient("https://s.altnet.rippletest.net:51234/")
        existing = Wallet.from_seed(seed)
        funded = generate_faucet_wallet(client, existing)
        address = funded.get('address', existing.classic_address) if isinstance(funded, dict) else funded.classic_address
        balance_request = AccountInfo(
            account=address,
            ledger_index="validated",
            strict=True,
        )
        balance_response = client.request(balance_request)
        if not balance_response.is_successful():
            raise Exception(f"Failed to get account info: {balance_response.result}")
        balance = balance_response.result["account_data"]["Balance"]
        return {"address": address, "balance_drops": balance, "balance_xrp": int(balance) / 1_000_000}
    except Exception as e:
        raise e


def validate_account_for_escrow(seed: str, amount: float) -> bool:
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
    except Exception:
        return False

