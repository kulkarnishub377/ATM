"""
Simple console ATM simulation.
Supports: check balance, deposit, withdraw, change PIN, view transaction history, and exit.
"""


def get_float(prompt: str) -> float:
    """Prompt the user until a valid positive float is entered."""
    while True:
        raw = input(prompt).strip()
        try:
            value = float(raw)
            if value <= 0:
                print("Amount must be greater than zero. Please try again.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a numeric amount.")


def get_int(prompt: str) -> int:
    """Prompt the user until a valid integer is entered."""
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print("Invalid input. Please enter a number.")


class ATM:
    """Represents a simple ATM with PIN authentication."""

    def __init__(self, pin: str, initial_balance: float = 500.00) -> None:
        self._pin = pin
        self._balance = initial_balance
        self._transactions: list[str] = []

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def authenticate(self) -> bool:
        """Ask the user for their PIN. Allow up to 3 attempts."""
        for attempt in range(1, 4):
            entered = input("Enter your PIN: ").strip()
            if entered == self._pin:
                return True
            remaining = 3 - attempt
            if remaining:
                print(f"Incorrect PIN. {remaining} attempt(s) remaining.")
            else:
                print("Card blocked. Too many incorrect PIN attempts.")
        return False

    # ------------------------------------------------------------------
    # ATM operations
    # ------------------------------------------------------------------

    def show_balance(self) -> None:
        print(f"  Your current balance is: ${self._balance:,.2f}")

    def deposit(self) -> None:
        amount = get_float("  Enter amount to deposit: $")
        self._balance += amount
        note = f"Deposited  ${amount:>10,.2f}  |  Balance: ${self._balance:,.2f}"
        self._transactions.append(note)
        print(f"  Deposited ${amount:,.2f} successfully.  New balance: ${self._balance:,.2f}")

    def withdraw(self) -> None:
        amount = get_float("  Enter amount to withdraw: $")
        if amount > self._balance:
            print("  Insufficient funds.")
            return
        self._balance -= amount
        note = f"Withdrew   ${amount:>10,.2f}  |  Balance: ${self._balance:,.2f}"
        self._transactions.append(note)
        print(f"  Withdrew ${amount:,.2f} successfully.  New balance: ${self._balance:,.2f}")

    def change_pin(self) -> None:
        current = input("  Enter current PIN: ").strip()
        if current != self._pin:
            print("  Incorrect PIN. PIN change cancelled.")
            return
        new_pin = input("  Enter new PIN: ").strip()
        if not new_pin.isdigit() or not (4 <= len(new_pin) <= 8):
            print("  PIN must be 4–8 digits. PIN change cancelled.")
            return
        confirm = input("  Confirm new PIN: ").strip()
        if new_pin != confirm:
            print("  PINs do not match. PIN change cancelled.")
            return
        self._pin = new_pin
        print("  PIN changed successfully.")

    def show_history(self) -> None:
        if not self._transactions:
            print("  No transactions yet.")
            return
        print("  --- Transaction History ---")
        for i, record in enumerate(self._transactions, start=1):
            print(f"  {i:>3}. {record}")
        print("  ---------------------------")

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        print("=================================")
        print("       Simple ATM System         ")
        print("=================================")

        if not self.authenticate():
            return

        print("\nAuthentication successful. Welcome!\n")

        while True:
            print("---------------------------------")
            print("  1. Check Balance")
            print("  2. Deposit")
            print("  3. Withdraw")
            print("  4. Transaction History")
            print("  5. Change PIN")
            print("  6. Exit")
            print("---------------------------------")
            choice = get_int("Choose an option: ")
            print()

            if choice == 1:
                self.show_balance()
            elif choice == 2:
                self.deposit()
            elif choice == 3:
                self.withdraw()
            elif choice == 4:
                self.show_history()
            elif choice == 5:
                self.change_pin()
            elif choice == 6:
                print("Thank you for using the ATM. Goodbye!")
                break
            else:
                print("Invalid choice. Please choose 1–6.")

            print()


if __name__ == "__main__":
    # NOTE: PIN "1234" is used here for demonstration purposes only.
    # Never use a hardcoded or trivially guessable PIN in production code.
    atm = ATM(pin="1234", initial_balance=500.00)
    atm.run()
