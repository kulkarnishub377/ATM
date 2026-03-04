"""
atm.utils
---------
ATM-wide constants and pure utility functions.
No internal package dependencies (safe to import anywhere).

NOTE: All constants and demo data are for educational / simulation purposes only.
"""

import random
import string

# ------------------------------------------------------------------
# ATM-wide constants
# ------------------------------------------------------------------

DAILY_WITHDRAWAL_LIMIT: float = 50_000.0   # ₹ per card per calendar day
MAX_PIN_ATTEMPTS:       int   = 3
FRAUD_ALERT_THRESHOLD:  float = 25_000.0   # amounts ≥ this trigger a confirmation


# ------------------------------------------------------------------
# OTP simulation
# ------------------------------------------------------------------

def sim_otp() -> str:
    """Simulate dispatching an OTP; returns the 6-digit code (demo only)."""
    return "".join(random.choices(string.digits, k=6))


# ------------------------------------------------------------------
# Denomination helpers
# ------------------------------------------------------------------

def denomination_breakdown(amount: int) -> dict[int, int]:
    """
    Return the minimum number of notes needed for the given ₹ amount
    using standard RBI denominations (₹2000, ₹500, ₹200, ₹100, ₹50, ₹20, ₹10).
    """
    denominations = [2000, 500, 200, 100, 50, 20, 10]
    notes: dict[int, int] = {}
    remaining = amount
    for denom in denominations:
        if remaining >= denom:
            count = remaining // denom
            notes[denom] = count
            remaining -= count * denom
    return notes
