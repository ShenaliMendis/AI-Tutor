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
      title: 'Hexa Elite Leaderboard',
      theme: ThemeData(
        primarySwatch: Colors.yellow,
        scaffoldBackgroundColor: Colors.white,
        fontFamily: 'Roboto',
      ),
      home: LeaderboardScreen(),
    );
  }
}

class LeaderboardScreen extends StatefulWidget {
  @override
  _LeaderboardScreenState createState() => _LeaderboardScreenState();
}

class _LeaderboardScreenState extends State<LeaderboardScreen> {
  int _currentIndex = 0;
  TextEditingController _searchController = TextEditingController();
  List<Map<String, dynamic>> filteredData = [];
  final List<Map<String, dynamic>> leaderboardData = [
    {'rank': 1, 'name': 'Mahesh Kumara', 'score': 965, 'icon': Icons.emoji_events},
    {'rank': 2, 'name': 'Ninesh Sanka', 'score': 865, 'icon': Icons.person},
    {'rank': 3, 'name': 'Roman Range', 'score': 826, 'icon': Icons.person},
    {'rank': 4, 'name': 'Pasan Bandara', 'score': 798, 'icon': Icons.emoji_events},
    {'rank': 5, 'name': 'Cristina Ronaldo', 'score': 766, 'icon': Icons.emoji_events},
    {'rank': 6, 'name': 'Sharuk Khan', 'score': 756, 'icon': Icons.person},
    {'rank': 7, 'name': 'Rithik Roshan', 'score': 740, 'icon': Icons.person},
  ];

  @override
  void initState() {
    super.initState();
    filteredData = leaderboardData;
    _searchController.addListener(_filterLeaderboard);
  }

  void _filterLeaderboard() {
    final query = _searchController.text.toLowerCase();
    setState(() {
      filteredData = leaderboardData
          .where((item) => item['name'].toLowerCase().contains(query))
          .toList();
    });
  }

  void _onTabTapped(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  String getRankSuffix(int rank) {
    if (rank == 1) return 'st';
    if (rank == 2) return 'nd';
    if (rank == 3) return 'rd';
    return 'th';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FA),
      appBar: const CustomAppBar(),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Search Bar
            Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _searchController,
                    decoration: InputDecoration(
                      hintText: 'Find Your Rank',
                      prefixIcon: Icon(Icons.search),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(50.0),
                      ),
                    ),
                  ),
                ),
                SizedBox(width: 8.0),
                ElevatedButton.icon(
                  onPressed: () {
                    // Handle search action
                  },
                  label: Text('Search'),
                  icon: Icon(Icons.arrow_forward),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Color.fromARGB(255, 185, 185, 185),
                  ),
                ),
              ],
            ),
            SizedBox(height: 8.0),
            // Suggestions
            if (_searchController.text.isNotEmpty)
              Container(
                height: 100.0,
                child: ListView.builder(
                  itemCount: filteredData.length,
                  itemBuilder: (context, index) {
                    final item = filteredData[index];
                    return ListTile(
                      title: Text(item['name']),
                      onTap: () {
                        _searchController.text = item['name'];
                        setState(() {
                          filteredData = [item];
                        });
                      },
                    );
                  },
                ),
              ),
            SizedBox(height: 24.0),
            // Leaderboard Title
            Center(
              child: Text(
                '~ Leader Board ~',
                style: TextStyle(
                  fontSize: 20.0,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            SizedBox(height: 16.0),
            // Table Header
            Row(
              children: [
                Expanded(
                  flex: 3,
                  child: Text(
                    'Rank',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
                Expanded(
                  flex: 8,
                  child: Text(
                    'Details',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
                Expanded(
                  flex: 2,
                  child: Text(
                    'Score',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
            SizedBox(height: 8.0),
            // Leaderboard List
            Expanded(
              child: ListView.builder(
                itemCount: filteredData.length,
                itemBuilder: (context, index) {
                  final item = filteredData[index];
                  return ListTile(
                    leading: Container(
                      padding: EdgeInsets.all(8.0),
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: Color.fromARGB(255, 128, 129, 129),
                      ),
                      child: Text(
                        '${item['rank']}${getRankSuffix(item['rank'])}',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    title: Container(
                      padding: EdgeInsets.all(8.0),
                      decoration: BoxDecoration(
                        border: Border.all(
                          color: Colors.grey[300]!,
                        ),
                        borderRadius: BorderRadius.circular(8.0),
                      ),
                      child: Row(
                        children: [
                          Container(
                            padding: EdgeInsets.all(4.0),
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: Colors.grey[300],
                            ),
                            child: Icon(
                              item['icon'],
                              size: 16.0,
                            ),
                          ),
                          SizedBox(width: 8.0),
                          Text(item['name']),
                        ],
                      ),
                    ),
                    trailing: Container(
                      padding: EdgeInsets.all(8.0),
                      decoration: BoxDecoration(
                        borderRadius: BorderRadius.circular(8.0),
                        color: Colors.grey[300],
                      ),
                      child: Text(
                        item['score'].toString(),
                        textAlign: TextAlign.center,
                      ),
                    ),
                    onTap: () {
                      // Handle item tap
                    },
                  );
                },
              ),
            ),
            SizedBox(height: 16.0),
            // Back Home Button
            Center(
              child: ElevatedButton.icon(
                icon: Icon(Icons.arrow_back),
                onPressed: () {
                  // Handle back home action
                },
                label: Text('Back Home'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Color.fromARGB(255, 137, 138, 138),
                ),
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
}
