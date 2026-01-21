import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;
import '../api/api_service.dart';

class ChatScreen extends StatefulWidget {
  final int otherUserId;
  final String otherUserName;

  const ChatScreen({super.key, required this.otherUserId, required this.otherUserName});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _msgCtrl = TextEditingController();
  final ApiService _api = ApiService();
  List<dynamic> _messages = [];
  WebSocketChannel? _channel;
  String? _token;

  @override
  void initState() {
    super.initState();
    _initChat();
  }

  void _initChat() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('jwt_token');
    
    // Load History
    final history = await _api.getChatHistory(widget.otherUserId);
    setState(() {
      _messages = history;
    });

    // Connect WS
    if (_token != null) {
      // Note: ws://10.0.2.2:8000/chat/ws/TOKEN
      final wsUrl = Uri.parse("ws://127.0.0.1:8000/chat/ws/$_token"); 
      _channel = WebSocketChannel.connect(wsUrl);
      
      _channel!.stream.listen((message) {
        final decoded = jsonDecode(message);
        // Only add if it belongs to this chat context
        if (decoded['sender_id'] == widget.otherUserId || decoded['receiver_id'] == widget.otherUserId) {
           setState(() {
             _messages.add(decoded);
           });
        }
      });
    }
  }

  void _sendMessage() {
    if (_msgCtrl.text.trim().isEmpty) return;
    final text = _msgCtrl.text.trim();
    
    final payload = jsonEncode({
      "receiver_id": widget.otherUserId,
      "content": text
    });
    
    _channel?.sink.add(payload);
    _msgCtrl.clear();
    // Optimistic UI update or wait for echo? 
    // Backend echoes back to sender, so we wait for echo in stream listener.
  }

  @override
  void dispose() {
    _channel?.sink.close(status.goingAway);
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.otherUserName)),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              itemCount: _messages.length,
              itemBuilder: (ctx, i) {
                final msg = _messages[i];
                final isMe = (msg['sender_id'] != widget.otherUserId); // Simplified logic
                return Align(
                  alignment: isMe ? Alignment.centerRight : Alignment.centerLeft,
                  child: Container(
                    margin: const EdgeInsets.symmetric(vertical: 4, horizontal: 8),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: isMe ? Colors.deepPurple[100] : Colors.grey[300],
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(msg['content']),
                  ),
                );
              },
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(8.0),
            child: Row(
              children: [
                Expanded(child: TextField(controller: _msgCtrl, decoration: const InputDecoration(hintText: "Type a message..."))),
                IconButton(icon: const Icon(Icons.send), onPressed: _sendMessage),
              ],
            ),
          )
        ],
      ),
    );
  }
}
