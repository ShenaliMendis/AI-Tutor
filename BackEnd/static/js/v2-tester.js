// API Endpoints for v2
const API_V2_BASE = '/api/v2';
const API_V2_ENDPOINTS = {
    planCourse: `${API_V2_BASE}/plan-course`,
    planModule: `${API_V2_BASE}/plan-module`,
    createLessonContent: `${API_V2_BASE}/create-lesson-content`,
    createQuiz: `${API_V2_BASE}/create-quiz`,
    health: `${API_V2_BASE}/health`,
    feedback: `${API_V2_BASE}/feedback`,
    exportCourse: (courseId) => `${API_V2_BASE}/export-course/${courseId}`,
    debug: `${API_V2_BASE}/debug`
};

// Store IDs for easy access
let currentCourseId = null;
let currentModuleId = null;
let currentLessonId = null;

// Helper function to format JSON
function formatJSON(json) {
    return JSON.stringify(json, null, 2);
}

// Helper function to show/hide loading indicator
function toggleLoading(elementId, show) {
    const element = document.getElementById(elementId);
    if (element) {
        element.style.display = show ? 'block' : 'none';
    }
}

// Helper function to show response container and set data
function showResponse(containerId, dataId, data) {
    const container = document.getElementById(containerId);
    const dataElement = document.getElementById(dataId);
    
    if (container && dataElement) {
        container.style.display = 'block';
        dataElement.textContent = formatJSON(data);
    }
}

// Health Check
document.getElementById('health-check-btn').addEventListener('click', async () => {
    toggleLoading('health-loading', true);
    
    try {
        const response = await fetch(API_V2_ENDPOINTS.health);
        const data = await response.json();
        
        showResponse('health-response', 'health-response-data', data);
    } catch (error) {
        console.error('Health check error:', error);
        showResponse('health-response', 'health-response-data', { error: error.message });
    } finally {
        toggleLoading('health-loading', false);
    }
});

// Course Form Submission (v2)
document.getElementById('v2-course-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    toggleLoading('v2-course-loading', true);
    document.getElementById('v2-course-response').style.display = 'none';
    
    try {
        // Parse learning objectives into array
        const learningObjectives = document.getElementById('learning-objectives').value
            .split('\n')
            .filter(obj => obj.trim() !== '');
        
        // Prepare request data
        const requestData = {
            title: document.getElementById('course-title').value,
            description: document.getElementById('course-description').value,
            target_audience: document.getElementById('target-audience').value,
            time_available: document.getElementById('time-available').value,
            learning_objectives: learningObjectives,
            preferred_format: document.getElementById('preferred-format').value,
            difficulty_level: document.getElementById('difficulty-level').value,
            content_style: document.getElementById('content-style').value,
            include_resources: true
        };
        
        console.log('Sending course request:', requestData);
        
        // Call API
        const response = await fetch(API_V2_ENDPOINTS.planCourse, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || `API error: ${response.status}`);
        }
        
        // Store course ID for later use
        currentCourseId = data.course_id;
        
        // Show course ID in the alert box
        document.getElementById('course-id-value').textContent = currentCourseId;
        document.getElementById('course-id-container').classList.remove('d-none');
        
        // Auto-fill course ID in module form
        document.getElementById('course-id').value = currentCourseId;
        
        // Display response
        showResponse('v2-course-response', 'v2-course-response-data', data);
    } catch (error) {
        console.error('Error generating course:', error);
        showResponse('v2-course-response', 'v2-course-response-data', { error: error.message });
    } finally {
        toggleLoading('v2-course-loading', false);
    }
});

// Export Course button
document.getElementById('export-course-btn').addEventListener('click', async () => {
    if (!currentCourseId) {
        alert('No course ID available. Please create a course first.');
        return;
    }
    
    try {
        const response = await fetch(API_V2_ENDPOINTS.exportCourse(currentCourseId));
        const data = await response.json();
        
        alert(`Export status: ${data.message}`);
    } catch (error) {
        console.error('Error exporting course:', error);
        alert(`Error exporting course: ${error.message}`);
    }
});

