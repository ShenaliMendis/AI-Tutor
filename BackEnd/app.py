from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import requests
import json
import os
from dotenv import load_dotenv
import db_handler as db
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default-secret-key")

# FastAPI backend URL
API_URL = "http://localhost:8000"

# Initialize database
db.init_db()

# Helper function to generate a session ID
def get_or_create_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plan-course', methods=['GET', 'POST'])
def plan_course():
    if request.method == 'POST':
        # Collect form data
        course_data = {
            "title": request.form.get('title'),
            "description": request.form.get('description'),
            "target_audience": request.form.get('target_audience'),
            "time_available": request.form.get('time_available'),
            "learning_objectives": request.form.get('learning_objectives', '').split('\n'),
            "preferred_format": request.form.get('preferred_format', 'text-heavy')
        }
        
        # Clean empty items from learning objectives
        course_data["learning_objectives"] = [obj.strip() for obj in course_data["learning_objectives"] if obj.strip()]
        
        try:
            # Send to FastAPI
            response = requests.post(f"{API_URL}/api/plan-course", json=course_data)
            course_plan = response.json()
            
            # Store in database instead of session
            session_id = get_or_create_session_id()
            db.set_data(f"{session_id}_course_plan", course_plan)
            
            return redirect(url_for('view_course'))
        except Exception as e:
            flash(f"Error generating course: {str(e)}", "danger")
            return render_template('plan_course.html')
    
    return render_template('plan_course.html')

@app.route('/view-course')
def view_course():
    session_id = get_or_create_session_id()
    course_plan = db.get_data(f"{session_id}_course_plan")
    
    if not course_plan:
        flash("No course plan found. Please create a course first.", "warning")
        return redirect(url_for('plan_course'))
    
    return render_template('view_course.html', course=course_plan)

@app.route('/plan-module/<module_id>', methods=['GET', 'POST'])
def plan_module(module_id):
    session_id = get_or_create_session_id()
    course_plan = db.get_data(f"{session_id}_course_plan")
    
    if not course_plan:
        flash("No course plan found. Please create a course first.", "warning")
        return redirect(url_for('plan_course'))
    
    # Find the module
    module = None
    for m in course_plan['modules']:
        if m['module_id'] == module_id:
            module = m
            break
    
    if not module:
        flash("Module not found.", "danger")
        return redirect(url_for('view_course'))
    
    if request.method == 'POST':
        try:
            # Send to FastAPI
            module_data = {
                "module_title": module['module_title'],
                "module_summary": module['module_summary']
            }
            response = requests.post(f"{API_URL}/api/plan-module", json=module_data)
            module_plan = response.json()
            
            # Store in database instead of session
            module_plans = db.get_data(f"{session_id}_module_plans") or {}
            module_plans[module_id] = module_plan
            db.set_data(f"{session_id}_module_plans", module_plans)
            
            return redirect(url_for('view_module', module_id=module_id))
        except Exception as e:
            flash(f"Error generating module plan: {str(e)}", "danger")
    
    return render_template('plan_module.html', module=module)

@app.route('/view-module/<module_id>')
def view_module(module_id):
    session_id = get_or_create_session_id()
    course_plan = db.get_data(f"{session_id}_course_plan")
    module_plans = db.get_data(f"{session_id}_module_plans") or {}
    
    if not course_plan:
        flash("No course plan found. Please create a course first.", "warning")
        return redirect(url_for('plan_course'))
    
    # Find the module in course plan
    module = None
    for m in course_plan['modules']:
        if m['module_id'] == module_id:
            module = m
            break
    
    if not module:
        flash("Module not found.", "danger")
        return redirect(url_for('view_course'))
    
    # Get module plan if available
    module_plan = module_plans.get(module_id)
    
    return render_template('view_module.html', module=module, module_plan=module_plan)

