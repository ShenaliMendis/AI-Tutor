// API Endpoints
const API_BASE = '/api/v1';
const API_V2_BASE = '/api/v2';
const API_ENDPOINTS = {
    planCourse: `${API_BASE}/plan-course`,
    planModule: `${API_BASE}/plan-module`,
    createLessonContent: `${API_BASE}/create-lesson-content`,
    createQuiz: `${API_BASE}/create-quiz`
};

const API_V2_ENDPOINTS = {
    planCourse: `${API_V2_BASE}/plan-course`,
    planModule: `${API_V2_BASE}/plan-module`,
    createLessonContent: `${API_V2_BASE}/create-lesson-content`,
    createQuiz: `${API_V2_BASE}/create-quiz`,
    health: `${API_V2_BASE}/health`,
    feedback: `${API_V2_BASE}/feedback`,
    exportCourse: (courseId) => `${API_V2_BASE}/export-course/${courseId}`
};

// Store for course data
const appState = {
    courseData: null,
    moduleData: null,
    lessonData: null,
    quizData: null,
    selectedModuleId: null,
    selectedLessonId: null,
    apiVersion: 'v1'  // Default to v1 API
};

// DOM elements
const elements = {
    workflowSteps: document.getElementById('workflow-steps'),
    stepContainers: document.querySelectorAll('.step-container'),
    
    // Course form elements
    courseForm: document.getElementById('course-form'),
    courseTitle: document.getElementById('course-title'),
    courseDescription: document.getElementById('course-description'),
    targetAudience: document.getElementById('target-audience'),
    timeAvailable: document.getElementById('time-available'),
    learningObjectives: document.getElementById('learning-objectives'),
    preferredFormat: document.getElementById('preferred-format'),
    courseLoading: document.getElementById('course-loading'),
    courseResultContainer: document.getElementById('course-result-container'),
    resultCourseTitle: document.getElementById('result-course-title'),
    resultCourseDescription: document.getElementById('result-course-description'),
    resultCourseIntroduction: document.getElementById('result-course-introduction'),
    modulesContainer: document.getElementById('modules-container'),
    
    // Module form elements
    moduleForm: document.getElementById('module-form'),
    moduleCourseTitle: document.getElementById('module-course-title'),
    moduleCourseDescription: document.getElementById('module-course-description'),
    moduleTitle: document.getElementById('module-title'),
    moduleSummary: document.getElementById('module-summary'),
    moduleLoading: document.getElementById('module-loading'),
    moduleResultContainer: document.getElementById('module-result-container'),
    resultModuleIntroduction: document.getElementById('result-module-introduction'),
    lessonsContainer: document.getElementById('lessons-container'),
    
    // Lesson form elements
    lessonForm: document.getElementById('lesson-form'),
    lessonCourseTitle: document.getElementById('lesson-course-title'),
    lessonModuleTitle: document.getElementById('lesson-module-title'),
    lessonTitle: document.getElementById('lesson-title'),
    lessonObjective: document.getElementById('lesson-objective'),
    lessonLoading: document.getElementById('lesson-loading'),
    lessonResultContainer: document.getElementById('lesson-result-container'),
    lessonContent: document.getElementById('lesson-content'),
    
    // Quiz form elements
    quizForm: document.getElementById('quiz-form'),
    quizCourseTitle: document.getElementById('quiz-course-title'),
    quizModuleTitle: document.getElementById('quiz-module-title'),
    quizLessonTitle: document.getElementById('quiz-lesson-title'),
    quizLessonObjective: document.getElementById('quiz-lesson-objective'),
    quizLoading: document.getElementById('quiz-loading'),
    quizResultContainer: document.getElementById('quiz-result-container'),
    quizQuestions: document.getElementById('quiz-questions')
};

// Handle step navigation
elements.workflowSteps.addEventListener('click', (e) => {
    e.preventDefault();
    if (e.target.tagName === 'A') {
        const stepNum = e.target.getAttribute('data-step');
        
        // Update active step in sidebar
        document.querySelectorAll('#workflow-steps a').forEach(link => {
            link.classList.remove('active');
        });
        e.target.classList.add('active');
        
        // Show active step content
        elements.stepContainers.forEach(container => {
            container.classList.remove('active');
        });
        document.getElementById(`step-${stepNum}`).classList.add('active');
    }
});

