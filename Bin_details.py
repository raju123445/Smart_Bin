import random
import time
import mysql.connector
from mysql.connector import Error

class SmartDustbin:
    def __init__(self, bin_id, division_id, capacity, db_connection):
        self.bin_id = bin_id  # Bin ID (from database)
        self.division_id = division_id  # Division ID (from database)
        self.capacity = capacity  # Maximum capacity of the dustbin
        self.current_load = 0  # Current load in the dustbin
        self.wet_waste_count = 0  # Count of wet waste items
        self.dry_waste_count = 0  # Count of dry waste items
        self.db_connection = db_connection  # Database connection

    def detect_motion(self):
        """Simulates motion detection to open the dustbin lid."""
        motion_detected = random.choice([True, False])  # Randomly decide if motion is detected
        if motion_detected:
            print(f"Bin {self.bin_id}: Motion detected: Opening dustbin lid.")
        else:
            print(f"Bin {self.bin_id}: No motion detected: Dustbin lid remains closed.")

    def segregate_waste(self):
        """Simulates waste segregation (wet vs dry)."""
        if self.current_load < self.capacity:
            waste_type = random.choice(['wet', 'dry'])  # Randomly choose wet or dry waste
            if waste_type == 'wet':
                self.wet_waste_count += 1
                print(f"Bin {self.bin_id}: Wet waste detected. Segregating and storing.")
            else:
                self.dry_waste_count += 1
                print(f"Bin {self.bin_id}: Dry waste detected. Segregating and storing.")
            self.current_load += 1
        else:
            print(f"Bin {self.bin_id}: Dustbin is full! Cannot add more waste.")

    def check_full_status(self):
        """Check if the dustbin is full."""
        if self.current_load >= self.capacity:
            print(f"Bin {self.bin_id}: The dustbin is full! Sending notification to the corporation.")
            self.send_notification()
        else:
            print(f"Bin {self.bin_id}: The dustbin is {self.capacity - self.current_load} items away from being full.")

    def send_notification(self):
        """Simulate sending a notification to the corporation with waste counts."""
        print(f"Notification sent: 'Bin {self.bin_id} full. Wet Waste: {self.wet_waste_count}, Dry Waste: {self.dry_waste_count}'")
        self.update_database_status()

    def update_database_status(self):
        """Update the dry and wet waste counts in the database."""
        try:
            cursor = self.db_connection.cursor()
            # Update the database with the new wet and dry waste counts
            update_query = """
                UPDATE division_bins
                SET Dry_waste = %s, Wet_waste = %s, Bin_status = 'Full'
                WHERE division_id = %s AND bin_id = %s;
            """
            cursor.execute(update_query, (self.dry_waste_count, self.wet_waste_count, self.division_id, self.bin_id))
            self.db_connection.commit()  # Commit the changes
            print(f"Bin {self.bin_id}: Database updated with current waste status.")
        except Error as e:
            print(f"Bin {self.bin_id}: Error while updating database: {e}")
        finally:
            cursor.close()

    def display_status(self):
        """Display the current status of the dustbin."""
        print(f"Bin {self.bin_id}: Current Load: {self.current_load}/{self.capacity}")
        print(f"Bin {self.bin_id}: Wet Waste: {self.wet_waste_count}, Dry Waste: {self.dry_waste_count}")
        print("-" * 40)

# Establish database connection
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='wms'
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

# Simulate the Smart Dustbin Management System
if __name__ == "__main__":
    # Connect to MySQL database
    db_connection = connect_to_database()
    if not db_connection:
        exit()

    # Create instances of smart dustbins for each bin
    smart_dustbins = []
    # Assume you have multiple bins across different divisions, here we initialize a few as examples
    smart_dustbins.append(SmartDustbin(bin_id=101, division_id=1, capacity=10, db_connection=db_connection))
    smart_dustbins.append(SmartDustbin(bin_id=102, division_id=1, capacity=10, db_connection=db_connection))
    smart_dustbins.append(SmartDustbin(bin_id=201, division_id=2, capacity=10, db_connection=db_connection))

    # Simulate the dustbin's operation for each bin
    for _ in range(12):  # Try adding 12 items (more than the dustbin capacity)
        for dustbin in smart_dustbins:
            time.sleep(3)  # Simulate a time delay between actions (3 seconds for testing)
            dustbin.detect_motion()  # Simulate motion detection
            dustbin.segregate_waste()  # Segregate waste
            dustbin.check_full_status()  # Check if the dustbin is full
            dustbin.display_status()  # Display the current status of the dustbin

            # If the bin is full, send notification and stop for this bin
            if dustbin.current_load >= dustbin.capacity:
                break  # Stop after sending notification for this bin

    # Close the database connection when done
    db_connection.close()
