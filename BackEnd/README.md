# TuteAI - AI-Powered Course Generation System

TuteAI is an intelligent course generation platform that leverages Google's Gemini AI to create structured educational content. The system enables educators, trainers, and content creators to quickly build complete courses with detailed modules, lessons, and assessments.

## 🌟 Features

- **Complete Course Planning**: Generate course outlines with customized titles, descriptions, and modules
- **Module Development**: Create detailed module plans with logical lesson sequencing
- **Lesson Content Generation**: Develop comprehensive lesson content aligned with learning objectives
- **Quiz Generation**: Automatically create assessment questions with explanations
- **API-First Architecture**: Access all functionality through a well-documented RESTful API
- **Versioned API Design**: Built for long-term extensibility and backward compatibility

## 🛠️ Technical Architecture

TuteAI follows a clean, modular architecture designed for maintainability and scalability:

### Directory Structure

```
tuteAI/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   ├── courses.py
│   │   │   │   ├── lessons.py
│   │   │   │   ├── modules.py
│   │   │   │   └── __init__.py
│   │   │   ├── router.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── models/
│   │   ├── course.py
│   │   ├── lesson.py
│   │   ├── module.py
│   │   └── __init__.py
│   ├── services/
│   │   ├── ai_service.py
│   │   └── __init__.py
│   ├── utils/
│   │   ├── id_generator.py
│   │   └── __init__.py
│   ├── config.py
│   └── __init__.py
├── main.py
├── requirements.txt
├── .env
└── README.md
```

### Key Components

1. **API Layer** (`app/api/`):
   - Versioned endpoints (v1, with architecture supporting future versions)
   - Clean separation of resource-specific routes (courses, modules, lessons)
   - Consistent error handling and response formatting

2. **Models** (`app/models/`):
   - Pydantic data models for request validation and response serialization
   - Separated by domain concern (course, module, lesson)

3. **Services** (`app/services/`):
   - AI service layer abstracting communication with Gemini AI
   - Handles prompt engineering and response processing

4. **Utils** (`app/utils/`):
   - Helper functions like ID generation

5. **Configuration** (`app/config.py`):
   - Environment-based settings management with pydantic-settings
   - Secret handling with dotenv

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Google AI API key for Gemini model access

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/tuteAI.git
   cd tuteAI
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root:
   ```
   GOOGLE_API_KEY=your-api-key-here
   ```

5. Run the application:
   ```bash
   python main.py
   ```

The API will be available at http://localhost:8000

## 📚 API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Core Endpoints

#### Course Planning
```
POST /api/v1/plan-course
```
Create a structured course outline with modules.

#### Module Planning
```
POST /api/v1/plan-module
```
Generate detailed module structure with lessons.

#### Lesson Content
```
POST /api/v1/create-lesson-content
```
Create comprehensive lesson content.

#### Quiz Generation
```
POST /api/v1/create-quiz
```
Generate assessment questions for a lesson.

## 🧠 AI Integration

TuteAI utilizes Google's Gemini 2.0 Flash model for content generation. The AI service component:

1. Formats specialized prompts based on user inputs
2. Processes responses to extract structured data
3. Handles JSON parsing and validation
4. Manages error scenarios gracefully

## 🛡️ Environment Configuration

The application uses environment variables for configuration:
- `GOOGLE_API_KEY`: Your Google AI API key
- Additional configuration parameters can be added to the `Settings` class in `config.py`

## 🌱 Future Development

TuteAI's architecture is designed for extensibility:

1. **API Versioning**: The `/api/v1` prefix allows for future API versions without breaking changes
2. **Additional AI Models**: The service layer can be extended to support multiple AI providers
3. **Content Storage**: Integration with a database for persistence
4. **User Authentication**: Role-based access control for content creators
5. **Export Formats**: Support for exporting courses to various LMS formats

## 📄 License

This project is licensed under the [Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)](https://creativecommons.org/licenses/by-nc/4.0/) - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
