from app.services.rate_limiter import RateLimiter


def test_rate_limiter_allows_ten_requests():
    limiter = RateLimiter(
        max_requests=10,
        window_seconds=60
    )

    for _ in range(10):
        limiter.wait_if_needed()

    assert len(limiter.request_times) == 10