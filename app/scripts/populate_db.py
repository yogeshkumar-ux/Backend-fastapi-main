import json
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson.objectid import ObjectId
import ssl

# Load courses data from JSON file
try:
    with open('courses.json') as f:
        courses = json.load(f)
    print("Courses data loaded successfully.")
except Exception as e:
    print(f"Error loading courses data: {e}")

# Connect to MongoDB Atlas
try:
    client = MongoClient(
        'mongodb+srv://ykapr17:8eztCdvhCL0LRYda@cluster1.sfl5w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1'
       
    )
    print("Connected to MongoDB Atlas.")
except Exception as e:
    print(f"Error connecting to MongoDB Atlas: {e}")

# Create or switch to the courses database
try:
    db = client['courses_db']
    print("Switched to courses_db database.")
except Exception as e:
    print(f"Error switching to database: {e}")

# Create or switch to the courses collection
try:
    courses_collection = db['courses']
    print("Switched to courses collection.")
except Exception as e:
    print(f"Error switching to collection: {e}")

# Drop the collection if it exists (for a fresh start)
try:
    courses_collection.drop()
    print("Dropped existing courses collection.")
except Exception as e:
    print(f"Error dropping collection: {e}")

# Create indices for efficient retrieval
try:
    courses_collection.create_index([('name', ASCENDING)])
    courses_collection.create_index([('date', DESCENDING)])
    courses_collection.create_index([('ratings.total', DESCENDING)])
    courses_collection.create_index([('domain', ASCENDING)])
    print("Created indices.")
except Exception as e:
    print(f"Error creating indices: {e}")

# Insert courses data into the collection
try:
    for course in courses:
        course['_id'] = ObjectId()
        if 'ratings' not in course:
            course['ratings'] = {'total': 0}
        for chapter in course.get('chapters', []):
            chapter['_id'] = ObjectId()
            if 'ratings' not in chapter:
                chapter['ratings'] = {'positive': 0, 'negative': 0}
        courses_collection.insert_one(course)
    print("Courses data inserted successfully.")
except Exception as e:
    print(f"Error inserting data: {e}")
