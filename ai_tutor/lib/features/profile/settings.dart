import 'package:flutter/material.dart';
import 'package:ai_tutor/core/CustomAppBar.dart';
import 'package:ai_tutor/core/BottomNavigator.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Settings Screen',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: SettingsScreen(),
    );
  }
}

class SettingsScreen extends StatefulWidget {
  @override
  _SettingsScreenState createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _isNotificationEnabled = false;
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
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
        children:[
         Row(
          children: [
          
         IconButton(
          icon: Icon(Icons.arrow_back, color: Colors.black),
          onPressed: () {},
        ),
            Text('Settings', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
           ],
           ),
            SizedBox(height: 16),
            Container(
              padding: EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color.fromARGB(255, 128, 128, 128),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Column(
                children: [
                
                  _buildSettingItem(Icons.person, 'Accounts settings', () {
                    // Handle Accounts settings tap
                  }),
                  _buildSettingItem(Icons.notifications, 'Notifications', () {
                    // Handle Notifications tap
                  }),
SwitchListTile(
      title: DefaultTextStyle(
        style: TextStyle(color: Colors.white),
        child: Text('App notification'),
      ),
      value: _isNotificationEnabled, // Replace with actual value
      onChanged: (value) {
        setState(() {
          _isNotificationEnabled = value;
        });
        // Handle switch change
      },
    ),
                  _buildSettingItem(Icons.language, 'Language & Region', () {
                    // Handle Language & Region tap
                  }),
                  _buildSettingItem(Icons.privacy_tip, 'Privacy settings', () {
                    // Handle Privacy settings tap
                  }),
                  _buildSettingItem(Icons.info, 'About', () {
                    // Handle About tap
                  }),
                  _buildSettingItem(Icons.logout, 'Logout', () {
                    // Handle Logout tap
                  }),
                ],
              ),
            ),
          ],
        ),
      ),
      
      bottomNavigationBar: BottomNavigator(
        currentIndex: _currentIndex,
        onTap: _onTabTapped,
      ),
    );
  }

  Widget _buildSettingItem(IconData icon, String title, VoidCallback onTap) {
    return ListTile(
      leading: Icon(icon),
      title: Text(title),
      titleTextStyle: TextStyle(
        fontSize: 16,
        color: Colors.white,
      ),
      iconColor: Colors.white,
      onTap: onTap,
    );
  }
}