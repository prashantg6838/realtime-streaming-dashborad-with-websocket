import streamlit as st
import pydeck as pdk
import asyncio
import websockets
import json
import threading
from queue import Queue
import time
import random
import psycopg2

# Set the page layout to 'wide'
st.set_page_config(layout="wide")

# Create a thread-safe queue for inter-thread communication
data_queue = Queue()

# List to store live feed messages
live_feed = []

# Function to connect to PostgreSQL
def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname='postgres',
            user='root',
            password='root',
            host='localhost',
            port='5432'  # Change if needed
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def get_initial_status_flag_sum():
    conn = connect_to_db()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT COALESCE(SUM(status_flag), 0) FROM status_count;")
                result = cur.fetchone()[0]
            print("Initial status_flag sum retrieved successfully.")
            return result
        except Exception as e:
            print(f"Error retrieving initial status_flag sum: {e}")
            return 0  # Return 0 in case of an error
        finally:
            conn.close()

def update_status_flag_sum(new_sum):
    conn = connect_to_db()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE status_count SET status_flag = %s;", (new_sum,))  # Correct tuple format
            conn.commit()
            print("Status flag sum updated successfully.")
        except Exception as e:
            print(f"Error updating status flag sum: {e}")
        finally:
            conn.close()

def insert_initial_status_flag(initial_value):
    conn = connect_to_db()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO status_count (status_flag) VALUES (%s);", (initial_value,))
            conn.commit()
            print("Initial status_flag inserted successfully.")
        except Exception as e:
            print(f"Error inserting initial status_flag: {e}")
        finally:
            conn.close()

initial_sum = get_initial_status_flag_sum()
if initial_sum == 0:
    insert_initial_status_flag(0)

# Function to listen to WebSocket
async def listen_to_websocket():
    uri = "ws://fd3a-2409-40f2-2094-f14d-784a-95ad-64dc-d0f2.ngrok-free.app"
    async with websockets.connect(uri) as websocket:
        while True:
            data = await websocket.recv()
            try:
                data = json.loads(data)
                data_queue.put(data)
            except json.JSONDecodeError as e:
                st.error(f"Failed to decode JSON: {e}")

# Function to start WebSocket listener in a separate thread
def start_websocket_listener():
    asyncio.run(listen_to_websocket())

# Initialize session state variables
if 'status_flag_sum' not in st.session_state:
    st.session_state.status_flag_sum = get_initial_status_flag_sum()  # Get initial sum from DB
if 'map_data' not in st.session_state:
    st.session_state.map_data = []

# Function to generate random transparent color
def random_color():
    colors = [
        [255, 0, 0, 200],     # Bright Red
        [0, 255, 0, 200],     # Bright Green
        [0, 0, 255, 200],     # Bright Blue
        [255, 255, 0, 200],   # Yellow
        [255, 165, 0, 200],   # Orange
        [255, 20, 147, 200],  # Deep Pink
        [128, 0, 128, 200],   # Purple
        [0, 255, 255, 200],   # Cyan
        [75, 0, 130, 200],    # Indigo
    ]
    return random.choice(colors)

# Function to remove bubbles and tooltips after 15 seconds
def clean_up_old_markers():
    current_time = time.time()
    st.session_state.map_data = [marker for marker in st.session_state.map_data if current_time - marker['timestamp'] < 15]

# Start WebSocket listener in a separate thread
if 'websocket_thread' not in st.session_state:
    st.session_state.websocket_thread = threading.Thread(target=start_websocket_listener)
    st.session_state.websocket_thread.start()

