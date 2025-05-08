import 'package:flutter/material.dart';
import 'package:ai_tutor/quiz/result.dart';
import 'dart:convert';

void main() {
  runApp(const HexaEliteApp());
}

class HexaEliteApp extends StatelessWidget {
  const HexaEliteApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'HexaElite AI Tutor',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        fontFamily: 'Roboto',
      ),
      home: const HexaEliteTutorPage(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class Question {
  final int id;
  final String text;
  final List<String> options;
  
  const Question({
    required this.id,
    required this.text,
    required this.options,
  });
  
  factory Question.fromJson(Map<String, dynamic> json) {
    return Question(
      id: json['id'],
      text: json['text'],
      options: List<String>.from(json['options']),
    );
  }
}

class HexaEliteTutorPage extends StatefulWidget {
  const HexaEliteTutorPage({Key? key}) : super(key: key);

  @override
  State<HexaEliteTutorPage> createState() => _HexaEliteTutorPageState();
}

class _HexaEliteTutorPageState extends State<HexaEliteTutorPage> {
  int _currentPage = 0;
  List<int> _selectedAnswers = [];
  final int _totalPages = 9;
  late List<Question> _questions;
  
  @override
  void initState() {
    super.initState();
    _loadQuestions();
  }
  
  void _loadQuestions() {
    // Sample JSON data - In a real app, this could come from an API
    final String jsonData = '''
    [
      {
        "id": 1,
        "text": "Aspen is as close as one can get to a storybook alpine own in America?",
        "options": ["possibilities", "shopping", "hiking", "Aspen"]
      },
      {
        "id": 2,
        "text": "Aspen is as close as one can get to a storybook alpine own in America?",
        "options": ["possibilities", "shopping", "hiking", "Aspen"]
      },
      {
        "id": 3,
        "text": "Aspen is as close as one can get to a storybook alpine own in America?",
        "options": ["possibilities", "shopping", "hiking", "Aspen"]
      },
      {
        "id": 4,
        "text": "What is the capital city of France?",
        "options": ["London", "Paris", "Berlin", "Rome"]
      },
      {
        "id": 5,
        "text": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Mars", "Venus", "Jupiter"]
      },
      {
        "id": 6,
        "text": "What is the chemical symbol for gold?",
        "options": ["Au", "Ag", "Fe", "Cu"]
      },
      {
        "id": 7,
        "text": "Who painted the Mona Lisa?",
        "options": ["Vincent van Gogh", "Pablo Picasso", "Leonardo da Vinci", "Michelangelo"]
      },
      {
        "id": 8,
        "text": "What is the largest ocean on Earth?",
        "options": ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean", "Pacific Ocean"]
      },
      {
        "id": 9,
        "text": "Which is the tallest mountain in the world?",
        "options": ["K2", "Mount Everest", "Kangchenjunga", "Lhotse"]
      },
      {
        "id": 10,
        "text": "What is the hardest natural substance on Earth?",
        "options": ["Gold", "Iron", "Diamond", "Platinum"]
      }
    ]
    ''';
    
    final List<dynamic> decodedData = json.decode(jsonData);
    _questions = decodedData.map((item) => Question.fromJson(item)).toList();
    
    // Limit to 10 questions maximum
    if (_questions.length > 10) {
      _questions = _questions.sublist(0, 10);
    }
    
    // Initialize selected answers list with -1 (nothing selected)
    _selectedAnswers = List.filled(_questions.length, -1);
    
    // For demo purposes, set some initial selections
    _selectedAnswers[0] = 1;  // Question 1, option B selected
    _selectedAnswers[1] = 3;  // Question 2, option D selected
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Container(
          color: Colors.white,
          child: Column(
            children: [
              // App Bar
              _buildAppBar(),
              
              // Search and Question Button
              _buildSearchBar(),
              
              // Quiz Section
              _buildQuizSection(),
              
              // Page Navigation
              _buildPageNavigation(),
              
              // Submit Button
              _buildSubmitButton(),
              
              // Bottom Navigation
              _buildBottomNavigation(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAppBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              const Text(
                'HexaElite',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(width: 8),
              Row(
                children: [
                  Container(
                    width: 8,
                    height: 8,
                    decoration: const BoxDecoration(
                      color: Colors.blue,
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 4),
                  const Text(
                    'Ashad, Samsudeen',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey,
                    ),
                  ),
                  const Icon(Icons.keyboard_arrow_down, size: 16),
                ],
              ),
            ],
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {},
          ),
        ],
      ),
    );
  }

  Widget _buildSearchBar() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: [
          Expanded(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: Colors.grey[200],
                borderRadius: BorderRadius.circular(20),
              ),
              child: Row(
                children: const [
                  Icon(Icons.search, color: Colors.grey, size: 20),
                  SizedBox(width: 4),
                  Text(
                    'Ask Questions',
                    style: TextStyle(
                      color: Colors.grey,
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.grey[400],
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              children: const [
                Text(
                  'Question',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 14,
                  ),
                ),
                SizedBox(width: 4),
                Icon(Icons.arrow_forward, color: Colors.white, size: 16),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuizSection() {
    return Expanded(
      child: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Select Answer All Questions',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            
            // Loop through questions from JSON data
            for (int i = 0; i < _questions.length && i < 10; i++)
              Column(
                children: [
                  _buildQuestionItem(
                    questionNumber: _questions[i].id,
                    questionText: _questions[i].text,
                    options: _questions[i].options,
                    selectedOptionIndex: _selectedAnswers[i],
                    onOptionSelected: (index) {
                      setState(() {
                        _selectedAnswers[i] = index;
                      });
                    },
                  ),
                  const SizedBox(height: 12),
                ],
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuestionItem({
    required int questionNumber,
    required String questionText,
    required List<String> options,
    required int selectedOptionIndex,
    required Function(int) onOptionSelected,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '$questionNumber. $questionText',
          style: const TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 8),
        ...List.generate(
          options.length,
          (index) => _buildOptionItem(
            label: '${String.fromCharCode(97 + index)}. ${options[index]}',
            isSelected: selectedOptionIndex == index,
            onTap: () => onOptionSelected(index),
          ),
        ),
      ],
    );
  }

  Widget _buildOptionItem({
    required String label,
    required bool isSelected,
    required VoidCallback onTap,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        children: [
          Expanded(
            child: Text(
              label,
              style: const TextStyle(fontSize: 13),
            ),
          ),
          GestureDetector(
            onTap: onTap,
            child: Container(
              width: 20,
              height: 20,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(
                  color: Colors.grey,
                  width: 1,
                ),
                color: isSelected ? Colors.black : Colors.white,
              ),
              child: isSelected
                  ? const Center(
                      child: Icon(
                        Icons.circle,
                        size: 10,
                        color: Colors.white,
                      ),
                    )
                  : null,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPageNavigation() {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: List.generate(
          _totalPages > 9 ? 9 : _totalPages,
          (index) => _buildPageIndicator(index),
        ),
      ),
    );
  }

  Widget _buildPageIndicator(int index) {
    return GestureDetector(
      onTap: () {
        setState(() {
          _currentPage = index;
        });
      },
      child: Container(
        width: 26,
        height: 26,
        margin: const EdgeInsets.symmetric(horizontal: 2),
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: _currentPage == index ? Colors.blue[100] : Colors.grey[200],
        ),
        child: Center(
          child: Text(
            '${index + 1}',
            style: TextStyle(
              color: _currentPage == index ? Colors.blue[800] : Colors.grey[600],
              fontWeight: _currentPage == index ? FontWeight.bold : FontWeight.normal,
              fontSize: 12,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSubmitButton() {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Container(
        width: 180,
        height: 45,
        decoration: BoxDecoration(
          color: Colors.grey[600],
          borderRadius: BorderRadius.circular(22),
        ),
    child: GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => const CongratulationsScreen()),
        );
      },
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: const [
          Text(
            'Submit Answers',
            style: TextStyle(
              color: Colors.white,
              fontSize: 14,
              fontWeight: FontWeight.bold,
            ),
          ),
          SizedBox(width: 6),
          Icon(
            Icons.arrow_forward,
            color: Colors.white,
            size: 18,
          ),
        ],
      ),
    ),
  ),
);
  }

  Widget _buildBottomNavigation() {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12),
      decoration: BoxDecoration(
        border: Border(
          top: BorderSide(
            color: Colors.grey[300]!,
            width: 1,
          ),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          _buildBottomNavItem(Icons.remove, isSelected: false),
          _buildBottomNavItem(Icons.crop_7_5, isSelected: true),
          _buildBottomNavItem(Icons.favorite_border, isSelected: false),
          _buildBottomNavItem(Icons.person_outline, isSelected: false),
        ],
      ),
    );
  }

  Widget _buildBottomNavItem(IconData icon, {required bool isSelected}) {
    return Container(
      padding: const EdgeInsets.all(6),
      decoration: BoxDecoration(
        color: isSelected ? Colors.grey[300] : Colors.transparent,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Icon(
        icon,
        color: isSelected ? Colors.black : Colors.grey,
        size: 20,
      ),
    );
  }
}