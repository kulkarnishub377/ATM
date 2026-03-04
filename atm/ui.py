"""
atm.ui
------
Terminal UI helpers: box-drawing characters and validated input functions.
No internal package dependencies (safe to import anywhere).
"""

WIDTH = 60  # total character width of the ATM box (including border chars)


# ------------------------------------------------------------------
# Box-drawing primitives
# ------------------------------------------------------------------

def box_top() -> None:
    print("╔" + "═" * (WIDTH - 2) + "╗")


def box_mid() -> None:
    print("╠" + "═" * (WIDTH - 2) + "╣")


def box_bot() -> None:
    print("╚" + "═" * (WIDTH - 2) + "╝")


def box_line(text: str = "", align: str = "center") -> None:
    inner = WIDTH - 4
    if align == "center":
        padded = text.center(inner)
    elif align == "right":
        padded = text.rjust(inner)
    else:
        padded = text.ljust(inner)
    print(f"║  {padded}  ║")


def blank_line() -> None:
    box_line()


# ------------------------------------------------------------------
# Validated input helpers
# ------------------------------------------------------------------

def get_int(prompt: str, *, lo: int = 0, hi: int = 9999) -> int:
    """Read an integer in the closed interval [lo, hi] from stdin."""
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
    """Read a positive whole-rupee amount ≥ minimum from stdin."""
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
    """Read a PIN string from stdin (plain input; masking requires OS support)."""
    return input(prompt).strip()
