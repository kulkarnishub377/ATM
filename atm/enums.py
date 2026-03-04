"""
atm.enums
---------
Enumerations shared across the ATM package.
"""

from enum import Enum


class AccountType(Enum):
    SAVINGS = "Savings"
    CURRENT = "Current"


class TransactionType(Enum):
    CREDIT = "CR"
    DEBIT  = "DR"


class Language(Enum):
    ENGLISH = "English"
    HINDI   = "Hindi (हिंदी)"
