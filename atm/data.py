"""
atm.data
--------
Pre-loaded demo accounts for the ATM simulation.

NOTE: Account numbers, PINs, card numbers, and balances are entirely
      fictional and exist for DEMONSTRATION / EDUCATIONAL purposes only.
      In a real system, account data is fetched from a secure bank database
      and PINs are never stored in plain text.
"""

from atm.enums import AccountType
from atm.models import Account

DEMO_ACCOUNTS: list[Account] = [
    Account(
        account_number="31290012345678",
        account_holder="RAJESH KUMAR SHARMA",
        account_type=AccountType.SAVINGS,
        ifsc_code="SBIN0001234",
        branch="New Delhi Main Branch",
        mobile="9876543210",
        balance=85_500.00,
        pin="1234",
        card_number="4532 1234 5678 9010",
        card_expiry="12/27",
    ),
    Account(
        account_number="31290087654321",
        account_holder="PRIYA MEHTA",
        account_type=AccountType.CURRENT,
        ifsc_code="SBIN0001234",
        branch="New Delhi Main Branch",
        mobile="9123456780",
        balance=2_50_000.00,
        pin="5678",
        card_number="4532 9876 5432 1090",
        card_expiry="08/26",
    ),
]