// Course Form Submission
elements.courseForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Show loading indicator
    elements.courseLoading.style.display = 'block';
    elements.courseResultContainer.style.display = 'none';
    
    try {
        // Get learning objectives as array
        const learningObjectivesArray = elements.learningObjectives.value
            ? elements.learningObjectives.value.split('\n').filter(obj => obj.trim() !== '')
            : [];
        
        // Prepare request data
        const requestData = {
            title: elements.courseTitle.value,
            description: elements.courseDescription.value,
            target_audience: elements.targetAudience.value,
            time_available: elements.timeAvailable.value,
            learning_objectives: learningObjectivesArray,
            preferred_format: elements.preferredFormat.value
        };
        
        // Call API
        const response = await fetch(API_ENDPOINTS.planCourse, {
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
        appState.courseData = data;
        
        // Display results
        elements.resultCourseTitle.textContent = data.course_title;
        elements.resultCourseDescription.textContent = data.course_description;
        elements.resultCourseIntroduction.textContent = data.course_introduction;
        
        // Display modules
        elements.modulesContainer.innerHTML = '';
        data.modules.forEach(module => {
            const moduleElement = document.createElement('div');
            moduleElement.className = 'list-group-item list-group-item-action';
            moduleElement.innerHTML = `
                <div class="d-flex w-100 justify-content-between">
                    <h5 class="mb-1">${module.module_title}</h5>
                </div>
                <p class="mb-1">${module.module_summary}</p>
                <button class="btn btn-sm btn-outline-primary mt-2 select-module" 
                    data-module-id="${module.module_id}" 
                    data-module-title="${module.module_title}" 
                    data-module-summary="${module.module_summary}">
                    Develop This Module
                </button>
            `;
            elements.modulesContainer.appendChild(moduleElement);
        });
        
        // Add event listeners to module select buttons
        document.querySelectorAll('.select-module').forEach(button => {
            button.addEventListener('click', (e) => {
                const moduleId = e.target.getAttribute('data-module-id');
                const moduleTitle = e.target.getAttribute('data-module-title');
                const moduleSummary = e.target.getAttribute('data-module-summary');
                
                // Set module data in form
                elements.moduleCourseTitle.value = data.course_title;
                elements.moduleCourseDescription.value = data.course_description;
                elements.moduleTitle.value = moduleTitle;
                elements.moduleSummary.value = moduleSummary;
                
                // Store selected module
                appState.selectedModuleId = moduleId;
                
                // Navigate to module step
                document.querySelectorAll('#workflow-steps a')[1].click();
            });
        });
        
        // Show results container
        elements.courseResultContainer.style.display = 'block';
    } catch (error) {
        console.error('Error generating course:', error);
        alert('An error occurred while generating the course. Please try again.');
    } finally {
        // Hide loading indicator
        elements.courseLoading.style.display = 'none';
    }
});

// Module Form Submission
elements.moduleForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Show loading indicator
    elements.moduleLoading.style.display = 'block';
    elements.moduleResultContainer.style.display = 'none';
    
    try {
        // Prepare request data
        const requestData = {
            course_title: elements.moduleCourseTitle.value,
            course_description: elements.moduleCourseDescription.value,
            module_title: elements.moduleTitle.value,
            module_summary: elements.moduleSummary.value
        };
        
        // Call API
        const response = await fetch(API_ENDPOINTS.planModule, {
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
        appState.moduleData = data;
        
        // Display results
        elements.resultModuleIntroduction.textContent = data.module_introduction;
        
        // Display lessons
        elements.lessonsContainer.innerHTML = '';
        data.lessons.forEach(lesson => {
            const lessonElement = document.createElement('div');
            lessonElement.className = 'list-group-item list-group-item-action';
            lessonElement.innerHTML = `
                <div class="d-flex w-100 justify-content-between">
                    <h5 class="mb-1">${lesson.lesson_title}</h5>
                </div>
                <p class="mb-1"><strong>Objective:</strong> ${lesson.lesson_objective}</p>
                <button class="btn btn-sm btn-outline-primary mt-2 select-lesson" 
                    data-lesson-id="${lesson.lesson_id}" 
                    data-lesson-title="${lesson.lesson_title}" 
                    data-lesson-objective="${lesson.lesson_objective}">
                    Create Lesson Content
                </button>
            `;
            elements.lessonsContainer.appendChild(lessonElement);
        });
        
        // Add event listeners to lesson select buttons
        document.querySelectorAll('.select-lesson').forEach(button => {
            button.addEventListener('click', (e) => {
                const lessonId = e.target.getAttribute('data-lesson-id');
                const lessonTitle = e.target.getAttribute('data-lesson-title');
                const lessonObjective = e.target.getAttribute('data-lesson-objective');
                
                // Set lesson data in form
                elements.lessonCourseTitle.value = elements.moduleCourseTitle.value;
                elements.lessonModuleTitle.value = elements.moduleTitle.value;
                elements.lessonTitle.value = lessonTitle;
                elements.lessonObjective.value = lessonObjective;
                
                // Copy to quiz form too
                elements.quizCourseTitle.value = elements.moduleCourseTitle.value;
                elements.quizModuleTitle.value = elements.moduleTitle.value;
                elements.quizLessonTitle.value = lessonTitle;
                elements.quizLessonObjective.value = lessonObjective;
                
                // Store selected lesson
                appState.selectedLessonId = lessonId;
                
                // Navigate to lesson step
                document.querySelectorAll('#workflow-steps a')[2].click();
            });
        });
        
        // Show results container
        elements.moduleResultContainer.style.display = 'block';
    } catch (error) {
        console.error('Error generating module:', error);
        alert('An error occurred while generating the module. Please try again.');
    } finally {
        // Hide loading indicator
        elements.moduleLoading.style.display = 'none';
    }
});

