import 'package:flutter/material.dart';
import '../api/api_service.dart';

class DiscoveryScreen extends StatefulWidget {
  const DiscoveryScreen({super.key});

  @override
  State<DiscoveryScreen> createState() => _DiscoveryScreenState();
}

class _DiscoveryScreenState extends State<DiscoveryScreen> {
  final ApiService _api = ApiService();
  List<dynamic> _people = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadPeople();
  }

  void _loadPeople() async {
    final people = await _api.discoverPeople();
    if (mounted) {
      setState(() {
        _people = people;
        _isLoading = false;
      });
    }
  }

  void _sendRequest(int userId) async {
    final success = await _api.sendRequest(userId);
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(success ? 'Request Sent!' : 'Failed to send request')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) return const Center(child: CircularProgressIndicator());
    if (_people.isEmpty) return const Center(child: Text("No matches found yet."));

    return ListView.builder(
      itemCount: _people.length,
      itemBuilder: (context, index) {
        final item = _people[index];
        final user = item['user'];
        final score = item['score'];

        return Card(
          margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: ListTile(
            leading: CircleAvatar(child: Text(user['full_name'][0])),
            title: Text("${user['full_name']} (${user['age'] ?? 'N/A'})"),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text("${user['city']} • ${user['area']}"),
                Text("Match Score: $score", style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.green)),
                Text(user['intent'] ?? ''),
              ],
            ),
            trailing: IconButton(
              icon: const Icon(Icons.person_add, color: Colors.blue),
              onPressed: () => _sendRequest(user['id']),
            ),
          ),
        );
      },
    );
  }
}
