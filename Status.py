import mysql.connector
from mysql.connector import Error

def update_bin_status(bin_id, new_status):
    try:
        # Connect to MySQL database
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='wms'
        )

        if connection.is_connected():
            print("Connected to MySQL database")

            # Validate new bin_status value
            if 0 <= new_status <= 100:
                # Update the bin_status for a specific bin_id
                update_query = """
                UPDATE division_bins
                SET bin_status = %s
                WHERE bin_id = %s;
                """
                cursor = connection.cursor()
                cursor.execute(update_query, (new_status, bin_id))
                connection.commit()

                print(f"Bin ID {bin_id} updated with new status {new_status}.")
            else:
                print("Error: bin_status must be between 0 and 100.")

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

# Example of updating a bin's status
update_bin_status(101, 50)  # Updating bin ID 1 with status 50