// Lesson Form Submission
elements.lessonForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Show loading indicator
    elements.lessonLoading.style.display = 'block';
    elements.lessonResultContainer.style.display = 'none';
    
    try {
        // Prepare request data
        const requestData = {
            course_title: elements.lessonCourseTitle.value,
            module_title: elements.lessonModuleTitle.value,
            lesson_title: elements.lessonTitle.value,
            lesson_objective: elements.lessonObjective.value
        };
        
        // Call API
        const response = await fetch(API_ENDPOINTS.createLessonContent, {
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
        appState.lessonData = data;
        
        // Display results
        elements.lessonContent.innerHTML = formatContent(data.lesson_content);
        
        // Show results container
        elements.lessonResultContainer.style.display = 'block';
    } catch (error) {
        console.error('Error generating lesson:', error);
        alert('An error occurred while generating the lesson. Please try again.');
    } finally {
        // Hide loading indicator
        elements.lessonLoading.style.display = 'none';
    }
});

// Quiz Form Submission
elements.quizForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    // Show loading indicator
    elements.quizLoading.style.display = 'block';
    elements.quizResultContainer.style.display = 'none';
    
    try {
        // Prepare request data
        const requestData = {
            course_title: elements.quizCourseTitle.value,
            module_title: elements.quizModuleTitle.value,
            lesson_title: elements.quizLessonTitle.value,
            lesson_objective: elements.quizLessonObjective.value
        };
        
        // Call API
        const response = await fetch(API_ENDPOINTS.createQuiz, {
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
        appState.quizData = data;
        
        // Display results
        elements.quizQuestions.innerHTML = '';
        
        data.quiz.forEach((question, index) => {
            const accordionItem = document.createElement('div');
            accordionItem.className = 'accordion-item';
            
            const questionId = `question-${index}`;
            const headerId = `header-${index}`;
            const collapseId = `collapse-${index}`;
            
            accordionItem.innerHTML = `
                <h2 class="accordion-header" id="${headerId}">
                    <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" 
                            data-bs-target="#${collapseId}" aria-expanded="false" aria-controls="${collapseId}">
                        ${index + 1}. ${question.question}
                    </button>
                </h2>
                <div id="${collapseId}" class="accordion-collapse collapse" 
                     aria-labelledby="${headerId}" data-bs-parent="#quiz-questions">
                    <div class="accordion-body">
                        <div class="list-group mb-3">
                            ${question.options.map(option => `
                                <div class="list-group-item ${option === question.correct_answer ? 'list-group-item-success' : ''}">
                                    ${option}
                                    ${option === question.correct_answer ? 
                                        '<span class="badge bg-success float-end">Correct Answer</span>' : ''}
                                </div>
                            `).join('')}
                        </div>
                        <div class="alert alert-info">
                            <strong>Explanation:</strong> ${question.explanation}
                        </div>
                    </div>
                </div>
            `;
            
            elements.quizQuestions.appendChild(accordionItem);
        });
        
        // Show results container
        elements.quizResultContainer.style.display = 'block';
    } catch (error) {
        console.error('Error generating quiz:', error);
        alert('An error occurred while generating the quiz. Please try again.');
    } finally {
        // Hide loading indicator
        elements.quizLoading.style.display = 'none';
    }
});

// Helper to format content with proper paragraphs and headings
function formatContent(content) {
    // Replace newlines with proper paragraph breaks
    let formatted = content
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>');
    
    // Wrap in paragraph tags if not already
    if (!formatted.startsWith('<p>')) {
        formatted = `<p>${formatted}</p>`;
    }
    
    // Format headings (assumes headings are on their own lines with patterns like "# Title")
    formatted = formatted.replace(/<p>#+\s+(.+?)<\/p>/g, '<h3>$1</h3>');
    
    // Format lists
    formatted = formatted.replace(/<p>(\s*-\s+.+?)<\/p>/g, '<ul><li>$1</li></ul>');
    formatted = formatted.replace(/<br>\s*-\s+/g, '</li><li>');
    
    // Format bold text
    formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    
    return formatted;
}
