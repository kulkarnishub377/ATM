"""
Primary entry point for the Indian Bank ATM simulation.

Run
---
::

    python main.py

Demo accounts
-------------
+--------------------+--------+------------+----------+
| Card (last 4)      | Type   | Balance    | PIN      |
+====================+========+============+==========+
| 9010               | Saving | ₹85,500    | 1234     |
+--------------------+--------+------------+----------+
| 1090               | Curr.  | ₹2,50,000  | 5678     |
+--------------------+--------+------------+----------+

NOTE: PINs shown above are for DEMONSTRATION purposes only.
      Never store or hardcode PINs in real banking software.
"""

from atm import BankATM, DEMO_ACCOUNTS

if __name__ == "__main__":
    BankATM(accounts=DEMO_ACCOUNTS).run()
