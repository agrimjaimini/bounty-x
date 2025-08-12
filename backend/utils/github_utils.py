import re
import requests
import secrets
import string
from typing import Optional


def generate_developer_secret_key() -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))


def extract_issue_number_from_url(github_issue_url: str) -> Optional[str]:
    pattern = r'github\.com/[^/]+/[^/]+/issues/(\d+)'
    match = re.search(pattern, github_issue_url)
    return match.group(1) if match else None


def verify_merge_request_contains_issue(
    merge_request_url: str,
    issue_number: str,
    developer_secret_key: Optional[str] = None,
) -> bool:
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
            rf'resolve #{issue_number}\b',
        ]

        if not any(
            re.search(p, title, re.IGNORECASE) or re.search(p, body, re.IGNORECASE)
            for p in issue_patterns
        ):
            return False

        is_merged = bool(pr_data.get('merged') or pr_data.get('merge_commit_sha'))
        if not is_merged:
            return False

        if developer_secret_key:
            return developer_secret_key in title or developer_secret_key in body

        return True
    except Exception:
        return False

