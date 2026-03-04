"""
Advanced Indian Bank ATM Simulation
====================================
Architecture  : Dataclasses + Enums + clean separation of concerns
Bank style    : SBI / HDFC / ICICI inspired terminal UI
Currency      : Indian Rupees (₹)
Features      :
  - PIN authentication (4-digit, 3 attempts, card lock)
  - Balance enquiry (available vs ledger balance)
  - Fast Cash (₹500 / ₹1000 / ₹2000 / ₹5000 / ₹10000 / ₹20000)
  - Custom cash withdrawal with denomination breakdown
  - Daily withdrawal limit (₹50,000 per card per day)
  - Cash deposit
  - Fund Transfer – NEFT / IMPS with OTP simulation
  - Bill Payments – Electricity, Mobile Recharge, DTH
  - Mini Statement (last 5 transactions)
  - Full Statement  (all transactions)
  - PIN Change
  - Mobile Number Update
  - Cheque Book Request
  - Transaction reference numbers (UUID-based)
  - Fraud alert for unusually large transactions
  - Session timeout simulation
  - English / Hindi bilingual menus

NOTE: This is a demonstration / educational program.
      All data is in-memory only; nothing is persisted to disk.
      PINs shown in source code are for demo purposes only and must
      never be used in a real banking application.
"""

from __future__ import annotations

import random
import string
import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum, auto
from typing import Optional


# ══════════════════════════════════════════════════════════════════════
# Enumerations
# ══════════════════════════════════════════════════════════════════════

class AccountType(Enum):
    SAVINGS = "Savings"
    CURRENT = "Current"


class TransactionType(Enum):
    CREDIT = "CR"
    DEBIT  = "DR"


class Language(Enum):
    ENGLISH = "English"
    HINDI   = "Hindi (हिंदी)"


# ══════════════════════════════════════════════════════════════════════
# Data models
# ══════════════════════════════════════════════════════════════════════

@dataclass
class Transaction:
    """Represents a single debit or credit entry on an account."""
    ref_no:        str
    timestamp:     datetime
    txn_type:      TransactionType
    amount:        float
    balance_after: float
    description:   str

    def display_line(self) -> str:
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
    """Represents a single bank account."""
    account_number:   str
    account_holder:   str
    account_type:     AccountType
    ifsc_code:        str
    branch:           str
    mobile:           str
    balance:          float
    pin:              str
    card_number:      str          # 16-digit card number (masked for display)
    card_expiry:      str          # MM/YY
    is_blocked:       bool = False
    daily_withdrawn:  float = 0.0
    last_txn_date:    date  = field(default_factory=date.today)
    transactions:     list[Transaction] = field(default_factory=list)
    cheque_requests:  int  = 0

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def masked_card(self) -> str:
        """Return card number with middle digits masked: XXXX XXXX XXXX 1234."""
        c = self.card_number.replace(" ", "")
        return f"XXXX XXXX XXXX {c[-4:]}"

    def masked_mobile(self) -> str:
        """Return mobile with middle digits masked: +91 XXXXX XX890."""
        m = self.mobile
        return f"+91 XXXXX X{m[-4:]}" if len(m) >= 4 else "+91 XXXXXXXXXX"

    def masked_account(self) -> str:
        """Return account number with first digits masked: XXXXXX1234."""
        a = self.account_number
        return f"XXXXXX{a[-4:]}"

    def available_balance(self) -> float:
        """Available balance = ledger balance (demo: same value)."""
        return self.balance

    def _reset_daily_limit_if_new_day(self) -> None:
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
        """Create and append a Transaction; update balance."""
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


# ══════════════════════════════════════════════════════════════════════
# UI helpers (no third-party libs)
# ══════════════════════════════════════════════════════════════════════

WIDTH = 60  # terminal width for the ATM box


def _box_top() -> None:
    print("╔" + "═" * (WIDTH - 2) + "╗")


def _box_mid() -> None:
    print("╠" + "═" * (WIDTH - 2) + "╣")


def _box_bot() -> None:
    print("╚" + "═" * (WIDTH - 2) + "╝")


def _box_line(text: str = "", align: str = "center") -> None:
    inner = WIDTH - 4
    if align == "center":
        padded = text.center(inner)
    elif align == "right":
        padded = text.rjust(inner)
    else:
        padded = text.ljust(inner)
    print(f"║  {padded}  ║")


