"""Oncology knowledge base search stub."""

from shared.models import BusinessError


async def oncokb_search(question: str, cancer: str) -> list[dict]:
    """Return guideline snippets for a query."""
    # Placeholder implementation
    if "nothing" in question:
        snippets: list[dict] = []
    else:
        snippets = [
            {
                "snippet": f"Guideline for {cancer}",
                "source": "OncoKB",
                "url": "http://example.com",
            }
        ]
    if not snippets:
        raise BusinessError(404, "No KB hit")
    return snippets
