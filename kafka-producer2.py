from confluent_kafka import Producer
import json
import random
import time

# Kafka Producer Configuration
producer_config = {
    'bootstrap.servers': 'localhost:9092'  # Update with your Kafka broker address if needed
}

producer = Producer(producer_config)

# Delivery report callback function
def delivery_report(err, msg):
    if err:
        print(f"Message failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# Define bounding boxes for different regions of India
indian_city_coordinates = [
    {"state": "Delhi", "city": "New Delhi", "lat": 28.6139, "lon": 77.2090},
    {"state": "Maharashtra", "city": "Mumbai", "lat": 19.0760, "lon": 72.8777},
    {"state": "Karnataka", "city": "Bangalore", "lat": 12.9716, "lon": 77.5946},
    {"state": "Tamil Nadu", "city": "Chennai", "lat": 13.0827, "lon": 80.2707},
    {"state": "West Bengal", "city": "Kolkata", "lat": 22.5726, "lon": 88.3639},
    {"state": "Telangana", "city": "Hyderabad", "lat": 17.3850, "lon": 78.4867},
    {"state": "Rajasthan", "city": "Jaipur", "lat": 26.9124, "lon": 75.7873},
    {"state": "Uttar Pradesh", "city": "Lucknow", "lat": 26.8467, "lon": 80.9462},
    {"state": "Bihar", "city": "Patna", "lat": 25.5941, "lon": 85.1376},
    {"state": "Madhya Pradesh", "city": "Bhopal", "lat": 23.2599, "lon": 77.4126},
    {"state": "Gujarat", "city": "Gandhinagar", "lat": 23.2156, "lon": 72.6369},
    {"state": "Kerala", "city": "Thiruvananthapuram", "lat": 8.5241, "lon": 76.9366},
    {"state": "Odisha", "city": "Bhubaneswar", "lat": 20.2961, "lon": 85.8245},
    {"state": "Goa", "city": "Panaji", "lat": 15.4909, "lon": 73.8278},
    {"state": "Himachal Pradesh", "city": "Shimla", "lat": 31.1048, "lon": 77.1734},
    {"state": "Uttarakhand", "city": "Dehradun", "lat": 30.3165, "lon": 78.0322},
    {"state": "Jharkhand", "city": "Ranchi", "lat": 23.3441, "lon": 85.3096},
    {"state": "Manipur", "city": "Imphal", "lat": 24.8170, "lon": 93.9368},
    {"state": "Assam", "city": "Dispur", "lat": 26.1445, "lon": 91.7362},
    {"state": "Meghalaya", "city": "Shillong", "lat": 25.5788, "lon": 91.8933},
    {"state": "Tripura", "city": "Agartala", "lat": 23.8315, "lon": 91.2868},
    {"state": "Arunachal Pradesh", "city": "Itanagar", "lat": 27.0844, "lon": 93.6053},
    {"state": "Nagaland", "city": "Kohima", "lat": 25.6747, "lon": 94.1100},
    {"state": "Mizoram", "city": "Aizawl", "lat": 23.7271, "lon": 92.7176},
    {"state": "Chhattisgarh", "city": "Raipur", "lat": 21.2514, "lon": 81.6296},
    {"state": "Puducherry", "city": "Puducherry", "lat": 11.9416, "lon": 79.8083},
    {"state": "Chandigarh", "city": "Chandigarh", "lat": 30.7333, "lon": 76.7794}
]

project_name = ["BH_प्रोजेक्ट बेस्ड लर्निंग आधारित माइक्रो इम्प्रूवमेंट प्रोजेक्ट (2-4)","Innovative Pedagogy" ,"BR_DIET_KUMARBAG_समझ के साथ पठन कौशल का विकास",
"DIET_Samastipur_स्थानीय मान की अवधारना की समझ के लिए कक्षा- कक्ष की प्रक्रियाएं If","BR_DIET_Saran_पढ़ते चलो-बढ़ते चलो","DIET Banka_MIP_आकृतियों की दुनियाँ",
"DIET_Muzaffarpur_MIP_पठन कौशल का विकास","Cycle 3_PTM_Learning Spaces at Home","Cycle 3_Learning Shapes",
"Cycle 3_Write-a-thon","Shape Changing Table","Transversal Angles","Square and square roots","Hinge Joints",
"Explore Burning Candle","Soil Erosion Model","DIET Madhubani_DEP _MIP_आओ सीखें खेल-खेल में जोड़ -घटाव","BR_DIET_Khagaria_आओ अंग्रेजी सीखें",
"BH_DIET_Katihar_आओ स्थानीय मान के साथ संख्याओं को सीखें","DIET Siwan_कहानी-कविता के द्वारा लेखन कौशल का विकास","BH_DIET-Aurangabad 2D आकृतियों  की  पहचान" ,
"BR_DIET_Kishanganj_पठन  कौशल का विकास ","BR_DIET_Lakhisarai_आओ पढ़ना सीखे","BR_DIET_Begusarai-पाठ्य पुस्तकों की नजर से गणित","DIET_BUXAR_MIP_प्राथमिक स्तर पर पठन कौशल का विकास","DIET MADHEPURA _MIP_प्राथमिक कक्षाओं में चित्र-पठन कौशल ","BR_DIET_Gopalganj_भिन्न की समझ","DIET Purnia पठन कौशल विकास",
"DIET Bhagalpur_MIP_समझ के साथ पढ़ना","चौपाल-1","BR_DIET_Vaishali_खेलें_बोलें_सीखें","BR_DIET_Motihari_MIP_शुद्ध_सुनें, शुद्ध लिखें","मौखिक भाषा विकास की समझ के लिए कक्षा-कक्ष की प्रक्रियाएँ","BR_DIET_Sheikhpura_मौखिक भाषा का विकास","मौखिक भाषा विकास","DIET_KAIMUR_MIP_संख्या पहचान एवं तुलना","BH_प्रोजेक्ट बेस्ड लर्निंग आधारित माइक्रो इम्प्रूवमेंट प्रोजेक्ट (2-3)","प्रिंट रिच - पढ़ने का वातावरण","MIP_DIET NAWADA_गणित में स्थानीय मान की समझ",
"DIET DARBHANGA _MIP_प्राथमिक कक्षाओं में चित्र-पठन कौशल", "Cycle2_PTM_Students Dream","Cycle2_Be Ready to Measure","Cycle2_Read-a-thon",
"Herbal pesticide""Hibiscus Indicator","Fire Extiguisher Model","Prime Factorisation","Beam Balance - Mass Calibration","Quadrilaterals",
"BH_प्रोजेक्ट बेस्ड लर्निंग आधारित माइक्रो इम्प्रूवमेंट प्रोजेक्ट (2-1)","BH_प्रोजेक्ट बेस्ड लर्निंग आधारित माइक्रो इम्प्रूवमेंट प्रोजेक्ट (2-2)",
"PTM_Know Your Child & Their School","Fun with Numbers","Speak-a-thon","Operations - Multiplication and Division","Fractions - Addition and Subtraction","Linear Equations - Whole Numbers (Obs Embeded)","Food Test -Starch","Thermal Conductivity (Ghee)",
"Water Sprinkler Model","ಅಂತರಾಷ್ಟ್ರೀಯ ಯೋಗ ದಿನ 2024 International Yoga Day 2024","AP Vidyaa Pravesham - Block and district level officials_I విద్యా ప్రవేశం ఆధికారులు-I","AP Vidyaa Pravesham - Block and district level officials_II విద్యా ప్రవేశం ఆధికారులు-II",
"Vidya Pravesham School Leaders-I విద్యా ప్రవేశం పాఠశాల నాయకులు -I","Vidya Pravesham School Leaders-II విద्या ప్రవేశం పाఠశాల నాయకులు -II",
"प्रश्नावली","BH_प्रोजेक्ट बेस्ड लर्निंग आधारित माइक्रो इम्प्रूवमेंट प्रोजेक्ट - 0"]

school_name = [
    "Kendriya Vidyalaya","Jawahar Navodaya Vidyalaya","Government High School","Government Girls' School","Government Boys' School",
    "Kendriya Vidyalaya","Jawahar Navodaya Vidyalaya","Government High School","Government Girls' School","Government Boys' School",
    "Kendriya Vidyalaya","Jawahar Navodaya Vidyalaya","Government High School","Government Girls' School","Government Boys' School",
    "Kendriya Vidyalaya","Jawahar Navodaya Vidyalaya","Government High School","Government Girls' School","Government Boys' School",
    "Kendriya Vidyalaya","Jawahar Navodaya Vidyalaya","Government High School","Government Girls' School","Government Boys' School",
    "Kendriya Vidyalaya","Jawahar Navodaya Vidyalaya","Government High School","Government Girls' School","Government Boys' School",
    "Kendriya Vidyalaya","Jawahar Navodaya Vidyalaya","Government High School","Government Girls' School","Government Boys' School",
    "Kendriya Vidyalaya","Jawahar Navodaya Vidyalaya","Government High School","Government Girls' School","Government Boys' School",
    "Kendriya Vidyalaya","Jawahar Navodaya Vidyalaya","Government High School","Government Girls' School","Government Boys' School",
    "Kendriya Vidyalaya","Jawahar Navodaya Vidyalaya","Government High School","Government Girls' School","Government Boys' School"
]

# Function to select a random state's capital coordinates
def generate_random_india_coordinates():
    capital = random.choice(indian_city_coordinates)
    latitude = capital["lat"]
    longitude = capital["lon"]
    state = capital["state"]
    district = capital["city"]
    return latitude, longitude, state, district
 
# Function to produce a random message
def produce_random_message():
    latitude, longitude, state, district = generate_random_india_coordinates()
    message = {
        "longitude": longitude,  
        "latitude": latitude,
        "state" : state,
        "district" : district,    
        "status": random.choice(["submitted"]),
        "projectname": random.choice(project_name), 
        "school_name": random.choice(school_name)  
    }
    print(f"Producing message: {message}")
    producer.produce('location_topic', key=None, value=json.dumps(message), callback=delivery_report)
    producer.flush()

# Function to send random messages in intervals
def send_random_messages(interval=5):
    while True:
        produce_random_message()
        time.sleep(interval)  # Wait for 'interval' seconds before sending the next message

if __name__ == "__main__":
    send_random_messages(interval=5)  # Send messages every 5 seconds
