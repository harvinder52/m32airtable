from tenacity import retry, stop_after_attempt, wait_exponential
import httpx
import logging

logger = logging.getLogger(__name__)

def create_retry_decorator(max_attempts=3):
    """Create a retry decorator with exponential backoff"""
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry_error_callback=lambda retry_state: logger.error(
            f"Failed after {retry_state.attempt_number} attempts: {retry_state.outcome.exception()}"
        )
    )

def handle_rate_limit(response: httpx.Response):
    """Handle rate limiting"""
    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After", "5")
        logger.warning(f"Rate limited. Retry after: {retry_after}s")
        return True
    return False