# Indian Bank ATM — Python + Java

This repository contains a full-featured, console-based ATM simulation in
**Python** (advanced, Indian-bank style) and a simple **Java** version.

---

## Python version — Advanced Indian Bank ATM

### Features

| Category | Details |
|---|---|
| **Auth** | 4-digit PIN, 3 attempts, card lock on failure |
| **Currency** | Indian Rupees (₹) throughout |
| **Balance Enquiry** | Available vs ledger balance, IFSC, account type |
| **Cash Withdrawal** | Fast-Cash (₹500/1K/2K/5K/10K/20K), custom amount, denomination breakdown |
| **Daily Limit** | ₹50,000 per card per calendar day |
| **Fraud Alert** | Extra confirmation for amounts ≥ ₹25,000 |
| **Cash Deposit** | With updated balance confirmation |
| **Fund Transfer** | NEFT / IMPS with OTP simulation |
| **Bill Payment** | Electricity, Mobile Recharge, DTH (OTP for ≥ ₹1,000) |
| **Mini Statement** | Last 5 transactions with running balance |
| **Full Statement** | Complete transaction history |
| **PIN Change** | Requires current PIN; enforces 4-digit, non-repeat |
| **Mobile Update** | OTP-verified mobile number change |
| **Cheque Book** | 10- or 25-leaf request with reference number |
| **Account Details** | Masked card, IFSC, branch, mobile |
| **Bilingual** | English / Hindi menus |
| **Receipts** | Optional on-screen receipt after each transaction |

### Package structure

```
atm/                  ← Python package
├── __init__.py       ← public re-exports (BankATM, DEMO_ACCOUNTS)
├── enums.py          ← AccountType, TransactionType, Language
├── models.py         ← Transaction, Account dataclasses
├── ui.py             ← box-drawing helpers + validated input functions
├── strings.py        ← bilingual string dict + T() lookup
├── utils.py          ← constants + sim_otp() + denomination_breakdown()
├── data.py           ← demo accounts (DEMO_ACCOUNTS)
└── bank.py           ← BankATM class (core engine)
main.py               ← primary entry point
atm.py                ← backward-compat shim (python atm.py still works)
```

### Prerequisites

- Python 3.9+  (no third-party libraries required)

### Run

```bash
python main.py
# or
python atm.py
```

### Demo accounts

| Card (last 4) | Type    | Balance     | PIN  |
|:---:|:---:|---:|:---:|
| 9010 | Savings | ₹85,500  | 1234 |
| 1090 | Current | ₹2,50,000 | 5678 |

> **Note:** PINs are hardcoded for demonstration purposes only.
> In a real banking system, PINs are never stored or shown in plain text.

---

## Java version — Simple ATM

### Prerequisites

- Java 17+

### Run

```bash
javac Main.java
java Main
```

---

Follow the on-screen menu to perform ATM operations.
