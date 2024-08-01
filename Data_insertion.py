import mysql.connector

class Importing:
    def __init__(self, Table_insert, database_name):
        self.Table_insert = Table_insert
        self.database_name = database_name

        # Connect to MySQL
        self.mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            autocommit=True  # Enable autocommit
        )

        print(self.mydb)
        self.mycursor = self.mydb.cursor(buffered=True)

        # Create the database
        self.mycursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database_name}")
        self.mycursor.execute(f"USE {self.database_name}")  # Switch to the new database

        
        self.table_names = [i for i in self.Table_insert]
        print(self.table_names)

        # Create tables
        for table_name in self.table_names:
            # Escape table names with backticks to handle spaces and reserved keywords
            table_name_1 = f"`{table_name}`"
            
            # Create the table with the specified schema
            self.mycursor.execute(f"""
                CREATE TABLE {table_name_1} (
                    id INT NOT NULL AUTO_INCREMENT,
                    Bus_Operator_type VARCHAR(15),
                    BusName VARCHAR(50),
                    BusType VARCHAR(15),
                    Departing_Time TIME,
                    Duration VARCHAR(30),
                    Reaching_Time TIME,
                    Star_rating FLOAT(5),
                    Price FLOAT(5),
                    Seats_available INT(5),
                    PRIMARY KEY (id)
                )
            """)

        # Insert data into the tables
        for table_name in self.table_names:
            table_name_1 = f"`{table_name}`"
            print(f"Inserting data for table: {table_name}")
            for operator_type in ['Private', 'Government']:
                print(f"Inserting data for operator type: {operator_type}")
                try:
                    bus_name = self.Table_insert[table_name][operator_type]['Bus_Name']
                    bus_type = self.Table_insert[table_name][operator_type]['Bus_Type']
                    departing_time = self.Table_insert[table_name][operator_type]['Departing_Time']
                    duration = self.Table_insert[table_name][operator_type]['Duration']
                    reaching_time = self.Table_insert[table_name][operator_type]['Reaching_Time']
                    star_rating = self.Table_insert[table_name][operator_type]['Star_Rating']
                    price = self.Table_insert[table_name][operator_type]['Price']
                    seats_available = self.Table_insert[table_name][operator_type]['Seat_availability']
                except KeyError as e:
                    print(f"KeyError: {e} in table {table_name} for operator type {operator_type}. Skipping...")
                    continue

                
                insert_query = f"INSERT INTO {table_name_1} (Bus_Operator_type, BusName, BusType, Departing_Time, Duration, Reaching_Time, Star_rating, Price, Seats_available) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

                # Get the minimum length among the lists to avoid index errors
                value_lengths = [len(i) for i in [bus_name, bus_type, departing_time, duration, reaching_time, star_rating, price, seats_available]]
                min_length = min(value_lengths)
                print(f"Minimum length of lists: {min_length}")

                # Insert each value in the list as a separate row
                for i in range(min_length):
                    print(f"Inserting row {i+1} for {table_name} - {operator_type}")
                    print((
                        operator_type, 
                        bus_name[i], 
                        bus_type[i], 
                        departing_time[i], 
                        duration[i], 
                        reaching_time[i], 
                        star_rating[i], 
                        price[i], 
                        seats_available[i]
                    ))
                    self.mycursor.execute(insert_query, (
                        operator_type, 
                        bus_name[i], 
                        bus_type[i], 
                        departing_time[i], 
                        duration[i], 
                        reaching_time[i], 
                        star_rating[i], 
                        price[i], 
                        seats_available[i]
                    ))
                    self.mydb.commit()  # Commit after each insertion

importer = Importing(JKSRTC_Buses, "JKSRTC_Buses")
