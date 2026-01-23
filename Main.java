import java.util.Scanner;

/**
 * Simple console ATM simulation with a single account balance.
 * Supports: check balance, deposit, withdraw, and exit.
 */
public class Main {
    private static final Scanner scanner = new Scanner(System.in);
    private static double balance = 500.00; // initial balance

    public static void main(String[] args) {
        System.out.println("=================================");
        System.out.println("         Simple ATM System       ");
        System.out.println("=================================");

        boolean running = true;
        while (running) {
            printMenu();
            int choice = readInt("Choose an option: ");
            switch (choice) {
                case 1 -> showBalance();
                case 2 -> deposit();
                case 3 -> withdraw();
                case 4 -> {
                    System.out.println("Thank you for using the ATM. Goodbye!");
                    running = false;
                }
                default -> System.out.println("Invalid choice. Please try again.");
            }
            System.out.println();
        }
        scanner.close();
    }

    private static void printMenu() {
        System.out.println("1. Check Balance");
        System.out.println("2. Deposit");
        System.out.println("3. Withdraw");
        System.out.println("4. Exit");
    }

    private static void showBalance() {
        System.out.printf("Your current balance is: $%.2f%n", balance);
    }

    private static void deposit() {
        double amount = readDouble("Enter amount to deposit: ");
        if (amount <= 0) {
            System.out.println("Deposit amount must be positive.");
            return;
        }
        balance += amount;
        System.out.printf("Deposited $%.2f successfully. New balance: $%.2f%n", amount, balance);
    }

    private static void withdraw() {
        double amount = readDouble("Enter amount to withdraw: ");
        if (amount <= 0) {
            System.out.println("Withdrawal amount must be positive.");
            return;
        }
        if (amount > balance) {
            System.out.println("Insufficient funds.");
            return;
        }
        balance -= amount;
        System.out.printf("Withdrew $%.2f successfully. New balance: $%.2f%n", amount, balance);
    }

    private static int readInt(String prompt) {
        System.out.print(prompt);
        while (!scanner.hasNextInt()) {
            System.out.print("Please enter a valid number: ");
            scanner.next();
        }
        return scanner.nextInt();
    }

    private static double readDouble(String prompt) {
        System.out.print(prompt);
        while (!scanner.hasNextDouble()) {
            System.out.print("Please enter a valid amount: ");
            scanner.next();
        }
        return scanner.nextDouble();
    }
}
