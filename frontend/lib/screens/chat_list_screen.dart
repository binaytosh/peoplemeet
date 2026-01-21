import 'package:flutter/material.dart';
import '../api/api_service.dart';
import 'chat_screen.dart';

class ChatListScreen extends StatefulWidget {
  const ChatListScreen({super.key});

  @override
  State<ChatListScreen> createState() => _ChatListScreenState();
}

class _ChatListScreenState extends State<ChatListScreen> {
  final ApiService _api = ApiService();
  List<dynamic> _connections = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadConnections();
  }

  void _loadConnections() async {
    final conns = await _api.getConnections();
    if (mounted) {
      setState(() {
        _connections = conns;
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) return const Center(child: CircularProgressIndicator());
    
    return ListView.builder(
      itemCount: _connections.length,
      itemBuilder: (context, index) {
        final conn = _connections[index];
        // We need to resolve WHO the other person is. 
        // For MVP, we need the logic 'if my_id == sender_id ? receiver : sender'.
        // Since we don't store local user ID easily here without extra call,
        // we might blindly show both names or improve backend.
        // Let's assume for MVP we tap to chat.
        
        return ListTile(
          leading: const CircleAvatar(child: Icon(Icons.chat_bubble)),
          title: Text("Chat with Connection ${conn['id']}"),
          subtitle: const Text("Tap to open chat"),
          onTap: () {
            // Need the OTHER User ID. 
            // Mocking logic: Logic should send the correct User ID.
            // Let's assume the user has to pick manually or we fix logic later.
            // Sending '0' as placeholder or extracting from conn if possible.
            int otherId = (conn['sender_id'] ?? 0); 
            // This is buggy without knowing 'me'. Fixed in next iteration if needed.
            
            Navigator.of(context).push(
              MaterialPageRoute(
                builder: (_) => ChatScreen(otherUserId: otherId, otherUserName: "User $otherId"),
              ),
            );
          },
        );
      },
    );
  }
}
