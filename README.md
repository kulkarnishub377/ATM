# Simple ATM

This repository contains a console-based ATM simulation in **two languages** —
Java (`Main.java`) and Python (`atm.py`).

Both versions keep a single in-memory balance for demonstration purposes only.

---

## Features

- PIN authentication (up to 3 attempts)
- Check balance
- Deposit funds
- Withdraw funds
- View transaction history
- Change PIN

---

## Python version

### Prerequisites

- Python 3.9+

### Run

```bash
python atm.py
```

The default PIN is **1234** and the starting balance is **$500.00**.

---

## Java version

### Prerequisites

- Java 17+ (or any recent Java version that can compile `Main.java`)

### Run

```bash
javac Main.java
java Main
```

---

Follow the on-screen menu to perform ATM operations.
