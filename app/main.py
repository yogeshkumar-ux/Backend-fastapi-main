from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient, ASCENDING, DESCENDING
from bson import ObjectId
import re

app = FastAPI()

# Replace with your actual MongoDB connection string
client = MongoClient("mongodb+srv://ykapr17:8eztCdvhCL0LRYda@cluster1.sfl5w.mongodb.net/?retryWrites=true&w=majority&appName=Cluster1")
db = client['courses_db']
courses_collection = db['courses']

def format_course(course):
    course["_id"] = str(course["_id"])
    for chapter in course.get("chapters", []):
        chapter["_id"] = str(chapter["_id"])
        
    return course

@app.get("/courses")
def get_courses(sort: str = Query("alphabetical", enum=["alphabetical", "date", "rating"]),
                domain: str = None):
    sort_criteria = {
        "alphabetical": ("name", ASCENDING),
        "date": ("date", DESCENDING),
        "rating": ("ratings.total", DESCENDING)
    }
    query = {}
    if domain:
        query["domain"] = domain
    
    sort_field, sort_order = sort_criteria.get(sort, ("name", ASCENDING))
    
    courses = list(courses_collection.find(query).sort(sort_field, sort_order))
    formatted_courses = [format_course(course) for course in courses]
    
    return formatted_courses

@app.get("/courses/{course_id}")
def get_course_overview(course_id: str):
    if not ObjectId.is_valid(course_id):
        raise HTTPException(status_code=400, detail="Invalid course ID format")
    
    try:
        course = courses_collection.find_one({"_id": ObjectId(course_id)})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        return format_course(course)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/courses/{course_id}/chapters/{chapter_id}")
def get_chapter_info(course_id: str, chapter_id: str):
    if not ObjectId.is_valid(course_id) or not ObjectId.is_valid(chapter_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")

    try:
        course = courses_collection.find_one({"_id": ObjectId(course_id)})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        chapter = next((ch for ch in course.get("chapters", []) if ch["_id"] == ObjectId(chapter_id)), None)
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")
        
        chapter["_id"] = str(chapter["_id"])
        return chapter
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/courses/{course_id}/chapters/{chapter_id}/rate")
def rate_chapter(course_id: str, chapter_id: str, rating: str = Query(..., enum=["positive", "negative"])):
    if not ObjectId.is_valid(course_id) or not ObjectId.is_valid(chapter_id):
        raise HTTPException(status_code=400, detail="Invalid ID format")

    try:
        course = courses_collection.find_one({"_id": ObjectId(course_id)})
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        chapter = next((ch for ch in course.get("chapters", []) if ch["_id"] == ObjectId(chapter_id)), None)
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")
        
        if rating == "positive":
            chapter["ratings"]["positive"] += 1
        else:
            chapter["ratings"]["negative"] += 1

        total_rating = chapter["ratings"]["positive"] - chapter["ratings"]["negative"]

        courses_collection.update_one(
            {"_id": ObjectId(course_id), "chapters._id": ObjectId(chapter_id)},
            {
                "$set": {
                    "chapters.$.ratings": chapter["ratings"],
                    "ratings.total": total_rating
                }
            }
        )

        return {"message": "Rating updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
