import pytest
from fastapi.testclient import TestClient
from bson import ObjectId
from pymongo import MongoClient
from app.main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    # Connect to MongoDB
    mongo_client = MongoClient('mongodb+srv://ykapr17:8eztCdvhCL0LRYda@cluster1.sfl5w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1')
    db = mongo_client['test_db']
    courses_collection = db['courses']

    courses_collection.delete_many({})

    # Insert sample data
    course_id = courses_collection.insert_one({
        "name": "Dynamic Course",
        "date": 1622486400,
        "description": "Description of Dynamic Course",
        "domain": ["domain3"],
        "chapters": [
            {
                "_id": ObjectId(),
                "name": "Dynamic Chapter",
                "contents": "Contents of Dynamic Chapter",
                "ratings": {"positive": 0, "negative": 0}
            }
        ],
        "ratings": {"total": 0}
    }).inserted_id

    yield {
        'courses_collection': courses_collection,
        'course_id': str(course_id)
    }

    # Teardown: Drop the test database
    mongo_client.drop_database('test_db')
    mongo_client.close()

def test_get_courses(setup_database):
    response = client.get("/courses")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0  # Assuming there is at least one course

def test_get_course_overview(setup_database):
    course_id = setup_database['course_id']
    print(f"{course_id}, ccourseiddd")
    response = client.get(f"/courses/{course_id}")
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == "Dynamic Course"

def test_get_chapter_info(setup_database):
    course_id = setup_database['course_id']
    chapter_id = setup_database['courses_collection'].find_one({
        'name': 'Dynamic Course'
    })['chapters'][0]['_id']
    response = client.get(f"/courses/{course_id}/chapters/{chapter_id}")
    assert response.status_code == 200
    data = response.json()
    assert data['name'] == "Dynamic Chapter"

def test_rate_chapter_positive(setup_database):
    course_id = setup_database['course_id']
    chapter_id = setup_database['courses_collection'].find_one({
        'name': 'Dynamic Course'
    })['chapters'][0]['_id']
    response = client.post(f"/courses/{course_id}/chapters/{chapter_id}/rate?rating=positive")
    assert response.status_code == 200
    assert response.json() == {"message": "Rating updated successfully"}

    # Verify the rating was updated
    updated_chapter = setup_database['courses_collection'].find_one({
        'name': 'Dynamic Course'
    })['chapters'][0]
    assert updated_chapter['ratings']['positive'] == 1

def test_rate_chapter_negative(setup_database):
    course_id = setup_database['course_id']
    chapter_id = setup_database['courses_collection'].find_one({
        'name': 'Dynamic Course'
    })['chapters'][0]['_id']
    response = client.post(f"/courses/{course_id}/chapters/{chapter_id}/rate?rating=negative")
    assert response.status_code == 200
    assert response.json() == {"message": "Rating updated successfully"}

    # Verify the rating was updated
    updated_chapter = setup_database['courses_collection'].find_one({
        'name': 'Dynamic Course'
    })['chapters'][0]
    assert updated_chapter['ratings']['negative'] == 1


    
