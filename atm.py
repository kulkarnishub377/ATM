"""
Backward-compatible entry point for the Indian Bank ATM simulation.

The ATM system now lives in the ``atm/`` package.  This file is kept
so that ``python atm.py`` continues to work alongside the preferred
``python main.py`` command.

NOTE: DEMO_ACCOUNTS contains demo PINs for educational / simulation
      purposes only.  Never store PINs in plain text in production code.
"""

from atm import BankATM, DEMO_ACCOUNTS  # noqa: E402

if __name__ == "__main__":
    BankATM(accounts=DEMO_ACCOUNTS).run()
