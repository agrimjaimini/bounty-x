export interface Bounty {
  id: number;
  funder_id: number;
  bounty_name: string;
  github_issue_url: string;
  funder_address: string;
  developer_address: string | null;
  amount: number;
  escrow_id: string | null;
  escrow_sequence: number | null;
  escrow_condition: string | null;
  escrow_fulfillment: string | null;
  status: 'open' | 'accepted' | 'claimed' | 'cancelled';
  created_at: string;
  updated_at: string;
}

export interface User {
  id: number;
  username: string;
  xrp_address: string;
  bounties_created: number;
  bounties_accepted: number;
  total_xrp_funded: number;
  total_xrp_earned: number;
  current_xrp_balance: number;
  last_updated: string;
}

export interface UserRegister {
  username: string;
  password: string;
}

export interface UserLogin {
  username: string;
  password: string;
}

export interface BountyCreate {
  funder_id: number;
  bounty_name: string;
  github_issue_url: string;
  amount: number;
  finish_after: number;
}

export interface BountyAccept {
  developer_address: string;
  finish_after: number;
}

export interface BountyClaim {
  merge_request_url: string;
}

export interface BountyStatistics {
  total_bounties: number;
  open_bounties: number;
  accepted_bounties: number;
  claimed_bounties: number;
  total_amount: number;
}

export interface PlatformStatistics {
  users: {
    total_users: number;
    total_bounties_created: number;
    total_bounties_accepted: number;
    total_xrp_funded: number;
    total_xrp_earned: number;
  };
  bounties: {
    total_bounties: number;
    open_bounties: number;
    accepted_bounties: number;
    claimed_bounties: number;
    recent_bounties: number;
  };
  amounts: {
    total_amount: number;
    open_amount: number;
    claimed_amount: number;
  };
  status_counts: Record<string, number>;
}

export interface UserStatistics {
  total_bounties_created: number;
  total_bounties_accepted: number;
  total_amount_funded: number;
  total_amount_earned: number;
}

export interface ApiResponse<T> {
  message?: string;
  data?: T;
  error?: string;
} 