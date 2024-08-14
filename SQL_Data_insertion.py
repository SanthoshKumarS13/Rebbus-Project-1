import mysql.connector

class Importing:
    def __init__(self, Bus_state_name, Table_insert, table_name, database_name):
        self.Bus_state_name = Bus_state_name
        self.Table_insert = Table_insert
        self.table_name = table_name
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

        # Escape table names with backticks to handle spaces and reserved keywords
        table_name_1 = f"`{self.table_name}`"

        # Create the table with the specified schema, including Bus_route_name
        self.mycursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name_1} (
                id INT NOT NULL AUTO_INCREMENT,
                Bus_state_name VARCHAR(100),
                Bus_route_name VARCHAR(100),
                Bus_Operator_type VARCHAR(15),
                BusName VARCHAR(50),
                BusType VARCHAR(50),
                Departing_Time TIME,
                Duration VARCHAR(30),
                Reaching_Time TIME,
                Star_rating FLOAT(5),
                Price FLOAT(10),
                Seats_available INT(5),
                PRIMARY KEY (id)
            )
        """)

        # Insert data into the table
        for bus_route_name, operator_data in self.Table_insert.items():
            for operator_type in ['Private', 'Government']:
                print(f"Inserting data for operator type: {operator_type} on route: {bus_route_name}")
                try:
                    bus_name = operator_data[operator_type]['Bus_Name']
                    bus_type = operator_data[operator_type]['Bus_Type']
                    departing_time = operator_data[operator_type]['Departing_Time']
                    duration = operator_data[operator_type]['Duration']
                    reaching_time = operator_data[operator_type]['Reaching_Time']
                    star_rating = operator_data[operator_type]['Star_Rating']
                    price = operator_data[operator_type]['Price']
                    seats_available = operator_data[operator_type]['Seat_availability']
                except KeyError as e:
                    print(f"KeyError: {e} in route {bus_route_name} for operator type {operator_type}. Skipping...")
                    continue

                insert_query = f"INSERT INTO {table_name_1} (Bus_state_name, Bus_route_name, Bus_Operator_type, BusName, BusType, Departing_Time, Duration, Reaching_Time, Star_rating, Price, Seats_available) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"

                # Get the minimum length among the lists to avoid index errors
                value_lengths = [len(i) for i in [bus_name, bus_type, departing_time, duration, reaching_time, star_rating, price, seats_available]]
                min_length = min(value_lengths)
                print(f"Minimum length of lists: {min_length}")

                # Insert each value in the list as a separate row
                for i in range(min_length):
                    print(f"Inserting row {i+1} for {bus_route_name} - {operator_type}")
                    print((
                        self.Bus_state_name,
                        bus_route_name,
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
                        self.Bus_state_name,
                        bus_route_name,
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

#Inputing the arguments State bus name,Variable containing scraped data,Table name,Database name
importer = Importing('WBSTC-West Bengal State Transport',WBSTC, "Bus_Data", "RedBus")
