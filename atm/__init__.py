"""
atm
---
Indian Bank ATM Simulation — Python package.

Public API
----------
::

    from atm import BankATM, DEMO_ACCOUNTS

    BankATM(accounts=DEMO_ACCOUNTS).run()
"""

from atm.bank import BankATM
from atm.data import DEMO_ACCOUNTS

__all__ = ["BankATM", "DEMO_ACCOUNTS"]