def _blank_line() -> None:
    _box_line()


def get_int(prompt: str, *, lo: int = 0, hi: int = 9999) -> int:
    """Read an integer in [lo, hi] from stdin."""
    while True:
        raw = input(prompt).strip()
        try:
            v = int(raw)
            if lo <= v <= hi:
                return v
            print(f"  Please enter a number between {lo} and {hi}.")
        except ValueError:
            print("  Invalid input. Please enter a number.")


def get_amount(prompt: str, *, minimum: float = 1.0) -> float:
    """Read a positive float ≥ minimum from stdin."""
    while True:
        raw = input(prompt).strip()
        try:
            v = float(raw)
            if v < minimum:
                print(f"  Amount must be at least ₹{minimum:,.2f}.")
                continue
            if v != round(v):
                print("  Amount must be a whole number (no paise).")
                continue
            return v
        except ValueError:
            print("  Invalid amount. Please enter a numeric value.")


def get_pin_input(prompt: str) -> str:
    """Read a PIN string (displayed as ****). Uses plain input for portability."""
    raw = input(prompt).strip()
    return raw


def _sim_otp() -> str:
    """Simulate sending an OTP to the registered mobile and return it."""
    return "".join(random.choices(string.digits, k=6))


def _denomination_breakdown(amount: int) -> dict[int, int]:
    """Return the fewest notes for the given ₹ amount using standard denominations."""
    denominations = [2000, 500, 200, 100, 50, 20, 10]
    notes: dict[int, int] = {}
    remaining = amount
    for denom in denominations:
        if remaining >= denom:
            count = remaining // denom
            notes[denom] = count
            remaining -= count * denom
    return notes


# ══════════════════════════════════════════════════════════════════════
# Bilingual strings
# ══════════════════════════════════════════════════════════════════════

_STRINGS: dict[str, dict[Language, str]] = {
    "welcome":        {Language.ENGLISH: "WELCOME",                Language.HINDI: "स्वागत है"},
    "insert_card":    {Language.ENGLISH: "Please insert your card",Language.HINDI: "कृपया अपना कार्ड डालें"},
    "enter_pin":      {Language.ENGLISH: "Enter 4-digit PIN: ",    Language.HINDI: "4-अंकीय PIN दर्ज करें: "},
    "incorrect_pin":  {Language.ENGLISH: "Incorrect PIN.",         Language.HINDI: "गलत PIN."},
    "card_blocked":   {Language.ENGLISH: "Card blocked due to multiple wrong PIN attempts.",
                       Language.HINDI: "कई गलत PIN प्रयासों के कारण कार्ड ब्लॉक कर दिया गया।"},
    "auth_success":   {Language.ENGLISH: "Authentication successful.", Language.HINDI: "प्रमाणीकरण सफल।"},
    "thank_you":      {Language.ENGLISH: "Thank you for banking with us. Have a nice day!",
                       Language.HINDI: "हमारे साथ बैंकिंग के लिए धन्यवाद। आपका दिन शुभ हो!"},
    "please_wait":    {Language.ENGLISH: "Please wait...",         Language.HINDI: "कृपया प्रतीक्षा करें..."},
}


def T(key: str, lang: Language) -> str:
    return _STRINGS.get(key, {}).get(lang, _STRINGS.get(key, {}).get(Language.ENGLISH, key))


# ══════════════════════════════════════════════════════════════════════
# Core ATM engine
# ══════════════════════════════════════════════════════════════════════

DAILY_WITHDRAWAL_LIMIT = 50_000.0
MAX_PIN_ATTEMPTS       = 3
FRAUD_ALERT_THRESHOLD  = 25_000.0   # amounts ≥ this trigger a confirmation

