import sqlite3
import json
import os
from contextlib import contextmanager
import uuid

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'aitutor.db')

# Create database tables if they don't exist
def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            introduction TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS modules (
            id TEXT PRIMARY KEY,
            course_id TEXT NOT NULL,
            title TEXT NOT NULL,
            summary TEXT NOT NULL,
            introduction TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS lessons (
            id TEXT PRIMARY KEY,
            module_id TEXT NOT NULL,
            title TEXT NOT NULL,
            objective TEXT NOT NULL,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (module_id) REFERENCES modules (id)
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id TEXT PRIMARY KEY,
            lesson_id TEXT NOT NULL,
            quiz_data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lesson_id) REFERENCES lessons (id)
        )
        ''')
        
        conn.commit()

# Database connection context manager
@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    try:
        yield conn
    finally:
        conn.close()

# Generate a unique ID
def generate_id(prefix=""):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

# Course operations
def save_course(course_data):
    course_id = course_data.get('course_id', generate_id('course'))
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO courses (id, title, description, introduction) VALUES (?, ?, ?, ?)',
            (
                course_id,
                course_data['course_title'],
                course_data['course_description'],
                course_data['course_introduction']
            )
        )
        
        # Save modules
        for module in course_data['modules']:
            module_id = module.get('module_id', generate_id('mod'))
            cursor.execute(
                'INSERT OR REPLACE INTO modules (id, course_id, title, summary) VALUES (?, ?, ?, ?)',
                (
                    module_id,
                    course_id,
                    module['module_title'],
                    module['module_summary']
                )
            )
            # Update module with ID if it doesn't have one
            if 'module_id' not in module:
                module['module_id'] = module_id
        
        conn.commit()
    
    # Update the course data with the course_id
    course_data['course_id'] = course_id
    return course_data

def get_course(course_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get course info
        cursor.execute('SELECT * FROM courses WHERE id = ?', (course_id,))
        course = cursor.fetchone()
        
        if not course:
            return None
        
        # Get modules
        cursor.execute('SELECT * FROM modules WHERE course_id = ?', (course_id,))
        modules = cursor.fetchall()
        
        # Convert Row objects to dictionaries
        course_dict = dict(course)
        modules_list = []
        
        for module in modules:
            module_dict = dict(module)
            modules_list.append({
                'module_id': module_dict['id'],
                'module_title': module_dict['title'],
                'module_summary': module_dict['summary']
            })
        
        # Format the course data to match the expected structure
        return {
            'course_id': course_dict['id'],
            'course_title': course_dict['title'],
            'course_description': course_dict['description'],
            'course_introduction': course_dict['introduction'],
            'modules': modules_list
        }

# Module operations
def save_module_plan(module_id, module_plan):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Update module with introduction
        cursor.execute(
            'UPDATE modules SET introduction = ? WHERE id = ?',
            (module_plan['module_introduction'], module_id)
        )
        
        # Save lessons
        for lesson in module_plan['lessons']:
            lesson_id = lesson.get('lesson_id', generate_id('les'))
            cursor.execute(
                'INSERT OR REPLACE INTO lessons (id, module_id, title, objective) VALUES (?, ?, ?, ?)',
                (
                    lesson_id,
                    module_id,
                    lesson['lesson_title'],
                    lesson['lesson_objective']
                )
            )
            # Update lesson with ID if it doesn't have one
            if 'lesson_id' not in lesson:
                lesson['lesson_id'] = lesson_id
        
        conn.commit()
    
    return module_plan

def get_module(module_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get module info
        cursor.execute('SELECT * FROM modules WHERE id = ?', (module_id,))
        module = cursor.fetchone()
        
        if not module:
            return None, None
        
        # Get lessons for this module
        cursor.execute('SELECT * FROM lessons WHERE module_id = ?', (module_id,))
        lessons = cursor.fetchall()
        
        # Convert Row objects to dictionaries
        module_dict = dict(module)
        
        # Get the basic module info
        basic_module = {
            'module_id': module_dict['id'],
            'module_title': module_dict['title'],
            'module_summary': module_dict['summary']
        }
        
        # If introduction exists, create the full module plan
        if module_dict['introduction']:
            lessons_list = []
            
            for lesson in lessons:
                lesson_dict = dict(lesson)
                lessons_list.append({
                    'lesson_id': lesson_dict['id'],
                    'lesson_title': lesson_dict['title'],
                    'lesson_objective': lesson_dict['objective']
                })
                
            module_plan = {
                'module_introduction': module_dict['introduction'],
                'lessons': lessons_list
            }
            
            return basic_module, module_plan
        
        return basic_module, None

# Lesson operations
def save_lesson_content(lesson_id, content):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE lessons SET content = ? WHERE id = ?',
            (content, lesson_id)
        )
        conn.commit()

def get_lesson(lesson_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get lesson
        cursor.execute('SELECT * FROM lessons WHERE id = ?', (lesson_id,))
        lesson = cursor.fetchone()
        
        if not lesson:
            return None, None, None
        
        # Get module for this lesson
        cursor.execute('SELECT * FROM modules WHERE id = ?', (lesson['module_id'],))
        module = cursor.fetchone()
        
        # Get quiz if exists
        cursor.execute('SELECT * FROM quizzes WHERE lesson_id = ?', (lesson_id,))
        quiz = cursor.fetchone()
        
        lesson_dict = dict(lesson)
        module_id = module['id'] if module else None
        
        lesson_info = {
            'lesson_id': lesson_dict['id'],
            'lesson_title': lesson_dict['title'],
            'lesson_objective': lesson_dict['objective']
        }
        
        content = lesson_dict['content']
        
        quiz_data = None
        if quiz:
            quiz_data = json.loads(quiz['quiz_data'])
        
        return lesson_info, module_id, content, quiz_data

# Quiz operations
def save_quiz(lesson_id, quiz_data):
    quiz_id = generate_id('quiz')
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO quizzes (id, lesson_id, quiz_data) VALUES (?, ?, ?)',
            (
                quiz_id,
                lesson_id,
                json.dumps(quiz_data)
            )
        )
        conn.commit()

# Export course data
def export_course_data(course_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get course
        cursor.execute('SELECT * FROM courses WHERE id = ?', (course_id,))
        course = cursor.fetchone()
        
        if not course:
            return None
        
        # Get modules
        cursor.execute('SELECT * FROM modules WHERE course_id = ?', (course_id,))
        modules = cursor.fetchall()
        
        # Build the full course object
        course_dict = dict(course)
        
        full_course = {
            "course": {
                "course_id": course_dict['id'],
                "course_title": course_dict['title'],
                "course_description": course_dict['description'],
                "course_introduction": course_dict['introduction'],
                "modules": []
            },
            "modules": {},
            "lessons": {}
        }
        
        # Add modules
        for module in modules:
            module_dict = dict(module)
            module_id = module_dict['id']
            
            # Add basic module info to course
            full_course["course"]["modules"].append({
                "module_id": module_id,
                "module_title": module_dict['title'],
                "module_summary": module_dict['summary']
            })
            
            # Get lessons for this module
            cursor.execute('SELECT * FROM lessons WHERE module_id = ?', (module_id,))
            lessons = cursor.fetchall()
            
            if module_dict['introduction']:
                lesson_list = []
                
                for lesson in lessons:
                    lesson_dict = dict(lesson)
                    lesson_list.append({
                        "lesson_id": lesson_dict['id'],
                        "lesson_title": lesson_dict['title'],
                        "lesson_objective": lesson_dict['objective']
                    })
                
                # Add module plan to modules
                full_course["modules"][module_id] = {
                    "module_introduction": module_dict['introduction'],
                    "lessons": lesson_list
                }
                
                # Add lessons
                for lesson in lessons:
                    lesson_dict = dict(lesson)
                    lesson_id = lesson_dict['id']
                    
                    if lesson_dict['content']:
                        # Get quiz
                        cursor.execute('SELECT * FROM quizzes WHERE lesson_id = ?', (lesson_id,))
                        quiz = cursor.fetchone()
                        
                        lesson_data = {
                            "content": lesson_dict['content']
                        }
                        
                        if quiz:
                            lesson_data["quiz"] = json.loads(quiz['quiz_data'])
                        
                        full_course["lessons"][lesson_id] = lesson_data
        
        return full_course
