import 'package:flutter/material.dart';
import 'CustomAppBar.dart';
import 'BottomNavigator.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _currentIndex = 0;

  void _onTabTapped(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FA),
      appBar: const CustomAppBar(), // Use your CustomAppBar here
      body: Column(
        children: const [
          Expanded(child: Center(child: Text("Main Content Here"))),
        ],
      ),
      bottomNavigationBar: BottomNavigator(
        currentIndex: _currentIndex,
        onTap: _onTabTapped,
      ),
    );
  }
}


// import 'package:flutter/material.dart';
// import 'custom_app_bar.dart'; // Import your custom app bar

// void main() {
//   runApp(const MyApp());
// }

// class MyApp extends StatelessWidget {
//   const MyApp({super.key});

//   @override
//   Widget build(BuildContext context) {
//     return MaterialApp(
//       debugShowCheckedModeBanner: false,
//       home: const HomePage(),
//     );
//   }
// }

// class HomePage extends StatelessWidget {
//   const HomePage({super.key});

//   @override
//   Widget build(BuildContext context) {
//     return Scaffold(
//       backgroundColor: const Color(0xFFF5F7FA),
//       appBar: const CustomAppBar(), // Use your CustomAppBar here
//       body: const Center(
//         child: Text(
//           "Main Content Here",
//           style: TextStyle(fontSize: 18),
//         ),
//       ),
//     );
//   }
// }
