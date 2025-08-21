import os
from typing import Dict, Any


def start_esign(document_url: str, fields: Dict[str, Any]) -> Dict[str, str]:
    """Start an e-sign session with a configured provider.

    This is a provider-agnostic stub that returns a mock signing URL.
    Replace with a real integration (e.g., DocuSign, Aadhaar eSign) as needed.
    """
    provider = os.getenv("ESIGN_PROVIDER", "mock").lower()

    # In production, branch by provider and call the respective API to create
    # an envelope/session, then return the recipient's signing URL.
    if provider == "mock":
        # Return a placeholder URL; frontends can open this in a new tab.
        return {
            "signing_url": "https://example.com/mock-esign?token=demo",
            "provider": provider,
        }

    # Unknown provider: return a safe fallback
    return {
        "signing_url": "",
        "provider": provider,
        "error": "Unsupported e-sign provider"
    }

