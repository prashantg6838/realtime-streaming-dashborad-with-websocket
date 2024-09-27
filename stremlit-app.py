import streamlit as st
import pydeck as pdk
import asyncio
import websockets
import json
import threading
from queue import Queue
import time
import random

# Set the page layout to 'wide'
st.set_page_config(layout="wide")

# Create a thread-safe queue for inter-thread communication
data_queue = Queue()

# List to store live feed messages
live_feed = []

# Function to listen to WebSocket
async def listen_to_websocket():
    uri = "wss://7a12-2409-40f2-208e-523b-ea5c-8914-79b7-bf39.ngrok-free.app "
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
    st.session_state.status_flag_sum = 0
if 'map_data' not in st.session_state:
    st.session_state.map_data = []

# Function to generate random transparent color
# def random_color():
#     return [random.randint(0, 100), random.randint(0, 100), random.randint(0, 100), 200]
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

# CSS for live chat styling
st.markdown("""
    <style>
        .live-chat-box {
            max-height: 250px;
            overflow-y: auto;
            border: 1px solid #ccc;
            border-radius: 10px;
            padding: 8px;
            background-color: #f9f9f9;
            width: 100%;
        }
        .live-chat-message {
            padding: 4px;
            margin-bottom: 8px;
            border-bottom: 1px solid #ddd;
            font-size: 14px;
        }
        .live-chat-message h4 {
            margin: 0;
            color: #333;
            font-weight: bold;
            font-size: 14px;
        }
        .live-chat-message p {
            margin: 5px 0;
            color: #666;
            font-size: 12px;
        }
        .bubble {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        .timestamp {
            font-size: 10px;
            color: gray;
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

        # Update status_flag_sum
        st.session_state.status_flag_sum += status_flag

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

        # Add to the live feed with a bubble representing the marker color
        live_feed.append(f"""
            <div class='live-chat-message'>
                <span class='bubble' style='background-color: rgba({marker_color[0]}, {marker_color[1]}, {marker_color[2]}, 1);'></span>
                <h4>Project: {project_name}, School: {school_name}</h4>
                <p>Status: {status_flag}</p>
                <span class='timestamp'>{current_time}</span>
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

    # Create a Pydeck Deck with updated markers and tooltips
    map_placeholder.pydeck_chart(pdk.Deck(
        layers=[scatter_layer],
        initial_view_state=view_state,
        tooltip={"html": "{tooltip}", "style": {"backgroundColor": "steelblue","color": "white"}},
        map_style='mapbox://styles/mapbox/light-v10',
        height=600
    ))
    time.sleep(1)
