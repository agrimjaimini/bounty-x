#!/usr/bin/env python3
"""
Test script for the bounty API
This demonstrates the new functionality:
1. Creating a bounty with automatic escrow creation
2. Claiming a bounty with a merge request
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

def test_create_bounty():
    """Test creating a bounty with automatic escrow creation"""
    print("=== Testing Bounty Creation ===")
    
    bounty_data = {
        "github_issue_url": "https://github.com/example/repo/issues/123",
        "funder_address": "rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe",  # Example XRPL address
        "funder_secret": "sEdTM1uX8pu2do5XvTnutH6HsouMaM2",  # Example secret (for demo only)
        "amount": 100.0,  # 100 XRP
        "finish_after": 86400  # 24 hours
    }
    
    try:
        response = requests.post(f"{BASE_URL}/bounties/", json=bounty_data)
        if response.status_code == 200:
            bounty = response.json()
            print(f"✅ Bounty created successfully!")
            print(f"   Bounty ID: {bounty['id']}")
            print(f"   Status: {bounty['status']}")
            print(f"   Escrow ID: {bounty['escrow_id']}")
            return bounty['id']
        else:
            print(f"❌ Failed to create bounty: {response.status_code}")
            print(f"   Error: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating bounty: {e}")
        return None

def test_claim_bounty(bounty_id):
    """Test claiming a bounty with a merge request"""
    print(f"\n=== Testing Bounty Claiming (Bounty ID: {bounty_id}) ===")
    
    claim_data = {
        "developer_address": "rPT1Sjq2YGrBMTttX4GZHjKu9dyfzbpAYe",  # Example developer address
        "merge_request_url": "https://github.com/example/repo/pull/456"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/bounties/{bounty_id}/claim", json=claim_data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Bounty claimed successfully!")
            print(f"   Developer: {result['developer_address']}")
            print(f"   Merge Request: {result['merge_request_url']}")
        else:
            print(f"❌ Failed to claim bounty: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error claiming bounty: {e}")

def test_list_bounties():
    """Test listing all bounties"""
    print(f"\n=== Testing Bounty Listing ===")
    
    try:
        response = requests.get(f"{BASE_URL}/bounties/")
        if response.status_code == 200:
            bounties = response.json()
            print(f"✅ Found {len(bounties)} bounties:")
            for bounty in bounties:
                print(f"   - ID: {bounty['id']}, Status: {bounty['status']}, Amount: {bounty['amount']} XRP")
        else:
            print(f"❌ Failed to list bounties: {response.status_code}")
    except Exception as e:
        print(f"❌ Error listing bounties: {e}")

def main():
    print("🚀 Starting Bounty API Tests\n")
    
    # Test bounty creation
    bounty_id = test_create_bounty()
    
    if bounty_id:
        # Test bounty claiming
        test_claim_bounty(bounty_id)
    
    # Test listing bounties
    test_list_bounties()
    
    print(f"\n✨ Tests completed!")

if __name__ == "__main__":
    main() 