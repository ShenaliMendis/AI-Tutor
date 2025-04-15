# Course Generation System

A system that uses Google Generative AI to automatically generate course content based on user inputs.

## Features

- Generate complete course outlines with modules and lessons
- Create detailed lesson content with quizzes
- Simple UI for course generation and viewing
- Export courses as JSON for use in other systems

## Setup

### Prerequisites

- Python 3.8+
- Google Generative AI API Key (from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd course-generation-system
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API key:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   FLASK_SECRET_KEY=your_flask_secret_key_here
   ```

## Running the Application

1. Start the FastAPI backend:
   ```
   python main.py
   ```
   This will start the API server at http://localhost:8000.

2. In a separate terminal, start the Flask frontend:
   ```
   python app.py
   ```
   This will start the web interface at http://localhost:5000.

3. Open your browser and navigate to http://localhost:5000 to use the system.

## API Endpoints

The system provides the following API endpoints:

- `POST /api/plan-course`: Generate a course outline with modules
- `POST /api/plan-module`: Generate module details with lessons
- `POST /api/create-lesson-content`: Generate lesson content for a given lesson
- `POST /api/create-quiz`: Generate a quiz for a given lesson

## For Testing

To run the tests, execute the `test/test_apis.py` file. This will send requests to the API endpoints and print the responses.
   ```
   python test/test_apis.py
   ```

## System Architecture

- **FastAPI Backend**: Handles API requests and communicates with Google Generative AI
- **Flask Frontend**: Provides a user interface for interacting with the system
- **Google Generative AI**: Powers the content generation using Gemini model


## Project Structure

Here's the project structure you should have after implementing all the files:

```
course-generation-system/
├── .env                  # Environment variables (API keys)
├── app.py                # Flask frontend application
├── main.py               # FastAPI backend application
├── run.py                # Script to run both services
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
├── templates/            # HTML templates
│   ├── index.html        # Course generation form
│   └── course.html       # Course viewer page
├── test/                 # Test scripts
│   └── test_apis.py      # API tests
```

## How to Use the System

1. **Setup**:
   - Install the dependencies using `pip install -r requirements.txt`
   - Create a `.env` file with your Google Generative AI API key and Flask secret key
   - Make sure both keys are properly set

2. **Running the System**:
   - Use the `run.py` script: `python run.py`
   - Or start the services separately:
     - FastAPI backend: `python main.py`
     - Flask frontend: `python app.py`

3. **Using the System**:
   - Open your browser and go to `http://localhost:5000`
   - Fill out the course generation form with:
     - Course title/description
     - Target audience
     - Time available
     - Learning objectives (optional)
     - Preferred format
   - Click "Generate Course" to create the course outline
   - Generate module details and lesson content as needed
   - View the full course structure with all generated content
   - Export the course as JSON for use in other systems

The system follows a hierarchical approach to course generation:
1. First, generate the course structure with modules
2. Then generate each module's details with lessons
3. Finally, generate content for individual lessons with quizzes

This approach allows for incremental generation and reduces the load on the API, making the system more responsive and efficient.

## Future Enhancements

As mentioned in your original document, there are several ways to enhance this system:

1. **Review and feedback mechanism**: Add an AI-powered review system to evaluate course content
2. **Export formats**: Add support for exporting to PDF, DOCX, or LMS-compatible formats
3. **Personalization**: Adapt content based on learning styles or user preferences
4. **Multilingual support**: Add translation capabilities for global audiences
5. **Advanced analytics**: Track course effectiveness and user engagement

Let me know if you'd like me to explain any part of the system in more detail or if you need help implementing any specific feature!

## Extending the System

You can extend this system by:

1. Adding more API endpoints for additional functionality:
   - Review and feedback generation
   - Exporting to different formats (PDF, DOCX, etc.)
   - User progress tracking

2. Improving prompt engineering for better content generation:
   - Domain-specific prompts for different subjects
   - Different learning styles (visual, hands-on, etc.)
   - Adjusting content complexity based on audience

3. Adding authentication and user management:
   - User accounts to save courses
   - Sharing and collaboration features
   - Analytics on course generation and usage

## License

This project is licensed under the [CC BY-NC 4.0 License](LICENSE).