@app.route('/create-lesson/<lesson_id>', methods=['GET', 'POST'])
def create_lesson(lesson_id):
    session_id = get_or_create_session_id()
    module_plans = db.get_data(f"{session_id}_module_plans") or {}
    
    # Find the lesson
    lesson = None
    parent_module_id = None
    
    for module_id, module_plan in module_plans.items():
        for l in module_plan['lessons']:
            if l['lesson_id'] == lesson_id:
                lesson = l
                parent_module_id = module_id
                break
        if lesson:
            break
    
    if not lesson:
        flash("Lesson not found.", "danger")
        return redirect(url_for('view_course'))
    
    if request.method == 'POST':
        try:
            # Send to FastAPI for content
            lesson_data = {
                "lesson_title": lesson['lesson_title'],
                "lesson_objective": lesson['lesson_objective']
            }
            
            # Get lesson content
            content_response = requests.post(f"{API_URL}/api/create-lesson-content", json=lesson_data)
            lesson_content = content_response.json().get('lesson_content', content_response.text)
            
            # Get quiz
            quiz_response = requests.post(f"{API_URL}/api/create-quiz", json=lesson_data)
            quiz_data = quiz_response.json()
            
            # Store in database
            lesson_contents = db.get_data(f"{session_id}_lesson_contents") or {}
            lesson_quizzes = db.get_data(f"{session_id}_lesson_quizzes") or {}
            
            lesson_contents[lesson_id] = lesson_content
            lesson_quizzes[lesson_id] = quiz_data
            
            db.set_data(f"{session_id}_lesson_contents", lesson_contents)
            db.set_data(f"{session_id}_lesson_quizzes", lesson_quizzes)
            
            flash("Lesson content successfully generated!", "success")
            return redirect(url_for('view_lesson', lesson_id=lesson_id))
        except Exception as e:
            flash(f"Error generating lesson: {str(e)}", "danger")
    
    return render_template('create_lesson.html', lesson=lesson, module_id=parent_module_id)

@app.route('/view-lesson/<lesson_id>')
def view_lesson(lesson_id):
    session_id = get_or_create_session_id()
    module_plans = db.get_data(f"{session_id}_module_plans") or {}
    lesson_contents = db.get_data(f"{session_id}_lesson_contents") or {}
    lesson_quizzes = db.get_data(f"{session_id}_lesson_quizzes") or {}
    
    # Find the lesson
    lesson = None
    parent_module_id = None
    
    for module_id, module_plan in module_plans.items():
        for l in module_plan['lessons']:
            if l['lesson_id'] == lesson_id:
                lesson = l
                parent_module_id = module_id
                break
        if lesson:
            break
    
    if not lesson:
        flash("Lesson not found.", "danger")
        return redirect(url_for('view_course'))
    
    content = lesson_contents.get(lesson_id)
    quiz = lesson_quizzes.get(lesson_id)
    
    # Ensure quiz is in the correct format expected by the template
    if quiz and not isinstance(quiz.get('quiz', []), list):
        quiz = {'quiz': []}  # Provide an empty quiz list if format is incorrect
    
    return render_template('view_lesson.html', 
                           lesson=lesson, 
                           module_id=parent_module_id, 
                           content=content, 
                           quiz=quiz)

@app.route('/export-course')
def export_course():
    session_id = get_or_create_session_id()
    course_plan = db.get_data(f"{session_id}_course_plan")
    module_plans = db.get_data(f"{session_id}_module_plans") or {}
    lesson_contents = db.get_data(f"{session_id}_lesson_contents") or {}
    lesson_quizzes = db.get_data(f"{session_id}_lesson_quizzes") or {}
    
    if not course_plan:
        flash("No course plan found. Please create a course first.", "warning")
        return redirect(url_for('plan_course'))
    
    # Create a complete course object
    full_course = {
        "course": course_plan,
        "modules": {},
        "lessons": {}
    }
    
    for module_id, module_plan in module_plans.items():
        full_course["modules"][module_id] = module_plan
        
        # Add lessons for this module
        for lesson in module_plan['lessons']:
            lesson_id = lesson['lesson_id']
            if lesson_id in lesson_contents and lesson_id in lesson_quizzes:
                full_course["lessons"][lesson_id] = {
                    "content": lesson_contents[lesson_id],
                    "quiz": lesson_quizzes[lesson_id]
                }
    
    # Convert to JSON for display
    course_json = json.dumps(full_course, indent=2)
    
    return render_template('export_course.html', course_json=course_json)

@app.route('/clear-session')
def clear_session():
    # Clear both Flask session and database session data
    session_id = session.get('session_id')
    if session_id:
        # Clear all data for this session
        db.delete_data(f"{session_id}_course_plan")
        db.delete_data(f"{session_id}_module_plans")
        db.delete_data(f"{session_id}_lesson_contents")
        db.delete_data(f"{session_id}_lesson_quizzes")
    
    session.clear()
    flash("Session cleared. You can start a new course.", "info")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
