import java.util.Scanner;

class BusSeat {
    private boolean isBooked;
    
    public BusSeat() {
        isBooked = false;
    }
    
    public boolean isBooked() {
        return isBooked;
    }
    
    public void bookSeat() {
        isBooked = true;
    }
    
    public void cancelBooking() {
        isBooked = false;
    }
}

class Main {
    private static BusSeat[] seats = new BusSeat[10]; // Assuming there are 10 seats
    private static Scanner scanner = new Scanner(System.in);
    private static String customerName;
    private static int availableSeats = 6; // Initially 6 available seats
    
    public static void main(String[] args) {
        System.out.println("==========================================");
        System.out.println("     Welcome to the Bus Seat Booking     ");
        System.out.println("             Website!                    ");
        System.out.println("==========================================");
        
        for (int i = 0; i < seats.length; i++) {
            seats[i] = new BusSeat();
        }
        
        while (true) {
            enterCustomerName();
            bookSeats();
            
            System.out.print("Do you want to continue booking? (yes/no): ");
            String continueBooking = scanner.next().toLowerCase();
            if (!continueBooking.equals("yes")) {
                System.out.println("==========================================");
                System.out.println("   Thank you for using the Bus Seat      ");
                System.out.println("          Booking Website!                ");
                System.out.println("==========================================");
                break;
            }
        }
        
        scanner.close();
    }
    
    private static void enterCustomerName() {
        System.out.print("Please enter your name: ");
        scanner.nextLine(); // Consume the newline left in the buffer
        customerName = scanner.nextLine();
        System.out.println("\nHello, " + customerName + "! Let's start booking your seats.");
    }
    
    private static void bookSeats() {
        while (true) {
            System.out.println("\nAvailable seats: " + availableSeats);
            
            System.out.print("Enter the number of seats you want to book, or 0 to go back: ");
            int numSeats = scanner.nextInt();
            
            if (numSeats == 0) {
                System.out.println("Returning to main menu.");
                break;
            }
            
            if (numSeats < 0) {
                System.out.println("Invalid number of seats. Please enter a positive number or 0 to go back.");
                continue;
            }
            
            if (numSeats > availableSeats) {
                System.out.println("Insufficient seats available. There are only " + availableSeats + " seats available.");
                continue;
            }
            
            int seatsBooked = 0;
            for (int i = 0; i < seats.length && seatsBooked < numSeats; i++) {
                if (!seats[i].isBooked()) {
                    seats[i].bookSeat();
                    seatsBooked++;
                    availableSeats--;
                }
            }
            
            if (seatsBooked > 0) {
                System.out.println("Booking " + seatsBooked + " seats for " + customerName + ". Seats booked successfully.");
            } else {
                System.out.println("Sorry, all selected seats are already booked.");
            }
            
            System.out.println("Returning to main menu.");
            break;
        }
    }
}
