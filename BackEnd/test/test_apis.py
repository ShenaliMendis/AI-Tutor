import requests
import json
import time

# Base URL of the FastAPI server
BASE_URL = "http://localhost:8000"

def test_plan_course():
    print("Testing /api/plan-course...")
    payload = {
        "title": "Introduction to Python Programming",
        "description": "A beginner-friendly course to learn Python programming.",
        "target_audience": "Beginners with no prior programming experience",
        "time_available": "4 weeks, 2 hours per week",
        "learning_objectives": [
            "Understand Python basics",
            "Write simple Python scripts",
            "Learn about data types and control structures"
        ],
        "preferred_format": "text-heavy"
    }
    response = requests.post(f"{BASE_URL}/api/plan-course", json=payload)
    print("Response:", response.status_code, response.json())
    # save response to a file
    with open("course_plan.json", "w") as f:
        json.dump(response.json(), f, indent=4)
    print("Course plan saved to course_plan.json")

def test_plan_module():
    print("Testing /api/plan-module...")
    payload = {
        "module_title": "Python Basics",
        "module_summary": "Learn the fundamentals of Python programming, including syntax and basic concepts."
    }
    response = requests.post(f"{BASE_URL}/api/plan-module", json=payload)
    print("Response:", response.status_code, response.json())
    # save response to a file
    with open("module_plan.json", "w") as f:
        json.dump(response.json(), f, indent=4)
    print("Module plan saved to module_plan.json")

def test_create_lesson_content():
    print("Testing /api/create-lesson-content...")
    payload = {
        "lesson_title": "Data Types in Python",
        "lesson_objective": "Understand different data types in Python and their usage."
    }
    response = requests.post(f"{BASE_URL}/api/create-lesson-content", json=payload)
    print("Response:", response.status_code)
    print("Lesson Content (Markdown):\n")
    print(response.text)
    
    try:
        response_data = response.json()
        with open("lesson_content.md", "w") as f:
            f.write(response_data.get("lesson_content", ""))
    except json.JSONDecodeError:
        print("Failed to decode JSON response.")

def test_create_quiz():
    print("Testing /api/create-quiz...")
    payload = {
        "lesson_title": "Data Types in Python",
        "lesson_objective": "Understand different data types in Python and their usage."
    }
    response = requests.post(f"{BASE_URL}/api/create-quiz", json=payload)
    print("Response:", response.status_code, response.json())
    with open("quiz.json", "w") as f:
        json.dump(response.json(), f, indent=4)

if __name__ == "__main__":
    print("Starting API tests...")
    test_plan_course()
    time.sleep(30)

    test_plan_module()
    time.sleep(30)

    test_create_lesson_content()
    time.sleep(30)

    test_create_quiz()
    print("API tests completed.")