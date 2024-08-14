import streamlit as st
import mysql.connector
import pandas as pd

# MySQL connection setup
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    autocommit=True
)

mycursor = mydb.cursor(buffered=True)

# Fetch list of databases
mycursor.execute("USE Redbus")

# Streamlit UI
st.set_page_config(layout='centered')
st.title("Welcome to Bus Selector 🚎🚎")

# Custom CSS for styling and hiding slider labels
st.markdown(
    """
    <style>
    .sidebar .sidebar-content {
        background-color: #004E64;
        color: #FFFFFF;
        border-right: 2px solid #25A18E;
    }
    .stSelectbox {
        background-color: Orange;
        color: #fb6107;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .stSelectbox label {
        color: #1f2421;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #25A18E;
        transform: scale(1.05);
    }
    .stDataFrame, .stTable {
        background-color: #E5FFF6;
        color: #004E64;
        border: 3px solid #004E64;
        border-radius:4px;
        margin-top: 20px;
    }
    .stSlider .stSliderLabel {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar for database and table selection
with st.sidebar:
    mycursor.execute(f"SELECT DISTINCT Bus_state_name FROM bus_data")
    State_transport = [state[0] for state in mycursor.fetchall()]
    State_transport = st.selectbox("Select State Transport", State_transport)
    if State_transport:
        mycursor.execute(f"SELECT DISTINCT Bus_route_name FROM bus_data WHERE Bus_state_name = '{State_transport}'")
        Bus_route = [route[0] for route in mycursor.fetchall()]
        Bus_route = st.selectbox("Select Bus route", Bus_route)
        if Bus_route:
            mycursor.execute(f"SELECT DISTINCT Bus_Operator_type FROM bus_data WHERE Bus_route_name = '{Bus_route}'")
            Select_operator_Type = [operator_type[0] for operator_type in mycursor.fetchall()]
            Select_operator_Type.insert(0, "Both")
            Select_operator_Type = st.selectbox("Bus Operator Types", Select_operator_Type, index=0)

# Main content
if State_transport and Bus_route and Select_operator_Type:
    mycursor.execute(f"SELECT DISTINCT BusName FROM bus_data WHERE Bus_route_name = '{Bus_route}' AND Bus_Operator_type = '{Select_operator_Type}'")
    Name = [column[0] for column in mycursor.fetchall()]
    Name.insert(0, "Default")  # Add "Default" option to select all
    Select_operator_Name = st.selectbox("Bus Name", Name, key="bus_name", index=0)

    # Fetch bus types based on selected operator type
    mycursor.execute(f"SELECT DISTINCT BusType FROM bus_data WHERE Bus_route_name = '{Bus_route}' AND Bus_Operator_type = '{Select_operator_Type}'")
    Type = [column[0] for column in mycursor.fetchall()]
    Type.insert(0, "Default")  # Add "Default" option to select all
    Select_Bus_Type = st.selectbox("Bus Comfort Type", Type, key="bus_type", index=0)

    # Fetch star ratings
    mycursor.execute(f"SELECT Star_rating FROM bus_data WHERE Bus_route_name = '{Bus_route}' AND Bus_Operator_type = '{Select_operator_Type}'")
    Star_Rating = st.slider("Ratings", min_value=0.0, max_value=5.0, step=0.1, value=(0.0, 5.0), key="star_rating")

    # Fetch price range
    mycursor.execute(f"SELECT Price FROM bus_data WHERE Bus_route_name = '{Bus_route}' AND Bus_Operator_type = '{Select_operator_Type}'")
    Price = st.slider("Price Range", min_value=0, max_value=5000, step=50, value=(0, 5000), key="price")

    # Fetch seats available
    mycursor.execute(f"SELECT Seats_available FROM bus_data WHERE Bus_route_name = '{Bus_route}' AND Bus_Operator_type = '{Select_operator_Type}'")
    Seats_available = st.slider("Seats Available", min_value=0, max_value=60, step=3, value=(0, 60), key="seats_available")

    # Fetch data based on selected filters
    with st.spinner('Fetching data...'):
        query_conditions = []
        if Select_operator_Name != "Default":
            query_conditions.append(f"BusName = '{Select_operator_Name}'")
        if Select_Bus_Type != "Default":
            query_conditions.append(f"BusType = '{Select_Bus_Type}'")
        
        query_conditions.append(f"Star_rating BETWEEN {Star_Rating[0]} AND {Star_Rating[1]}")
        query_conditions.append(f"Price BETWEEN {Price[0]} AND {Price[1]}")
        query_conditions.append(f"Seats_available BETWEEN {Seats_available[0]} AND {Seats_available[1]}")
        
        if Select_operator_Type != "Both":
            query_conditions.append(f"Bus_Operator_type = '{Select_operator_Type}'")
        
        query = f"""
        SELECT *, DATE_FORMAT(Departing_Time, '%H:%i:%s') AS Departing_Time_, DATE_FORMAT(Reaching_Time, '%H:%i:%s') AS Reaching_Time_ 
        FROM bus_data
        WHERE Bus_route_name = '{Bus_route}' AND {' AND '.join(query_conditions)}
        """
        
        mycursor.execute(query)
        data = mycursor.fetchall()
        columns = mycursor.column_names
        
        # Convert data to DataFrame without index
        df = pd.DataFrame(data, columns=columns)
        
        # Drop old columns
        df.drop(['Departing_Time', 'Reaching_Time'], axis=1, inplace=True)
        
        # Set 'id' column as the index
        df.set_index('id', inplace=True)

        # Display data without index
        st.write(f"Buses from {Bus_route} are")
        st.dataframe(df)