// Module Form Submission (v2)
document.getElementById('v2-module-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    toggleLoading('v2-module-loading', true);
    document.getElementById('v2-module-response').style.display = 'none';
    
    try {
        // Parse key concepts into array
        const keyConcepts = document.getElementById('key-concepts').value
            .split(',')
            .map(concept => concept.trim())
            .filter(concept => concept !== '');
        
        // Prepare request data
        const requestData = {
            course_id: document.getElementById('course-id').value,
            module_title: document.getElementById('module-title').value,
            module_summary: document.getElementById('module-summary').value,
            key_concepts: keyConcepts
        };
        
        // Call API
        const response = await fetch(API_V2_ENDPOINTS.planModule, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Store module ID for later use
        currentModuleId = data.module_id;
        
        // Show module ID in the alert box
        document.getElementById('module-id-value').textContent = currentModuleId;
        document.getElementById('module-id-container').classList.remove('d-none');
        
        // Auto-fill module ID in lesson form
        document.getElementById('module-id').value = currentModuleId;
        
        // Display response
        showResponse('v2-module-response', 'v2-module-response-data', data);
    } catch (error) {
        console.error('Error generating module:', error);
        showResponse('v2-module-response', 'v2-module-response-data', { error: error.message });
    } finally {
        toggleLoading('v2-module-loading', false);
    }
});

// Lesson Form Submission (v2)
document.getElementById('v2-lesson-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    toggleLoading('v2-lesson-loading', true);
    document.getElementById('v2-lesson-response').style.display = 'none';
    
    try {
        // Parse focus areas into array
        const focusAreas = document.getElementById('focus-areas').value
            .split(',')
            .map(area => area.trim())
            .filter(area => area !== '');
        
        // Prepare request data
        const requestData = {
            module_id: document.getElementById('module-id').value,
            lesson_title: document.getElementById('lesson-title').value,
            lesson_objective: document.getElementById('lesson-objective').value,
            focus_areas: focusAreas
        };
        
        // Call API
        const response = await fetch(API_V2_ENDPOINTS.createLessonContent, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Store lesson ID for later use
        currentLessonId = data.lesson_id;
        
        // Show lesson ID in the alert box
        document.getElementById('lesson-id-value').textContent = currentLessonId;
        document.getElementById('lesson-id-container').classList.remove('d-none');
        
        // Auto-fill lesson ID in quiz form
        document.getElementById('lesson-id').value = currentLessonId;
        
        // Display response
        showResponse('v2-lesson-response', 'v2-lesson-response-data', data);
    } catch (error) {
        console.error('Error generating lesson:', error);
        showResponse('v2-lesson-response', 'v2-lesson-response-data', { error: error.message });
    } finally {
        toggleLoading('v2-lesson-loading', false);
    }
});

// Quiz Form Submission (v2)
document.getElementById('v2-quiz-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    toggleLoading('v2-quiz-loading', true);
    document.getElementById('v2-quiz-response').style.display = 'none';
    
    try {
        // Prepare request data
        const requestData = {
            lesson_id: document.getElementById('lesson-id').value,
            difficulty_level: document.getElementById('quiz-difficulty').value,
            num_questions: parseInt(document.getElementById('num-questions').value),
            include_explanations: document.getElementById('include-explanations').checked
        };
        
        // Call API
        const response = await fetch(API_V2_ENDPOINTS.createQuiz, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Display response
        showResponse('v2-quiz-response', 'v2-quiz-response-data', data);
    } catch (error) {
        console.error('Error generating quiz:', error);
        showResponse('v2-quiz-response', 'v2-quiz-response-data', { error: error.message });
    } finally {
        toggleLoading('v2-quiz-loading', false);
    }
});

// Debug AI button
document.getElementById('debug-ai-btn').addEventListener('click', async () => {
    toggleLoading('debug-loading', true);
    
    try {
        const testPrompt = `Create a JSON response with the following structure:
{
  "course_title": "Test Course",
  "course_description": "Test description",
  "course_introduction": "Test introduction",
  "learning_outcomes": ["Outcome 1", "Outcome 2"],
  "prerequisites": ["Prerequisite 1"],
  "target_audience_description": "Test audience",
  "estimated_total_duration": "2 hours",
  "modules": [
    {
      "module_title": "Module 1",
      "module_summary": "Summary",
      "estimated_duration": "1 hour",
      "key_concepts": ["Concept 1", "Concept 2"]
    }
  ]
}`;

        // Call debug API
        const response = await fetch(API_V2_ENDPOINTS.debug, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ prompt: testPrompt })
        });
        
        const data = await response.json();
        
        showResponse('health-response', 'health-response-data', data);
    } catch (error) {
        console.error('Debug error:', error);
        showResponse('health-response', 'health-response-data', { error: error.message });
    } finally {
        toggleLoading('debug-loading', false);
    }
});
