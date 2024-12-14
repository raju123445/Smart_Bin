import random
import time
import cv2
import mysql.connector
from mysql.connector import Error

# Load the pre-trained Haar Cascade for detecting human faces
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

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
        """Simulates motion detection using OpenCV's face detection."""
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Error: Could not access the camera.")
            return False

        print("Camera opened. Press 'q' to exit.")
        human_detected = False

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame.")
                break

            # Convert to grayscale for better detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces in the frame
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces) > 0 and not human_detected:
                print(f"Bin {self.bin_id}: Motion detected: Opening dustbin lid.")
                human_detected = True  # Set flag to prevent further detections

                # Close the camera after detecting a human
                cap.release()
                cv2.destroyAllWindows()

                time.sleep(15)  # Wait 15 seconds before checking for another detection
                return True  # Indicating motion detection was successful

            # Draw rectangles around detected faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            # Display the resulting frame
            cv2.imshow('Camera Feed', frame)

            # Exit the loop when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        return False  # No human detected, exit the loop

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
        print(f"Bin {self.bin_id}: Notification sent: 'Dustbin full. Wet Waste: {self.wet_waste_count}, Dry Waste: {self.dry_waste_count}'")
        self.update_database_status()

    def update_database_status(self):
        """Update the dry and wet waste counts in the database."""
        try:
            cursor = self.db_connection.cursor()
            update_query = """
                UPDATE division_bins
                SET Dry_waste = %s, Wet_waste = %s, Bin_status = 'Full'
                WHERE division_id = %s AND bin_id = %s;
            """
            cursor.execute(update_query, (self.dry_waste_count, self.wet_waste_count, self.division_id, self.bin_id))
            self.db_connection.commit()
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
    # List of bins to be updated
    bin_ids = [101, 102, 103, 201, 202, 203, 301, 302, 303, 401, 402, 403]
    for bin_id in bin_ids:
        # For simplicity, assume each bin has a division_id 1 for now, and a capacity of 10.
        smart_dustbins.append(SmartDustbin(bin_id=bin_id, division_id=1, capacity=10, db_connection=db_connection))

    # Simulate the dustbin's operation for each bin
    for cycle in range(12):  # Run for 12 cycles
        # Randomly select a bin for this cycle
        selected_bin = random.choice(smart_dustbins)
        print(f"\nCycle {cycle+1}: Updating bin {selected_bin.bin_id}")

        if selected_bin.detect_motion():  # If human motion is detected
            selected_bin.segregate_waste()  # Segregate waste (wet/dry)
            selected_bin.check_full_status()  # Check if the bin is full
            selected_bin.display_status()  # Display the current status of the dustbin

        # Sleep 15 seconds before the next cycle
        time.sleep(15)

    # Close the database connection when done
    db_connection.close()
