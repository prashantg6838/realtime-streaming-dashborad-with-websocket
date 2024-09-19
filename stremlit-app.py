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

# Function to listen to WebSocket
async def listen_to_websocket():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        while True:
            data = await websocket.recv()
            
            # Print raw data for debugging
            print(f"Raw WebSocket data: {data}")
            
            try:
                # Attempt to decode JSON
                data = json.loads(data)
                
                # Put the data in the queue
                data_queue.put(data)
                
            except json.JSONDecodeError as e:
                st.error(f"Failed to decode JSON: {e}")
                print(f"JSONDecodeError: {e}")

# Function to start WebSocket listener in a separate thread
def start_websocket_listener():
    asyncio.run(listen_to_websocket())

# Initialize session state variables
if 'status_flag_sum' not in st.session_state:
    st.session_state.status_flag_sum = 0
if 'map_data' not in st.session_state:
    st.session_state.map_data = []

# Function to generate random transparent color
def random_color():
    return [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), random.randint(50, 150)]  # Transparency between 50-150

# Function to remove bubbles and tooltips after 12 seconds
def clean_up_old_markers():
    current_time = time.time()
    st.session_state.map_data = [marker for marker in st.session_state.map_data if current_time - marker['timestamp'] < 12]

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

# Initial Map Configuration
view_state = pdk.ViewState(latitude=20.5937, longitude=78.9629, zoom=5)

# Main loop to poll for data
while True:
    if not data_queue.empty():
        data = data_queue.get()
        
        # Extract data from the JSON
        longitude = data['longitude']
        latitude = data['latitude']
        status_flag = data['status_flag']
        project_name = data.get('project_name', 'Unknown Project')  # Extract project name
        school_name = data.get('school_name', 'N/A')
        
        # Update status_flag_sum
        st.session_state.status_flag_sum += status_flag
        
        # Add a new marker (bubble) to the data with a random color and timestamp
        st.session_state.map_data.append({
            'latitude': latitude,
            'longitude': longitude,
            'status_flag': status_flag,
            'color': random_color(),
            'project_name': project_name,
            'school_name': school_name,
            'timestamp': time.time()
        })
    
    # Clean up markers older than 12 seconds
    clean_up_old_markers()
    
    # Update the sum of status flags with a heading and big number
    status_flag_placeholder.markdown(f"""
        <div style='text-align: center; border: 1px solid black; padding: 5px; width: 100%; margin: 0 auto; border-radius: 10px;'>
            <p style='font-size: 24px; color: gray;'>Total Number of Submissions</p>
            <p style='font-size: 80px; font-weight: bold;'>{st.session_state.status_flag_sum}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Create a Pydeck Layer for the markers with random transparent colors
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=st.session_state.map_data,
        get_position='[longitude, latitude]',
        get_color='color',  # Use the random color for each bubble
        get_radius=20000,  # Adjust the size of the markers
        pickable=True,
        auto_highlight=True,
        tooltip=True
    )
    
    # Create an HTML tooltip for project details (similar to the popup box)
    html_tooltip = """
    <div style="background-color:white; padding:10px; border-radius:5px; width:220px;">
        <h4 style="margin:0; padding-bottom: 10px; color: #1a73e8; font-size: 16px;">Project Name: {project_name}</h4>
        <h4 style="margin:0; padding-bottom: 10px; color: #1a73e8; font-size: 16px;">School Name: {school_name}</h4>
    </div>
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
        tooltip={"html": "{tooltip}", "style": {"color": "white", "backgroundColor": "black"}},
        height=600
    ))
    
    # Sleep briefly to allow the Streamlit app to update
    time.sleep(1)