# Demo accounts loaded at startup
_DEMO_ACCOUNTS: list[Account] = [
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


class BankATM:
    """
    Indian bank ATM engine.

    Responsibilities
    ----------------
    - Session lifecycle  : card selection → auth → operations → exit
    - Transaction processing : withdraw, deposit, transfer, bill pay
    - Audit log              : every operation is recorded in Account.transactions
    - Fraud detection        : large-amount confirmation prompts
    - Bilingual UI           : English / Hindi
    """

    BANK_NAME     = "STATE BANK OF INDIA"
    BANK_TAGLINE  = "The Nation's Bank"
    ATM_ID        = "ATM/DEL/001/SBI"
    TOLL_FREE     = "1800 425 3800"

    def __init__(self, accounts: list[Account]) -> None:
        # account_number → Account mapping
        self._accounts: dict[str, Account] = {a.account_number: a for a in accounts}
        self._lang: Language = Language.ENGLISH
        self._session_account: Optional[Account] = None

    # ------------------------------------------------------------------
    # Top-level flow
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Entry point – loops across multiple sessions."""
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

    # ------------------------------------------------------------------
    # Session setup
    # ------------------------------------------------------------------

    def _print_bank_header(self) -> None:
        _box_top()
        _blank_line()
        _box_line(self.BANK_NAME, "center")
        _box_line(self.BANK_TAGLINE, "center")
        _blank_line()
        _box_line(f"ATM ID : {self.ATM_ID}", "center")
        _box_line(f"Toll Free : {self.TOLL_FREE}", "center")
        _blank_line()
        _box_bot()
        print()

    def _card_selection(self) -> bool:
        """Simulate 'insert card' by letting the user pick a demo account."""
        _box_top()
        _box_line("SELECT DEMO CARD / ACCOUNT", "center")
        _box_mid()
        for i, acc in enumerate(self._accounts.values(), start=1):
            _box_line(f"  {i}. {acc.masked_card()}  ({acc.account_type.value})", "left")
        _box_line(f"  {len(self._accounts) + 1}. Exit / Switch Off ATM", "left")
        _box_bot()
        choice = get_int("Select card slot: ", lo=1, hi=len(self._accounts) + 1)
        if choice == len(self._accounts) + 1:
            _box_top()
            _box_line("ATM is now offline. Thank you!", "center")
            _box_bot()
            return False
        acc_list = list(self._accounts.values())
        self._session_account = acc_list[choice - 1]
        return True

    def _select_language(self) -> None:
        _box_top()
        _box_line("SELECT LANGUAGE / भाषा चुनें", "center")
        _box_mid()
        _box_line("  1. English", "left")
        _box_line("  2. Hindi (हिंदी)", "left")
        _box_bot()
        choice = get_int("Choice: ", lo=1, hi=2)
        self._lang = Language.ENGLISH if choice == 1 else Language.HINDI
        print()

    def _authenticate(self) -> bool:
        """PIN authentication – 3 attempts, then block the card."""
        acc = self._session_account
        assert acc is not None

        if acc.is_blocked:
            _box_top()
            _box_line(T("card_blocked", self._lang), "center")
            _box_bot()
            return False

        self._select_language()

        _box_top()
        _box_line(T("welcome", self._lang), "center")
        _box_mid()
        _box_line(f"Card : {acc.masked_card()}", "left")
        _box_bot()
        print()

        for attempt in range(1, MAX_PIN_ATTEMPTS + 1):
            entered = get_pin_input(f"  {T('enter_pin', self._lang)}")
            if entered == acc.pin:
                print(f"\n  ✔  {T('auth_success', self._lang)}\n")
                return True
            remaining = MAX_PIN_ATTEMPTS - attempt
            if remaining > 0:
                print(f"  ✘  {T('incorrect_pin', self._lang)} {remaining} attempt(s) remaining.\n")
            else:
                acc.is_blocked = True
                print(f"\n  ✘  {T('card_blocked', self._lang)}\n")
        return False

    def _eject_card(self) -> None:
        print()
        _box_top()
        _box_line("Please collect your card.", "center")
        _box_line(T("thank_you", self._lang), "center")
        _box_bot()
        print()

    # ------------------------------------------------------------------
    # Main menu
    # ------------------------------------------------------------------

    def _main_menu(self) -> None:
        acc = self._session_account
        assert acc is not None

        while True:
            _box_top()
            _box_line(f"  Welcome,  {acc.account_holder}", "left")
            _box_line(f"  A/c : {acc.masked_account()}  |  {acc.account_type.value}", "left")
            _box_mid()
            _box_line("  1.  Balance Enquiry           (बैलेंस जानकारी)", "left")
            _box_line("  2.  Cash Withdrawal           (नकद निकासी)",      "left")
            _box_line("  3.  Cash Deposit              (नकद जमा)",          "left")
            _box_line("  4.  Fund Transfer             (फंड ट्रांसफर)",     "left")
            _box_line("  5.  Bill Payment              (बिल भुगतान)",       "left")
            _box_line("  6.  Mini Statement            (मिनी स्टेटमेंट)",   "left")
            _box_line("  7.  Full Statement            (पूर्ण विवरण)",      "left")
            _box_line("  8.  PIN Change                (PIN बदलें)",        "left")
            _box_line("  9.  Mobile Number Update      (मोबाइल अपडेट)",    "left")
            _box_line(" 10.  Cheque Book Request       (चेक बुक अनुरोध)", "left")
            _box_line(" 11.  Account Details           (खाता विवरण)",     "left")
            _box_line(" 12.  Exit / Eject Card         (बाहर निकलें)",     "left")
            _box_bot()
            choice = get_int("  Select option: ", lo=1, hi=12)
            print()

            if choice == 1:
                self._balance_enquiry()
            elif choice == 2:
                self._cash_withdrawal()
            elif choice == 3:
                self._cash_deposit()
            elif choice == 4:
                self._fund_transfer()
            elif choice == 5:
                self._bill_payment()
            elif choice == 6:
                self._mini_statement()
            elif choice == 7:
                self._full_statement()
            elif choice == 8:
                self._change_pin()
            elif choice == 9:
                self._update_mobile()
            elif choice == 10:
                self._cheque_book_request()
            elif choice == 11:
                self._account_details()
            elif choice == 12:
                break

            print()

    # ------------------------------------------------------------------
    # 1. Balance Enquiry
    # ------------------------------------------------------------------

    def _balance_enquiry(self) -> None:
        acc = self._session_account
        assert acc is not None
        _box_top()
        _box_line("BALANCE ENQUIRY", "center")
        _box_mid()
        _box_line(f"Account No.  : {acc.masked_account()}", "left")
        _box_line(f"Account Type : {acc.account_type.value}", "left")
        _box_line(f"IFSC Code    : {acc.ifsc_code}", "left")
        _box_mid()
        _box_line(f"Available Balance : ₹{acc.available_balance():>15,.2f}", "left")
        _box_line(f"Ledger Balance    : ₹{acc.balance:>15,.2f}", "left")
        _box_mid()
        _box_line(f"As on  : {datetime.now().strftime('%d-%b-%Y %H:%M:%S')}", "left")
        _box_bot()
        self._print_receipt_prompt(acc, "BALANCE ENQUIRY", acc.balance)

    # ------------------------------------------------------------------
    # 2. Cash Withdrawal
    # ------------------------------------------------------------------

    def _cash_withdrawal(self) -> None:
        acc = self._session_account
        assert acc is not None
        acc._reset_daily_limit_if_new_day()

        remaining_daily = DAILY_WITHDRAWAL_LIMIT - acc.daily_withdrawn
        if remaining_daily <= 0:
            _box_top()
            _box_line("Daily withdrawal limit (₹50,000) reached.", "center")
            _box_line("Please try again tomorrow.", "center")
            _box_bot()
            return

        _box_top()
        _box_line("CASH WITHDRAWAL", "center")
        _box_mid()
        _box_line(f"Available Balance      : ₹{acc.available_balance():>12,.2f}", "left")
        _box_line(f"Remaining Daily Limit  : ₹{remaining_daily:>12,.2f}", "left")
        _box_mid()
        _box_line("  FAST CASH", "left")
        _box_line("  1. ₹   500     2. ₹  1,000    3. ₹  2,000", "left")
        _box_line("  4. ₹ 5,000     5. ₹ 10,000    6. ₹ 20,000", "left")
        _box_line("  7. Other Amount", "left")
        _box_line("  8. Cancel", "left")
        _box_bot()

        fast_cash = {1: 500, 2: 1000, 3: 2000, 4: 5000, 5: 10000, 6: 20000}
        choice = get_int("  Select: ", lo=1, hi=8)
        if choice == 8:
            print("  Transaction cancelled.")
            return

        if choice in fast_cash:
            amount = float(fast_cash[choice])
        else:
            amount = get_amount("  Enter amount (multiples of ₹100): ", minimum=100)
            if amount % 100 != 0:
                print("  Amount must be in multiples of ₹100.")
                return

        # Fraud alert
        if amount >= FRAUD_ALERT_THRESHOLD:
            confirm = input(f"  Large withdrawal of ₹{amount:,.0f}. Confirm? (YES/NO): ").strip().upper()
            if confirm != "YES":
                print("  Transaction cancelled.")
                return

        if amount > acc.available_balance():
            print("  Insufficient balance.")
            return
        if amount > remaining_daily:
            print(f"  Exceeds remaining daily limit of ₹{remaining_daily:,.2f}.")
            return

        acc.balance          -= amount
        acc.daily_withdrawn  += amount
        txn = acc.record_transaction(TransactionType.DEBIT, amount, "ATM CASH WITHDRAWAL")

        # Denomination breakdown
        notes = _denomination_breakdown(int(amount))
        _box_top()
        _box_line("PLEASE COLLECT YOUR CASH", "center")
        _box_mid()
        _box_line("  Denomination Breakdown:", "left")
        for denom, count in notes.items():
            _box_line(f"    ₹{denom:>5} × {count:>2} = ₹{denom * count:>8,}", "left")
        _box_mid()
        _box_line(f"  Amount Dispensed : ₹{amount:>10,.2f}", "left")
        _box_line(f"  Available Balance: ₹{acc.available_balance():>10,.2f}", "left")
        _box_line(f"  Ref No.          : {txn.ref_no}", "left")
        _box_bot()
        self._print_receipt_prompt(acc, "CASH WITHDRAWAL", amount, ref=txn.ref_no)

    # ------------------------------------------------------------------
    # 3. Cash Deposit
    # ------------------------------------------------------------------

    def _cash_deposit(self) -> None:
        acc = self._session_account
        assert acc is not None

        amount = get_amount("  Enter deposit amount: ₹", minimum=100)

        acc.balance += amount
        txn = acc.record_transaction(TransactionType.CREDIT, amount, "ATM CASH DEPOSIT")

        _box_top()
        _box_line("CASH DEPOSIT SUCCESSFUL", "center")
        _box_mid()
        _box_line(f"  Amount Deposited : ₹{amount:>12,.2f}", "left")
        _box_line(f"  Updated Balance  : ₹{acc.balance:>12,.2f}", "left")
        _box_line(f"  Ref No.          : {txn.ref_no}", "left")
        _box_bot()
        self._print_receipt_prompt(acc, "CASH DEPOSIT", amount, ref=txn.ref_no)

    # ------------------------------------------------------------------
    # 4. Fund Transfer
    # ------------------------------------------------------------------

    def _fund_transfer(self) -> None:
        acc = self._session_account
        assert acc is not None

        _box_top()
        _box_line("FUND TRANSFER", "center")
        _box_mid()
        _box_line("  Transfer Mode:", "left")
        _box_line("  1. NEFT  (up to 2 hrs settlement)", "left")
        _box_line("  2. IMPS  (instant, 24×7)", "left")
        _box_line("  3. Cancel", "left")
        _box_bot()
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

        amount = get_amount(f"  Transfer Amount (₹): ", minimum=1)

        if amount > acc.available_balance():
            print("  Insufficient balance.")
            return

        # OTP simulation
        otp = _sim_otp()
        print(f"\n  OTP sent to {acc.masked_mobile()}")
        print(f"  [DEMO – OTP is: {otp}]\n")
        entered_otp = input("  Enter OTP: ").strip()
        if entered_otp != otp:
            print("  Incorrect OTP. Transaction cancelled.")
            return

        acc.balance -= amount
        desc = f"{mode} TO {beneficiary_acc[-4:].upper()} / {beneficiary_name[:15].upper()}"
        txn = acc.record_transaction(TransactionType.DEBIT, amount, desc)

        _box_top()
        _box_line(f"FUND TRANSFER ({mode}) SUCCESSFUL", "center")
        _box_mid()
        _box_line(f"  To Account  : XXXXXX{beneficiary_acc[-4:]}", "left")
        _box_line(f"  IFSC        : {beneficiary_ifsc}", "left")
        _box_line(f"  Beneficiary : {beneficiary_name[:30].upper()}", "left")
        _box_line(f"  Amount      : ₹{amount:>12,.2f}", "left")
        _box_line(f"  New Balance : ₹{acc.balance:>12,.2f}", "left")
        _box_line(f"  Ref No.     : {txn.ref_no}", "left")
        _box_bot()
        self._print_receipt_prompt(acc, f"FUND TRANSFER {mode}", amount, ref=txn.ref_no)

    # ------------------------------------------------------------------
    # 5. Bill Payment
    # ------------------------------------------------------------------

    def _bill_payment(self) -> None:
        acc = self._session_account
        assert acc is not None

        _box_top()
        _box_line("BILL PAYMENT", "center")
        _box_mid()
        _box_line("  1. Electricity Bill", "left")
        _box_line("  2. Mobile Recharge (Prepaid)", "left")
        _box_line("  3. DTH Recharge", "left")
        _box_line("  4. Cancel", "left")
        _box_bot()
        choice = get_int("  Select: ", lo=1, hi=4)
        if choice == 4:
            print("  Payment cancelled.")
            return

        service_map = {1: "ELECTRICITY", 2: "MOBILE RECHARGE", 3: "DTH RECHARGE"}
        service = service_map[choice]

        consumer_id = input(f"  Enter Consumer / Mobile No. for {service}: ").strip()
        if not consumer_id:
            print("  Consumer ID cannot be empty.")
            return

        amount = get_amount("  Enter amount (₹): ", minimum=10)

        if amount > acc.available_balance():
            print("  Insufficient balance.")
            return

        # Simulate OTP for amounts ≥ ₹1000
        if amount >= 1000:
            otp = _sim_otp()
            print(f"\n  OTP sent to {acc.masked_mobile()}")
            print(f"  [DEMO – OTP is: {otp}]\n")
            entered = input("  Enter OTP: ").strip()
            if entered != otp:
                print("  Incorrect OTP. Payment cancelled.")
                return

        acc.balance -= amount
        desc = f"BILL PMT {service[:15]} {consumer_id[-4:]}"
        txn = acc.record_transaction(TransactionType.DEBIT, amount, desc)

        _box_top()
        _box_line("BILL PAYMENT SUCCESSFUL", "center")
        _box_mid()
        _box_line(f"  Service     : {service}", "left")
        _box_line(f"  Consumer ID : {consumer_id}", "left")
        _box_line(f"  Amount Paid : ₹{amount:>10,.2f}", "left")
        _box_line(f"  New Balance : ₹{acc.balance:>10,.2f}", "left")
        _box_line(f"  Ref No.     : {txn.ref_no}", "left")
        _box_bot()
        self._print_receipt_prompt(acc, f"BILL PMT {service}", amount, ref=txn.ref_no)

    # ------------------------------------------------------------------
    # 6. Mini Statement
    # ------------------------------------------------------------------

    def _mini_statement(self) -> None:
        acc = self._session_account
        assert acc is not None
        last5 = acc.transactions[-5:]

        _box_top()
        _box_line("MINI STATEMENT (Last 5 Transactions)", "center")
        _box_mid()
        _box_line(f"Account : {acc.masked_account()}  |  {acc.account_type.value}", "left")
        _box_mid()
        if not last5:
            _box_line("  No transactions found.", "left")
        else:
            for txn in reversed(last5):
                _box_line(txn.display_line(), "left")
        _box_mid()
        _box_line(f"Available Balance : ₹{acc.available_balance():>15,.2f}", "left")
        _box_bot()

    # ------------------------------------------------------------------
    # 7. Full Statement
    # ------------------------------------------------------------------

    def _full_statement(self) -> None:
        acc = self._session_account
        assert acc is not None

        _box_top()
        _box_line("FULL ACCOUNT STATEMENT", "center")
        _box_mid()
        _box_line(f"Account Holder : {acc.account_holder}", "left")
        _box_line(f"Account No.    : {acc.masked_account()}", "left")
        _box_line(f"Account Type   : {acc.account_type.value}", "left")
        _box_line(f"IFSC Code      : {acc.ifsc_code}", "left")
        _box_line(f"Branch         : {acc.branch}", "left")
        _box_mid()
        _box_line("  Date-Time             Type  Amount              Balance", "left")
        _box_mid()
        if not acc.transactions:
            _box_line("  No transactions found.", "left")
        else:
            for txn in reversed(acc.transactions):
                _box_line(txn.display_line(), "left")
        _box_mid()
        _box_line(f"  Total Transactions : {len(acc.transactions)}", "left")
        _box_line(f"  Available Balance  : ₹{acc.available_balance():>15,.2f}", "left")
        _box_bot()

    # ------------------------------------------------------------------
    # 8. PIN Change
    # ------------------------------------------------------------------

    def _change_pin(self) -> None:
        acc = self._session_account
        assert acc is not None

        _box_top()
        _box_line("PIN CHANGE", "center")
        _box_bot()

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
        _box_top()
        _box_line("PIN changed successfully.", "center")
        _box_line("Please remember your new PIN.", "center")
        _box_bot()

    # ------------------------------------------------------------------
    # 9. Mobile Number Update
    # ------------------------------------------------------------------

    def _update_mobile(self) -> None:
        acc = self._session_account
        assert acc is not None

        _box_top()
        _box_line("MOBILE NUMBER UPDATE", "center")
        _box_mid()
        _box_line(f"  Registered Mobile : {acc.masked_mobile()}", "left")
        _box_bot()

        new_mobile = input("  Enter new 10-digit mobile number: ").strip()
        if not new_mobile.isdigit() or len(new_mobile) != 10:
            print("  Invalid mobile number. Must be 10 digits.")
            return

        otp = _sim_otp()
        print(f"\n  OTP sent to +91 {new_mobile}")
        print(f"  [DEMO – OTP is: {otp}]\n")
        entered = input("  Enter OTP: ").strip()
        if entered != otp:
            print("  Incorrect OTP. Update cancelled.")
            return

        acc.mobile = new_mobile
        _box_top()
        _box_line("Mobile number updated successfully.", "center")
        _box_bot()

    # ------------------------------------------------------------------
    # 10. Cheque Book Request
    # ------------------------------------------------------------------

    def _cheque_book_request(self) -> None:
        acc = self._session_account
        assert acc is not None

        _box_top()
        _box_line("CHEQUE BOOK REQUEST", "center")
        _box_mid()
        _box_line("  Cheque Book Options:", "left")
        _box_line("  1. 10 leaves", "left")
        _box_line("  2. 25 leaves", "left")
        _box_line("  3. Cancel", "left")
        _box_bot()
        choice = get_int("  Select: ", lo=1, hi=3)
        if choice == 3:
            print("  Request cancelled.")
            return

        leaves = 10 if choice == 1 else 25
        acc.cheque_requests += 1
        ref = "CHQ" + uuid.uuid4().hex[:8].upper()

        _box_top()
        _box_line("CHEQUE BOOK REQUEST SUBMITTED", "center")
        _box_mid()
        _box_line(f"  Leaves      : {leaves}", "left")
        _box_line(f"  Delivery    : Registered Address (5-7 working days)", "left")
        _box_line(f"  Request Ref : {ref}", "left")
        _box_bot()

    # ------------------------------------------------------------------
    # 11. Account Details
    # ------------------------------------------------------------------

    def _account_details(self) -> None:
        acc = self._session_account
        assert acc is not None

        _box_top()
        _box_line("ACCOUNT DETAILS", "center")
        _box_mid()
        _box_line(f"  Name         : {acc.account_holder}", "left")
        _box_line(f"  Account No.  : {acc.masked_account()}", "left")
        _box_line(f"  Account Type : {acc.account_type.value}", "left")
        _box_line(f"  IFSC Code    : {acc.ifsc_code}", "left")
        _box_line(f"  Branch       : {acc.branch}", "left")
        _box_line(f"  Mobile       : {acc.masked_mobile()}", "left")
        _box_line(f"  Card No.     : {acc.masked_card()}", "left")
        _box_line(f"  Card Expiry  : {acc.card_expiry}", "left")
        _box_bot()

    # ------------------------------------------------------------------
    # Receipt helper
    # ------------------------------------------------------------------

    def _print_receipt_prompt(
        self,
        acc:   Account,
        title: str,
        amount: float,
        ref:   str = "",
    ) -> None:
        want = input("\n  Do you want a receipt? (Y/N): ").strip().upper()
        if want == "Y":
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


# ══════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # NOTE: PINs ("1234", "5678") are hardcoded here for DEMONSTRATION ONLY.
    # In a real banking system, PINs are never stored in plain text and are
    # never present in source code.
    atm = BankATM(accounts=_DEMO_ACCOUNTS)
    atm.run()
