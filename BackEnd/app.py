# File: app.py
from flask import Flask, render_template, request, jsonify, session
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_secret_key")

# API base URL - change this to your FastAPI server URL
API_BASE_URL = "http://localhost:8000"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-course', methods=['POST'])
def generate_course():
    # Get form data
    data = {
        "title": request.form.get('title'),
        "description": request.form.get('description'),
        "target_audience": request.form.get('target_audience'),
        "time_available": request.form.get('time_available'),
        "learning_objectives": request.form.get('learning_objectives', '').split('\n') if request.form.get('learning_objectives') else None,
        "preferred_format": request.form.get('preferred_format', 'text-heavy')
    }
    
    # Call the FastAPI endpoint
    try:
        response = requests.post(f"{API_BASE_URL}/api/plan-course", json=data)
        response.raise_for_status()
        course_data = response.json()
        
        # Store in session
        session['course_data'] = course_data
        
        return jsonify({"success": True, "course": course_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/generate-module', methods=['POST'])
def generate_module():
    module_id = request.form.get('module_id')
    
    # Find the module from session
    course_data = session.get('course_data', {})
    module = next((m for m in course_data.get('modules', []) if m.get('module_id') == module_id), None)
    
    if not module:
        return jsonify({"success": False, "error": "Module not found"})
    
    data = {
        "module_title": module.get('module_title'),
        "module_summary": module.get('module_summary')
    }
    
    # Call the FastAPI endpoint
    try:
        response = requests.post(f"{API_BASE_URL}/api/plan-module", json=data)
        response.raise_for_status()
        module_data = response.json()
        
        # Store in session
        if 'modules_data' not in session:
            session['modules_data'] = {}
        session['modules_data'][module_id] = module_data
        
        return jsonify({"success": True, "module": module_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/generate-lesson', methods=['POST'])
def generate_lesson():
    lesson_id = request.form.get('lesson_id')
    module_id = request.form.get('module_id')
    
    # Find the lesson from session
    modules_data = session.get('modules_data', {})
    module_data = modules_data.get(module_id, {})
    lesson = next((l for l in module_data.get('lessons', []) if l.get('lesson_id') == lesson_id), None)
    
    if not lesson:
        return jsonify({"success": False, "error": "Lesson not found"})
    
    data = {
        "lesson_title": lesson.get('lesson_title'),
        "lesson_objective": lesson.get('lesson_objective')
    }
    
    # Call the FastAPI endpoint
    try:
        response = requests.post(f"{API_BASE_URL}/api/create-lesson", json=data)
        response.raise_for_status()
        lesson_data = response.json()
        
        # Store in session
        if 'lessons_data' not in session:
            session['lessons_data'] = {}
        session['lessons_data'][lesson_id] = lesson_data
        
        return jsonify({"success": True, "lesson": lesson_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/course')
def view_course():
    course_data = session.get('course_data')
    if not course_data:
        return "No course data found. Please generate a course first.", 404
    
    modules_data = session.get('modules_data', {})
    lessons_data = session.get('lessons_data', {})
    
    return render_template('course.html', 
                           course=course_data, 
                           modules_data=modules_data,
                           lessons_data=lessons_data)

@app.route('/export-course')
def export_course():
    course_data = session.get('course_data')
    modules_data = session.get('modules_data', {})
    lessons_data = session.get('lessons_data', {})
    
    if not course_data:
        return "No course data found. Please generate a course first.", 404
    
    # Create a full course data structure
    full_course = {
        "course": course_data,
        "modules": modules_data,
        "lessons": lessons_data
    }
    
    return jsonify(full_course)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
