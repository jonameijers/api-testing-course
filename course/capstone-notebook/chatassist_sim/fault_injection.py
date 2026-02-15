"""Context managers for fault injection and configuration overrides."""

from contextlib import contextmanager
import copy


@contextmanager
def inject_fault(simulator, fault_type, **kwargs):
    """Temporarily inject a fault into *simulator*.  Auto-resets on exit.

    Supported *fault_type* values:

    * ``"rate_limit"``     -- force a 429 response
    * ``"server_error"``   -- force a 500 response
    * ``"overloaded"``     -- force a 503 response
    * ``"timeout"``        -- sleep for *delay* seconds (default 15)
    * ``"malformed_json"`` -- truncate response body
    * ``"safety_block"``   -- force a safety-blocked response
    """
    original = copy.copy(simulator._fault_config)

    if fault_type == "rate_limit":
        simulator._fault_config["force_rate_limit"] = True
    elif fault_type == "server_error":
        simulator._fault_config["force_500"] = True
    elif fault_type == "overloaded":
        simulator._fault_config["force_503"] = True
    elif fault_type == "timeout":
        simulator._fault_config["response_delay_s"] = kwargs.get("delay", 15)
    elif fault_type == "malformed_json":
        simulator._fault_config["truncate_response"] = True
    elif fault_type == "safety_block":
        simulator._fault_config["force_safety_block"] = True
    else:
        raise ValueError(f"Unknown fault type: {fault_type!r}")

    try:
        yield simulator
    finally:
        simulator._fault_config = original


@contextmanager
def configure(simulator, **kwargs):
    """Temporarily change *simulator* config.  Auto-resets on exit.

    Any keyword argument is merged into ``simulator._sim_config`` for the
    duration of the ``with`` block.
    """
    original = copy.copy(simulator._sim_config)
    simulator._sim_config.update(kwargs)
    try:
        yield simulator
    finally:
        simulator._sim_config = original
