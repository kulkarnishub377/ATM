"""
atm.models
----------
Core domain dataclasses: Transaction and Account.

NOTE: PINs are stored as plain strings here for demo / educational purposes only.
      In production, PINs are never stored in plain text.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime

from atm.enums import AccountType, TransactionType


@dataclass
class Transaction:
    """A single debit or credit ledger entry on an account."""

    ref_no:        str
    timestamp:     datetime
    txn_type:      TransactionType
    amount:        float
    balance_after: float
    description:   str

    def display_line(self) -> str:
        """Return a single formatted line for statement display."""
        ts   = self.timestamp.strftime("%d-%b-%Y %H:%M")
        sign = "+" if self.txn_type == TransactionType.CREDIT else "-"
        return (
            f"  {ts}  {self.txn_type.value}  "
            f"{sign}₹{self.amount:>10,.2f}  "
            f"Bal: ₹{self.balance_after:>12,.2f}  "
            f"{self.description[:30]}"
        )


@dataclass
class Account:
    """A bank account with card details, PIN, and transaction history."""

    account_number:  str
    account_holder:  str
    account_type:    AccountType
    ifsc_code:       str
    branch:          str
    mobile:          str
    balance:         float
    pin:             str
    card_number:     str            # 16-digit card number (space-separated groups)
    card_expiry:     str            # MM/YY
    is_blocked:      bool           = False
    daily_withdrawn: float          = 0.0
    last_txn_date:   date           = field(default_factory=date.today)
    transactions:    list[Transaction] = field(default_factory=list)
    cheque_requests: int            = 0

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def masked_card(self) -> str:
        """e.g. 'XXXX XXXX XXXX 9010'"""
        c = self.card_number.replace(" ", "")
        return f"XXXX XXXX XXXX {c[-4:]}"

    def masked_mobile(self) -> str:
        """e.g. '+91 XXXXX X3210'"""
        m = self.mobile
        return f"+91 XXXXX X{m[-4:]}" if len(m) >= 4 else "+91 XXXXXXXXXX"

    def masked_account(self) -> str:
        """e.g. 'XXXXXX5678'"""
        return f"XXXXXX{self.account_number[-4:]}"

    def available_balance(self) -> float:
        """Available balance (demo: same as ledger balance)."""
        return self.balance

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------

    def reset_daily_limit_if_new_day(self) -> None:
        """Reset the daily-withdrawal counter when the calendar date rolls over."""
        today = date.today()
        if self.last_txn_date != today:
            self.daily_withdrawn = 0.0
            self.last_txn_date = today

    def record_transaction(
        self,
        txn_type:    TransactionType,
        amount:      float,
        description: str,
    ) -> Transaction:
        """
        Apply a debit/credit to the account balance, append a Transaction
        entry to the history, and return the new Transaction.
        """
        ref = "REF" + uuid.uuid4().hex[:10].upper()
        txn = Transaction(
            ref_no=ref,
            timestamp=datetime.now(),
            txn_type=txn_type,
            amount=amount,
            balance_after=self.balance,
            description=description,
        )
        self.transactions.append(txn)
        return txn
