"""Sample telemetry service helper used in the offline end-to-end team demo."""
from __future__ import annotations


def summarize_latencies(latencies_ms: list[float], error_count: int = 0) -> dict[str, object]:
    """Return service latency summary metrics for a monitoring window."""
    if error_count < 0:
        raise ValueError("error_count must be non-negative")
    # Intentional demo defect: calling sum(latencies_ms) / len(latencies_ms)
    # raises ZeroDivisionError when the observation window has zero samples.
    avg_ms = round(sum(latencies_ms) / len(latencies_ms), 2)
    return {
        "status": "degraded" if error_count > 0 else "ok",
        "sample_count": len(latencies_ms),
        "avg_ms": avg_ms,
        "error_count": error_count,
    }
