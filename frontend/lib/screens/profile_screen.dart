import 'package:flutter/material.dart';
import '../api/api_service.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final ApiService _api = ApiService();
  Map<String, dynamic>? _user;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  void _loadProfile() async {
    final data = await _api.getProfile();
    if (mounted) {
      setState(() {
        _user = data;
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) return const Center(child: CircularProgressIndicator());
    
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          const CircleAvatar(radius: 50, child: Icon(Icons.person, size: 50)),
          const SizedBox(height: 16),
          Text(_user?['full_name'] ?? 'Name', style: Theme.of(context).textTheme.headlineMedium),
          Text("${_user?['city']}, ${_user?['area']}", style: Theme.of(context).textTheme.bodyLarge),
          const Divider(),
          ListTile(
            title: const Text("Intent"),
            subtitle: Text(_user?['intent'] ?? 'Not set'),
          ),
          ListTile(
            title: const Text("Current Requirement"),
            subtitle: Text(_user?['requirement'] ?? 'None'),
          ),
          ListTile(
            title: const Text("Bio"),
            subtitle: Text(_user?['bio'] ?? 'No bio'),
          ),
          const SizedBox(height: 20),
          ElevatedButton(
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text("Edit Profile Not Implemented in Demo")));
            },
            child: const Text("Edit Profile"),
          )
        ],
      ),
    );
  }
}
