from confluent_kafka import Producer
import json

producer_config = {
    'bootstrap.servers': 'localhost:9092'
}

producer = Producer(producer_config)

def delivery_report(err, msg):
    if err:
        print(f"Message failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# def produce_message():
#     message = {
#         "longitude": 77.1025,
#         "latitude": 28.7041,
#         "status": "submitted"
#     }
#     producer.produce('location_topic', key=None, value=json.dumps(message), callback=delivery_report)
#     producer.flush()

# if __name__ == "__main__":
#     produce_message()

def produce_message(message):
    producer.produce('location_topic', key=None, value=json.dumps(message), callback=delivery_report)
    producer.flush()

def read_json_file(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
        message_dict = {}
        for item in data:
            message_dict["latitude"] = item["latitude"]
            message_dict["longitude"] = item["longitude"]
            message_dict["status"] = item["status"]
            pro_name = item["solutionInformation"]
            message_dict["projectname"] = pro_name["name"]
            message_dict["school_name"] = item["school_name"]
            print(message_dict)
            produce_message(message_dict)

if __name__ == "__main__":
    file_path = "/home/user1/Documents/stremlit-dashboard/ext-js.json"  # Replace with the actual path to your JSON file
    read_json_file(file_path)