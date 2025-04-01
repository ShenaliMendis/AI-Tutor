import 'package:flutter/material.dart';

void main() {
  runApp(MaterialApp(
    home: UpdateScreen(),
    debugShowCheckedModeBanner: false,
  ));
}

class UpdateScreen extends StatefulWidget {
  const UpdateScreen({Key? key}) : super(key: key);

  @override
  _UpdateScreenState createState() => _UpdateScreenState();
}

class _UpdateScreenState extends State<UpdateScreen> {
  DateTime? _selectedDate;
  Map<String, bool> _isEditing = {
    'username': false,
    'email': false,
    'date': false,
    'age': false,
    'education': false,
    'password': false,
    'verifyPassword': false,
  };

  TextEditingController _usernameController = TextEditingController(text: 'saduni');
  TextEditingController _emailController = TextEditingController(text: 'example@example.com');
  TextEditingController _dateController = TextEditingController(text: '2000-01-1');
  TextEditingController _ageController = TextEditingController(text: '25');
  TextEditingController _educationController = TextEditingController(text: 'Bachelor\'s Degree');
  TextEditingController _passwordController = TextEditingController(text: '12345');
  TextEditingController _verifyPasswordController = TextEditingController();

  Future<void> _selectDate(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(1900),
      lastDate: DateTime(2101),
    );
    if (picked != null && picked != _selectedDate) {
      setState(() {
        _selectedDate = picked;
        _dateController.text = "${_selectedDate!.toLocal()}".split(' ')[0];
      });
    }
  }

  void _updateDetails() {
    // Implement your update logic here
    // For example, you can print the updated details to the console
    print('Username: ${_usernameController.text}');
    print('Email: ${_emailController.text}');
    print('Date of Birth: ${_dateController.text}');
    print('Age: ${_ageController.text}');
    print('Education: ${_educationController.text}');
    print('Password: ${_passwordController.text}');
    print('Verify Password: ${_verifyPasswordController.text}');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[850], // Dark grey background
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Padding(
          padding: const EdgeInsets.all(10.10),
        ),
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              margin: EdgeInsets.all(4.4),
              padding: EdgeInsets.all(5),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(10),
              ),
              child: IconButton(
                icon: Icon(Icons.arrow_back_ios, color: Colors.black),
                onPressed: () {
                  Navigator.pop(context);
                },
              ),
            ),
            Text(
              'Account Details',
              style: TextStyle(
                color: Colors.white,
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 20),
            _buildEditableField('username', Icons.person, 'user name', controller: _usernameController),
            SizedBox(height: 10),
            _buildEditableField('email', Icons.email, 'email', controller: _emailController),
            SizedBox(height: 10),
            _buildEditableField('date', Icons.calendar_today, 'Select date of birth', isDateField: true, controller: _dateController),
            SizedBox(height: 10),
            _buildEditableField('age', Icons.confirmation_number, 'Select date of birth', controller: _ageController),
            SizedBox(height: 10),
            _buildEditableField('education', Icons.school, 'educational status', controller: _educationController),
            SizedBox(height: 10),
            _buildEditableField('password', Icons.lock, 'password', obscureText: true, controller: _passwordController),
            SizedBox(height: 10),
            _buildEditableField('verifyPassword', Icons.lock, 'Verify new password', obscureText: true, controller: _verifyPasswordController),
            SizedBox(height: 20),
            Center(
              child: ElevatedButton(
                onPressed: _updateDetails,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.black,
                  foregroundColor: Colors.white,
                  padding: EdgeInsets.symmetric(horizontal: 40, vertical: 15),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(5),
                  ),
                ),
                child: Text('Update'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEditableField(String key, IconData icon, String labelText, {bool obscureText = false, bool isDateField = false, TextEditingController? controller}) {
    return Row(
      children: [
        Expanded(
          child: isDateField && _isEditing[key] == true
              ? GestureDetector(
                  onTap: () => _selectDate(context),
                  child: Container(
                    padding: EdgeInsets.symmetric(vertical: 15, horizontal: 10),
                    decoration: BoxDecoration(
                      border: Border.all(color: Colors.white),
                      borderRadius: BorderRadius.circular(5),
                    ),
                    child: Row(
                      children: [
                        Icon(icon, color: Colors.white),
                        SizedBox(width: 10),
                        Text(
                          _selectedDate == null
                              ? labelText
                              : "${_selectedDate!.toLocal()}".split(' ')[0],
                          style: TextStyle(color: Colors.white),
                        ),
                      ],
                    ),
                  ),
                )
              : _buildTextField(
                  icon: icon,
                  labelText: labelText,
                  obscureText: obscureText,
                  enabled: _isEditing[key] ?? false,
                  controller: controller,
                ),
        ),
        IconButton(
          icon: Icon(Icons.edit, color: Colors.white),
          onPressed: () {
            setState(() {
              _isEditing[key] = !_isEditing[key]!;
            });
          },
        ),
      ],
    );
  }

  Widget _buildTextField({
    required IconData icon,
    required String labelText,
    bool obscureText = false,
    bool enabled = false,
    TextEditingController? controller,
  }) {
    return TextField(
      style: TextStyle(color: Colors.white),
      obscureText: obscureText,
      enabled: enabled,
      controller: controller,
      decoration: InputDecoration(
        prefixIcon: Icon(icon, color: Colors.white),
        labelText: labelText,
        labelStyle: TextStyle(color: Colors.white),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(5),
          borderSide: BorderSide(color: Colors.white),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(5),
          borderSide: BorderSide(color: Colors.white),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(5),
          borderSide: BorderSide(color: Colors.white),
        ),
      ),
    );
  }
}

