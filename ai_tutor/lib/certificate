import 'package:flutter/material.dart';

void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'HexaElite Certificate',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: CertificatePage(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class CertificatePage extends StatelessWidget {
  const CertificatePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Color(0xFFEAEFFF),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header Row
              Row(
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'AI Tutor',
                        style: TextStyle(fontSize: 14, color: Colors.black87),
                      ),
                      Text(
                        'HexaElite',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Colors.black,
                        ),
                      ),
                    ],
                  ),
                  Spacer(),
                  Icon(Icons.location_on, color: Colors.blue),
                  SizedBox(width: 4),
                  Text('Ashad, Samsudeen'),
                  SizedBox(width: 8),
                  Icon(Icons.settings),
                ],
              ),
              SizedBox(height: 24),

              // Certificate Image
              Center(
                child: Container(
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.grey.shade300),
                    boxShadow: [
                      BoxShadow(blurRadius: 6, color: Colors.grey.shade200)
                    ],
                  ),
                  child: Image.asset(
                    'assets/Certificate.png', // Replace with your actual filename
                    width: 300,
                    height: 180,
                    fit: BoxFit.cover,
                  ),
                ),
              ),
              SizedBox(height: 24),

              // Message
              Center(
                child: Text(
                  "Congratulation you got 87% mark from the quiz...",
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
                ),
              ),
              SizedBox(height: 32),

              // Buttons
              CustomButton(text: "Download Certificate", onTap: () {}),
              SizedBox(height: 16),
              CustomButton(text: "Share Your Social", onTap: () {}),
              SizedBox(height: 16),
              CustomButton(text: "Go to Leader Board", onTap: () {}),
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

class CustomButton extends StatelessWidget {
  final String text;
  final VoidCallback onTap;

  const CustomButton({required this.text, required this.onTap, super.key});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: ElevatedButton(
        onPressed: onTap,
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.grey.shade800,
          padding: EdgeInsets.symmetric(horizontal: 32, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          elevation: 8,
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(text, style: TextStyle(color: Colors.white)),
            SizedBox(width: 8),
            Icon(Icons.arrow_forward, color: Colors.white),
          ],
        ),
      ),
    );
  }
}