# Apply custom CSS to remove extra margins and padding
st.markdown("""
    <style>
        .block-container {
            padding: 0;
            margin-top: 50px;
        }
        .element-container {
            padding-left: 0 !important;
            padding-right: 0 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Split the layout into two columns (20% for the big number, 80% for the map)
col1, col2 = st.columns([0.2, 0.8])

# Placeholders for dynamic updates
status_flag_placeholder = col1.empty()
map_placeholder = col2.empty()

# Create a live chat box placeholder under the big number
with col1:
    st.markdown("<h3 style='text-align: center;'>Live Feed</h3>", unsafe_allow_html=True)
    live_feed_placeholder = st.empty()

# CSS for live chat styling (circle and message format)
st.markdown("""
    <style>
        .live-chat-box {
            max-height: 260px;
            overflow-y: auto;
            border: 1px solid #080808;
            border-radius: 10px;
            padding: 8px;
            background-color: #f9f9f9;
            width: 100%;
        }
        .live-chat-message {
            display: flex;
            align-items: flex-start;
            margin-bottom: 12px;
        }
        .avatar {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 5px;
            display: inline-block;
        }
        .message-content {
            background-color: #f4c9fd; /* Default message background color */
            padding: 8px 8px;
            max-height: 132px;
            border: 1px solid #efb0fc;
            border-radius: 12px;
            max-width: 200px;
            display: inline-block;
            position: relative;
        }
        .message-content h4 {
            margin: 0;
            color: #333;
            font-weight: bold;
            font-size: 14px;
        }
        .message-content p {
            margin: 5px 0;
            color: #666;
            font-size: 12px;
        }
        .timestamp {
            font-size: 10px;
            color: gray;
            text-align: right;
        }
        .bubble-color {
            background-color: rgba(0, 0, 255, 1); /* Replace with dynamic color */
        }
    </style>
""", unsafe_allow_html=True)

view_state = pdk.ViewState(
    latitude=20.5937,
    longitude=78.9629,
    zoom=4,
    pitch=0
)

# Main loop to poll for data
while True:
    if not data_queue.empty():
        data = data_queue.get()

        longitude = data['longitude']
        latitude = data['latitude']
        status_flag = data['status_flag']
        project_name = data.get('project_name', 'Unknown Project')
        school_name = data.get('school_name', 'N/A')

        # Generate random color
        marker_color = random_color()

        # Update status_flag_sum and store in PostgreSQL
        st.session_state.status_flag_sum += status_flag
        update_status_flag_sum(st.session_state.status_flag_sum)  # Update DB

        # Add a new marker to the map data
        st.session_state.map_data.append({
            'latitude': latitude,
            'longitude': longitude,
            'status_flag': status_flag,
            'color': marker_color,
            'project_name': project_name,
            'school_name': school_name,
            'timestamp': time.time()
        })

        current_time = time.strftime("%H:%M:%S", time.localtime())

        # Modify the live feed generation logic
        live_feed.append(f"""
            <div class='live-chat-message'>
                <span class='avatar bubble-color' style='background-color: rgba({marker_color[0]}, {marker_color[1]}, {marker_color[2]}, 1);'></span>
                <div class='message-content'>
                    <h4>Project Name: {project_name} School Name: <a href='school-details.html?school Name={school_name}' target='_blank'>{school_name}</a></h4>
                    <p>Status: {status_flag}</p>
                    <div class='timestamp'>{current_time}</div>
                </div>
            </div>
        """)

        # Limit live feed size (optional, based on your preference)
        live_feed = live_feed[:]  # Keep only the last 50 messages

    # Clean up markers older than 15 seconds
    clean_up_old_markers()

    # Update the sum of status flags
    status_flag_placeholder.markdown(f"""
        <div style='text-align: center; border: 1px solid black; padding: 5px; width: 100%; margin: 0 auto; border-radius: 10px;'>
            <p style='font-size: 20px; color: gray;'>Total Number of Submissions</p>
            <p style='font-size: 50px; font-weight: bold;'>{st.session_state.status_flag_sum}</p>
        </div>
        """, unsafe_allow_html=True)

    # Display live chat messages in ascending order (latest at bottom)
    live_feed_clean = ''.join([msg.replace('\n', '') for msg in live_feed])
    live_feed_placeholder.markdown(f"<div class='live-chat-box'>{live_feed_clean}</div>", unsafe_allow_html=True)

    # Create a Pydeck layer to display the markers
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=st.session_state.map_data,
        get_position='[longitude, latitude]',
        get_fill_color='color',
        get_radius='100',
        pickable=True,
        opacity=0.8,
        radius_min_pixels=10,
        radius_max_pixels=50,
    )

    # # Create a Pydeck deck to render the map
    # deck = pdk.Deck(
    #     layers=[layer],
    #     initial_view_state=view_state,
    #     tooltip={"text": "{project_name} | School: {school_name} | Status: {status_flag}"},
    # )
        # Create a Pydeck Layer for the markers
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=st.session_state.map_data,
        get_position='[longitude, latitude]',
        get_color='color',
        get_radius=50000,
        pickable=True,
        auto_highlight=True,
    )

    html_tooltip = """
    <b>Project Name:</b> {project_name},
    <b>School Name:</b> {school_name}
    """

    # Add HTML tooltips to markers
    for marker in st.session_state.map_data:
        marker['tooltip'] = html_tooltip.format(
            project_name=marker['project_name'],
            school_name=marker['school_name']
        )
    # Render the deck in the map placeholder
    # map_placeholder.pydeck_chart(deck)
    map_placeholder.pydeck_chart(pdk.Deck(
        layers=[scatter_layer],
        initial_view_state=view_state,
        tooltip={"html": "{tooltip}", "style": {"backgroundColor": "steelblue","color": "white"}},
        map_style='mapbox://styles/mapbox/light-v10',
        height=600
    ))

    # Sleep to control loop timing
    time.sleep(0.1)
