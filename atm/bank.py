"""
atm.bank
--------
BankATM — the core ATM engine.

Orchestrates the full session lifecycle:
  card selection → language → PIN auth → main menu → eject card

All transaction logic, fraud detection, OTP simulation, and receipt
printing live here.  UI primitives come from atm.ui, bilingual strings
from atm.strings, and utility functions from atm.utils.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from atm.enums import Language, TransactionType
from atm.models import Account
from atm.strings import T
from atm.ui import (
    blank_line,
    box_bot,
    box_line,
    box_mid,
    box_top,
    get_amount,
    get_int,
    get_pin_input,
)
from atm.utils import (
    DAILY_WITHDRAWAL_LIMIT,
    FRAUD_ALERT_THRESHOLD,
    MAX_PIN_ATTEMPTS,
    denomination_breakdown,
    sim_otp,
)


class BankATM:
    """
    Indian bank ATM engine.

    Parameters
    ----------
    accounts : list[Account]
        The accounts available for use at this ATM terminal.

    Usage
    -----
    ::

        from atm import BankATM, DEMO_ACCOUNTS
        BankATM(accounts=DEMO_ACCOUNTS).run()
    """

    BANK_NAME    = "STATE BANK OF INDIA"
    BANK_TAGLINE = "The Nation's Bank"
    ATM_ID       = "ATM/DEL/001/SBI"
    TOLL_FREE    = "1800 425 3800"

    def __init__(self, accounts: list[Account]) -> None:
        self._accounts: dict[str, Account] = {a.account_number: a for a in accounts}
        self._lang: Language = Language.ENGLISH
        self._session_account: Optional[Account] = None

    # ==================================================================
    # Top-level lifecycle
    # ==================================================================

    def run(self) -> None:
        """Entry point — loops across multiple independent sessions."""
        self._print_bank_header()
        while True:
            self._lang = Language.ENGLISH
            self._session_account = None
            if not self._card_selection():
                break
            if not self._authenticate():
                self._eject_card()
                continue
            self._main_menu()
            self._eject_card()

    # ==================================================================
    # Session setup
    # ==================================================================

    def _print_bank_header(self) -> None:
        box_top()
        blank_line()
        box_line(self.BANK_NAME,    "center")
        box_line(self.BANK_TAGLINE, "center")
        blank_line()
        box_line(f"ATM ID    : {self.ATM_ID}",    "center")
        box_line(f"Toll Free : {self.TOLL_FREE}",  "center")
        blank_line()
        box_bot()
        print()

    def _card_selection(self) -> bool:
        """Simulate card insertion by letting the user pick a demo account."""
        acc_list = list(self._accounts.values())
        box_top()
        box_line("SELECT DEMO CARD / ACCOUNT", "center")
        box_mid()
        for i, acc in enumerate(acc_list, start=1):
            box_line(f"  {i}. {acc.masked_card()}  ({acc.account_type.value})", "left")
        box_line(f"  {len(acc_list) + 1}. Exit / Switch Off ATM", "left")
        box_bot()
        choice = get_int("Select card slot: ", lo=1, hi=len(acc_list) + 1)
        if choice == len(acc_list) + 1:
            box_top()
            box_line("ATM is now offline. Thank you!", "center")
            box_bot()
            return False
        self._session_account = acc_list[choice - 1]
        return True

    def _select_language(self) -> None:
        box_top()
        box_line("SELECT LANGUAGE / भाषा चुनें", "center")
        box_mid()
        box_line("  1. English",           "left")
        box_line("  2. Hindi (हिंदी)",     "left")
        box_bot()
        choice = get_int("Choice: ", lo=1, hi=2)
        self._lang = Language.ENGLISH if choice == 1 else Language.HINDI
        print()

    def _authenticate(self) -> bool:
        """PIN authentication — MAX_PIN_ATTEMPTS attempts, then block the card."""
        acc = self._session_account
        assert acc is not None

        if acc.is_blocked:
            box_top()
            box_line(T("card_blocked", self._lang), "center")
            box_bot()
            return False

        self._select_language()

        box_top()
        box_line(T("welcome", self._lang), "center")
        box_mid()
        box_line(f"Card : {acc.masked_card()}", "left")
        box_bot()
        print()

        for attempt in range(1, MAX_PIN_ATTEMPTS + 1):
            entered = get_pin_input(f"  {T('enter_pin', self._lang)}")
            if entered == acc.pin:
                print(f"\n  ✔  {T('auth_success', self._lang)}\n")
                return True
            remaining = MAX_PIN_ATTEMPTS - attempt
            if remaining > 0:
                print(
                    f"  ✘  {T('incorrect_pin', self._lang)} "
                    f"{remaining} attempt(s) remaining.\n"
                )
            else:
                acc.is_blocked = True
                print(f"\n  ✘  {T('card_blocked', self._lang)}\n")
        return False

    def _eject_card(self) -> None:
        print()
        box_top()
        box_line("Please collect your card.", "center")
        box_line(T("thank_you", self._lang), "center")
        box_bot()
        print()

    # ==================================================================
    # Main menu
    # ==================================================================

    def _main_menu(self) -> None:
        acc = self._session_account
        assert acc is not None

        while True:
            box_top()
            box_line(f"  Welcome,  {acc.account_holder}", "left")
            box_line(
                f"  A/c : {acc.masked_account()}  |  {acc.account_type.value}", "left"
            )
            box_mid()
            box_line("   1.  Balance Enquiry           (बैलेंस जानकारी)",  "left")
            box_line("   2.  Cash Withdrawal           (नकद निकासी)",       "left")
            box_line("   3.  Cash Deposit              (नकद जमा)",           "left")
            box_line("   4.  Fund Transfer             (फंड ट्रांसफर)",      "left")
            box_line("   5.  Bill Payment              (बिल भुगतान)",        "left")
            box_line("   6.  Mini Statement            (मिनी स्टेटमेंट)",    "left")
            box_line("   7.  Full Statement            (पूर्ण विवरण)",       "left")
            box_line("   8.  PIN Change                (PIN बदलें)",         "left")
            box_line("   9.  Mobile Number Update      (मोबाइल अपडेट)",     "left")
            box_line("  10.  Cheque Book Request       (चेक बुक अनुरोध)",  "left")
            box_line("  11.  Account Details           (खाता विवरण)",      "left")
            box_line("  12.  Exit / Eject Card         (बाहर निकलें)",      "left")
            box_bot()
            choice = get_int("  Select option: ", lo=1, hi=12)
            print()

            if   choice == 1:  self._balance_enquiry()
            elif choice == 2:  self._cash_withdrawal()
            elif choice == 3:  self._cash_deposit()
            elif choice == 4:  self._fund_transfer()
            elif choice == 5:  self._bill_payment()
            elif choice == 6:  self._mini_statement()
            elif choice == 7:  self._full_statement()
            elif choice == 8:  self._change_pin()
            elif choice == 9:  self._update_mobile()
            elif choice == 10: self._cheque_book_request()
            elif choice == 11: self._account_details()
            elif choice == 12: break

            print()

    # ==================================================================
    # 1. Balance Enquiry
    # ==================================================================

    def _balance_enquiry(self) -> None:
        acc = self._session_account
        assert acc is not None
        box_top()
        box_line("BALANCE ENQUIRY", "center")
        box_mid()
        box_line(f"  Account No.  : {acc.masked_account()}",       "left")
        box_line(f"  Account Type : {acc.account_type.value}",      "left")
        box_line(f"  IFSC Code    : {acc.ifsc_code}",               "left")
        box_mid()
        box_line(f"  Available Balance : ₹{acc.available_balance():>15,.2f}", "left")
        box_line(f"  Ledger Balance    : ₹{acc.balance:>15,.2f}",             "left")
        box_mid()
        box_line(f"  As on : {datetime.now().strftime('%d-%b-%Y  %H:%M:%S')}", "left")
        box_bot()
        self._receipt_prompt(acc, "BALANCE ENQUIRY", acc.balance)

    # ==================================================================
    # 2. Cash Withdrawal
    # ==================================================================

    def _cash_withdrawal(self) -> None:
        acc = self._session_account
        assert acc is not None
        acc.reset_daily_limit_if_new_day()

        remaining_daily = DAILY_WITHDRAWAL_LIMIT - acc.daily_withdrawn
        if remaining_daily <= 0:
            box_top()
            box_line(f"Daily withdrawal limit (₹{DAILY_WITHDRAWAL_LIMIT:,.0f}) reached.", "center")
            box_line("Please try again tomorrow.", "center")
            box_bot()
            return

        box_top()
        box_line("CASH WITHDRAWAL", "center")
        box_mid()
        box_line(f"  Available Balance      : ₹{acc.available_balance():>12,.2f}", "left")
        box_line(f"  Remaining Daily Limit  : ₹{remaining_daily:>12,.2f}",          "left")
        box_mid()
        box_line("  FAST CASH",                                                      "left")
        box_line("  1. ₹   500     2. ₹  1,000    3. ₹  2,000",                    "left")
        box_line("  4. ₹ 5,000     5. ₹ 10,000    6. ₹ 20,000",                    "left")
        box_line("  7. Other Amount                8. Cancel",                       "left")
        box_bot()

        fast_cash = {1: 500, 2: 1_000, 3: 2_000, 4: 5_000, 5: 10_000, 6: 20_000}
        choice = get_int("  Select: ", lo=1, hi=8)
        if choice == 8:
            print("  Transaction cancelled.")
            return

        if choice in fast_cash:
            amount = float(fast_cash[choice])
        else:
            amount = get_amount("  Enter amount (multiples of ₹100): ₹", minimum=100)
            if amount % 100 != 0:
                print("  Amount must be in multiples of ₹100.")
                return

        if amount >= FRAUD_ALERT_THRESHOLD:
            confirm = input(
                f"  Large withdrawal of ₹{amount:,.0f}. Confirm? (YES/NO): "
            ).strip().upper()
            if confirm != "YES":
                print("  Transaction cancelled.")
                return

        if amount > acc.available_balance():
            print("  Insufficient balance.")
            return
        if amount > remaining_daily:
            print(f"  Exceeds remaining daily limit of ₹{remaining_daily:,.2f}.")
            return

        acc.balance         -= amount
        acc.daily_withdrawn += amount
        txn = acc.record_transaction(TransactionType.DEBIT, amount, "ATM CASH WITHDRAWAL")

        notes = denomination_breakdown(int(amount))
        box_top()
        box_line("PLEASE COLLECT YOUR CASH", "center")
        box_mid()
        box_line("  Denomination Breakdown:", "left")
        for denom, count in notes.items():
            box_line(f"    ₹{denom:>5} × {count:>2} = ₹{denom * count:>8,}", "left")
        box_mid()
        box_line(f"  Amount Dispensed : ₹{amount:>10,.2f}",              "left")
        box_line(f"  Available Balance: ₹{acc.available_balance():>10,.2f}", "left")
        box_line(f"  Ref No.          : {txn.ref_no}",                    "left")
        box_bot()
        self._receipt_prompt(acc, "CASH WITHDRAWAL", amount, ref=txn.ref_no)

    # ==================================================================
    # 3. Cash Deposit
    # ==================================================================

    def _cash_deposit(self) -> None:
        acc = self._session_account
        assert acc is not None

        amount = get_amount("  Enter deposit amount: ₹", minimum=100)
        acc.balance += amount
        txn = acc.record_transaction(TransactionType.CREDIT, amount, "ATM CASH DEPOSIT")

        box_top()
        box_line("CASH DEPOSIT SUCCESSFUL", "center")
        box_mid()
        box_line(f"  Amount Deposited : ₹{amount:>12,.2f}", "left")
        box_line(f"  Updated Balance  : ₹{acc.balance:>12,.2f}", "left")
        box_line(f"  Ref No.          : {txn.ref_no}", "left")
        box_bot()
        self._receipt_prompt(acc, "CASH DEPOSIT", amount, ref=txn.ref_no)

    # ==================================================================
    # 4. Fund Transfer
    # ==================================================================

    def _fund_transfer(self) -> None:
        acc = self._session_account
        assert acc is not None

        box_top()
        box_line("FUND TRANSFER", "center")
        box_mid()
        box_line("  Transfer Mode:", "left")
        box_line("  1. NEFT  (up to 2 hrs settlement)", "left")
        box_line("  2. IMPS  (instant, 24×7)",           "left")
        box_line("  3. Cancel",                           "left")
        box_bot()
        mode_choice = get_int("  Select mode: ", lo=1, hi=3)
        if mode_choice == 3:
            print("  Transfer cancelled.")
            return
        mode = "NEFT" if mode_choice == 1 else "IMPS"

        beneficiary_acc = input("  Beneficiary Account No.: ").strip()
        if not beneficiary_acc.isdigit() or len(beneficiary_acc) < 9:
            print("  Invalid account number.")
            return

        beneficiary_ifsc = input("  Beneficiary IFSC Code  : ").strip().upper()
        if len(beneficiary_ifsc) != 11:
            print("  Invalid IFSC code (must be 11 characters).")
            return

        beneficiary_name = input("  Beneficiary Name       : ").strip()
        if not beneficiary_name:
            print("  Beneficiary name cannot be empty.")
            return

        amount = get_amount("  Transfer Amount: ₹", minimum=1)

        if amount > acc.available_balance():
            print("  Insufficient balance.")
            return

        otp = sim_otp()
        print(f"\n  OTP sent to {acc.masked_mobile()}")
        print(f"  [DEMO – OTP is: {otp}]\n")
        entered_otp = input("  Enter OTP: ").strip()
        if entered_otp != otp:
            print("  Incorrect OTP. Transaction cancelled.")
            return

        acc.balance -= amount
        desc = (
            f"{mode} TO {beneficiary_acc[-4:].upper()} "
            f"/ {beneficiary_name[:15].upper()}"
        )
        txn = acc.record_transaction(TransactionType.DEBIT, amount, desc)

        box_top()
        box_line(f"FUND TRANSFER ({mode}) SUCCESSFUL", "center")
        box_mid()
        box_line(f"  To Account  : XXXXXX{beneficiary_acc[-4:]}",          "left")
        box_line(f"  IFSC        : {beneficiary_ifsc}",                     "left")
        box_line(f"  Beneficiary : {beneficiary_name[:30].upper()}",        "left")
        box_line(f"  Amount      : ₹{amount:>12,.2f}",                      "left")
        box_line(f"  New Balance : ₹{acc.balance:>12,.2f}",                 "left")
        box_line(f"  Ref No.     : {txn.ref_no}",                           "left")
        box_bot()
        self._receipt_prompt(acc, f"FUND TRANSFER {mode}", amount, ref=txn.ref_no)

    # ==================================================================
    # 5. Bill Payment
    # ==================================================================

    def _bill_payment(self) -> None:
        acc = self._session_account
        assert acc is not None

        box_top()
        box_line("BILL PAYMENT", "center")
        box_mid()
        box_line("  1. Electricity Bill",          "left")
        box_line("  2. Mobile Recharge (Prepaid)", "left")
        box_line("  3. DTH Recharge",              "left")
        box_line("  4. Cancel",                    "left")
        box_bot()
        choice = get_int("  Select: ", lo=1, hi=4)
        if choice == 4:
            print("  Payment cancelled.")
            return

        service_map = {1: "ELECTRICITY", 2: "MOBILE RECHARGE", 3: "DTH RECHARGE"}
        service = service_map[choice]

        consumer_id = input(f"  Consumer / Mobile No. for {service}: ").strip()
        if not consumer_id:
            print("  Consumer ID cannot be empty.")
            return

        amount = get_amount("  Amount: ₹", minimum=10)

        if amount > acc.available_balance():
            print("  Insufficient balance.")
            return

        if amount >= 1000:
            otp = sim_otp()
            print(f"\n  OTP sent to {acc.masked_mobile()}")
            print(f"  [DEMO – OTP is: {otp}]\n")
            entered = input("  Enter OTP: ").strip()
            if entered != otp:
                print("  Incorrect OTP. Payment cancelled.")
                return

        acc.balance -= amount
        desc = f"BILL PMT {service[:15]} {consumer_id[-4:]}"
        txn = acc.record_transaction(TransactionType.DEBIT, amount, desc)

        box_top()
        box_line("BILL PAYMENT SUCCESSFUL", "center")
        box_mid()
        box_line(f"  Service     : {service}",                          "left")
        box_line(f"  Consumer ID : {consumer_id}",                      "left")
        box_line(f"  Amount Paid : ₹{amount:>10,.2f}",                  "left")
        box_line(f"  New Balance : ₹{acc.balance:>10,.2f}",             "left")
        box_line(f"  Ref No.     : {txn.ref_no}",                       "left")
        box_bot()
        self._receipt_prompt(acc, f"BILL PMT {service}", amount, ref=txn.ref_no)

    # ==================================================================
    # 6. Mini Statement
    # ==================================================================

    def _mini_statement(self) -> None:
        acc = self._session_account
        assert acc is not None
        last5 = acc.transactions[-5:]

        box_top()
        box_line("MINI STATEMENT  (Last 5 Transactions)", "center")
        box_mid()
        box_line(f"  Account : {acc.masked_account()}  |  {acc.account_type.value}", "left")
        box_mid()
        if not last5:
            box_line("  No transactions found.", "left")
        else:
            for txn in reversed(last5):
                box_line(txn.display_line(), "left")
        box_mid()
        box_line(f"  Available Balance : ₹{acc.available_balance():>15,.2f}", "left")
        box_bot()

    # ==================================================================
    # 7. Full Statement
    # ==================================================================

    def _full_statement(self) -> None:
        acc = self._session_account
        assert acc is not None

        box_top()
        box_line("FULL ACCOUNT STATEMENT", "center")
        box_mid()
        box_line(f"  Account Holder : {acc.account_holder}",         "left")
        box_line(f"  Account No.    : {acc.masked_account()}",        "left")
        box_line(f"  Account Type   : {acc.account_type.value}",      "left")
        box_line(f"  IFSC Code      : {acc.ifsc_code}",               "left")
        box_line(f"  Branch         : {acc.branch}",                  "left")
        box_mid()
        box_line("  Date-Time            Type  Amount              Balance", "left")
        box_mid()
        if not acc.transactions:
            box_line("  No transactions found.", "left")
        else:
            for txn in reversed(acc.transactions):
                box_line(txn.display_line(), "left")
        box_mid()
        box_line(f"  Total Transactions : {len(acc.transactions)}",          "left")
        box_line(f"  Available Balance  : ₹{acc.available_balance():>15,.2f}", "left")
        box_bot()

    # ==================================================================
    # 8. PIN Change
    # ==================================================================

    def _change_pin(self) -> None:
        acc = self._session_account
        assert acc is not None

        box_top()
        box_line("PIN CHANGE", "center")
        box_bot()

        current = get_pin_input("  Enter current PIN: ")
        if current != acc.pin:
            print("  Incorrect PIN. PIN change cancelled.")
            return

        new_pin = get_pin_input("  Enter new 4-digit PIN: ")
        if not new_pin.isdigit() or len(new_pin) != 4:
            print("  PIN must be exactly 4 digits.")
            return

        confirm = get_pin_input("  Confirm new PIN: ")
        if new_pin != confirm:
            print("  PINs do not match. PIN change cancelled.")
            return

        if new_pin == current:
            print("  New PIN cannot be the same as the current PIN.")
            return

        acc.pin = new_pin
        box_top()
        box_line("PIN changed successfully.", "center")
        box_line("Please remember your new PIN.", "center")
        box_bot()

    # ==================================================================
    # 9. Mobile Number Update
    # ==================================================================

    def _update_mobile(self) -> None:
        acc = self._session_account
        assert acc is not None

        box_top()
        box_line("MOBILE NUMBER UPDATE", "center")
        box_mid()
        box_line(f"  Registered Mobile : {acc.masked_mobile()}", "left")
        box_bot()

        new_mobile = input("  Enter new 10-digit mobile number: ").strip()
        if not new_mobile.isdigit() or len(new_mobile) != 10:
            print("  Invalid mobile number. Must be 10 digits.")
            return

        otp = sim_otp()
        print(f"\n  OTP sent to +91 {new_mobile}")
        print(f"  [DEMO – OTP is: {otp}]\n")
        entered = input("  Enter OTP: ").strip()
        if entered != otp:
            print("  Incorrect OTP. Update cancelled.")
            return

        acc.mobile = new_mobile
        box_top()
        box_line("Mobile number updated successfully.", "center")
        box_bot()

    # ==================================================================
    # 10. Cheque Book Request
    # ==================================================================

    def _cheque_book_request(self) -> None:
        acc = self._session_account
        assert acc is not None

        box_top()
        box_line("CHEQUE BOOK REQUEST", "center")
        box_mid()
        box_line("  1. 10 leaves", "left")
        box_line("  2. 25 leaves", "left")
        box_line("  3. Cancel",    "left")
        box_bot()
        choice = get_int("  Select: ", lo=1, hi=3)
        if choice == 3:
            print("  Request cancelled.")
            return

        leaves = 10 if choice == 1 else 25
        acc.cheque_requests += 1
        ref = "CHQ" + uuid.uuid4().hex[:8].upper()

        box_top()
        box_line("CHEQUE BOOK REQUEST SUBMITTED", "center")
        box_mid()
        box_line(f"  Leaves      : {leaves}",                                    "left")
        box_line("  Delivery    : Registered Address (5-7 working days)", "left")
        box_line(f"  Request Ref : {ref}",                                        "left")
        box_bot()

    # ==================================================================
    # 11. Account Details
    # ==================================================================

    def _account_details(self) -> None:
        acc = self._session_account
        assert acc is not None

        box_top()
        box_line("ACCOUNT DETAILS", "center")
        box_mid()
        box_line(f"  Name         : {acc.account_holder}",        "left")
        box_line(f"  Account No.  : {acc.masked_account()}",       "left")
        box_line(f"  Account Type : {acc.account_type.value}",     "left")
        box_line(f"  IFSC Code    : {acc.ifsc_code}",              "left")
        box_line(f"  Branch       : {acc.branch}",                 "left")
        box_line(f"  Mobile       : {acc.masked_mobile()}",        "left")
        box_line(f"  Card No.     : {acc.masked_card()}",          "left")
        box_line(f"  Card Expiry  : {acc.card_expiry}",            "left")
        box_bot()

    # ==================================================================
    # Receipt helper
    # ==================================================================

    def _receipt_prompt(
        self,
        acc:    Account,
        title:  str,
        amount: float,
        ref:    str = "",
    ) -> None:
        """Ask the customer if they want a printed receipt; render one if yes."""
        want = input("\n  Do you want a receipt? (Y/N): ").strip().upper()
        if want != "Y":
            return
        print()
        print("  ┌──────────────────────────────────────┐")
        print(f"  │ {self.BANK_NAME:^38} │")
        print("  ├──────────────────────────────────────┤")
        print(f"  │ {title:^38} │")
        print("  ├──────────────────────────────────────┤")
        print(f"  │ Date : {datetime.now().strftime('%d-%b-%Y  %H:%M:%S'):<29} │")
        print(f"  │ A/c  : {acc.masked_account():<30} │")
        print(f"  │ Amt  : ₹{amount:<29,.2f} │")
        if ref:
            print(f"  │ Ref  : {ref:<30} │")
        print(f"  │ Bal  : ₹{acc.available_balance():<29,.2f} │")
        print("  └──────────────────────────────────────┘")
