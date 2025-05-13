import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'HexaElite Courses',
      theme: ThemeData(primarySwatch: Colors.blue),
      debugShowCheckedModeBanner: false,
      home: CoursesScreen(),
    );
  }
}

class CoursesScreen extends StatelessWidget {
  const CoursesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFEAEFFF),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header Row
              Row(
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: const [
                      Text("AI Tutor", style: TextStyle(fontSize: 14)),
                      Text(
                        "HexaElite",
                        style: TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const Spacer(),
                  const Icon(Icons.location_on, color: Colors.blue),
                  const SizedBox(width: 4),
                  const Text("Ashad, Samsudeen"),
                  const SizedBox(width: 8),
                  const Icon(Icons.settings),
                ],
              ),
              const SizedBox(height: 20),

              // Title
              Row(
                children: const [
                  Icon(Icons.arrow_back),
                  SizedBox(width: 8),
                  Text(
                    "Select Rebuild Courses",
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
                  ),
                ],
              ),
              const SizedBox(height: 20),

              // Sections
              const TopicSection(title: "Most Popular Topics"),
              const TopicSection(title: "Most Popular Topics - beginner"),
              const TopicSection(title: "Most Popular Topics - intermediate"),
              const TopicSection(title: "Most Popular Topics - advanced"),
            ],
          ),
        ),
      ),

      // Bottom Nav Bar
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: 0,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: ''),
          BottomNavigationBarItem(
              icon: Icon(Icons.confirmation_num), label: ''),
          BottomNavigationBarItem(icon: Icon(Icons.favorite), label: ''),
          BottomNavigationBarItem(icon: Icon(Icons.person), label: ''),
        ],
        selectedItemColor: Colors.blue,
        unselectedItemColor: Colors.grey,
      ),
    );
  }
}

class TopicSection extends StatelessWidget {
  final String title;
  const TopicSection({required this.title, super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title,
            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
        const SizedBox(height: 10),
        SizedBox(
          height: 80,
          child: ListView(
            scrollDirection: Axis.horizontal,
            children: const [
              TopicCard(name: "Ethics", icon: Icons.wifi),
              TopicCard(name: "Nature", icon: Icons.restaurant),
              TopicCard(name: "Magic", icon: Icons.bathtub),
              TopicCard(name: "History", icon: Icons.history_edu),
            ],
          ),
        ),
        const SizedBox(height: 20),
      ],
    );
  }
}

class TopicCard extends StatelessWidget {
  final String name;
  final IconData icon;

  const TopicCard({required this.name, required this.icon, super.key});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 80,
      margin: const EdgeInsets.only(right: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.4),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 28, color: Colors.grey.shade700),
          const SizedBox(height: 8),
          Text(
            name,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(fontSize: 12),
          ),
        ],
      ),
    );
  }
}
