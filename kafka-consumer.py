import faust
import asyncio
import websockets  # To handle WebSocket communication
import json

app = faust.App('location_stream', broker='kafka://localhost:9092')

class Location(faust.Record,serializer='json'):
    longitude: float
    latitude: float
    status: str
    projectname: str
    school_name: str

# Define the Kafka topic with the Location schema
topic = app.topic('location_topic', value_type=Location)

@app.agent(topic)
async def process_location(locations):
    async for location in locations:
        print(f"Raw message: {locations}")
        print(f"Project Name: {location.projectname}, Latitude: {location.latitude}, Longitude: {location.longitude}, Status: {location.status}, school_name: {location.school_name}")
        # Calculate status_flag based on the status
        status_flag = 1 if location.status == "submitted" else 0
        
        # Prepare data to send over WebSocket
        data = {
            'longitude': location.longitude,
            'latitude': location.latitude,
            'status_flag': status_flag,
            'project_name': location.projectname,
            'school_name': location.school_name
        }
        
        # Convert to JSON string
        json_data = json.dumps(data)
        # Call the WebSocket sending function
        await send_to_websocket(json_data)

# WebSocket handler (you will need to define the WebSocket URL and logic)
async def send_to_websocket(data):
    uri = "https://7a12-2409-40f2-208e-523b-ea5c-8914-79b7-bf39.ngrok-free.app "  # Example WebSocket URI
    try:
        async with websockets.connect(uri) as websocket:
            # Send the data as a string
            await websocket.send(str(data))
            # Optionally, receive an acknowledgment from the WebSocket server
            response = await websocket.recv()
            print(f"Received response from WebSocket: {response}")
    except Exception as e:
        print(f"WebSocket connection failed: {e}")

if __name__ == '__main__':
    app.main()
