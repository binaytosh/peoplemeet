import 'package:flutter/material.dart';
import '../api/api_service.dart';

class ConnectionsScreen extends StatefulWidget {
  const ConnectionsScreen({super.key});

  @override
  State<ConnectionsScreen> createState() => _ConnectionsScreenState();
}

class _ConnectionsScreenState extends State<ConnectionsScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final ApiService _api = ApiService();
  List<dynamic> _connections = [];
  List<dynamic> _requests = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _loadData();
  }

  void _loadData() async {
    final reqs = await _api.getRequests();
    final conns = await _api.getConnections();
    if (mounted) {
      setState(() {
        _requests = reqs;
        _connections = conns;
        _isLoading = false;
      });
    }
  }

  void _respond(int id, bool accept) async {
    await _api.respondToRequest(id, accept);
    _loadData(); // Refresh
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) return const Center(child: CircularProgressIndicator());

    return Column(
      children: [
        TabBar(
          controller: _tabController,
          labelColor: Colors.deepPurple,
          tabs: const [Tab(text: "Requests"), Tab(text: "Friends")],
        ),
        Expanded(
          child: TabBarView(
            controller: _tabController,
            children: [
              // Requests Tab
              _requests.isEmpty
                  ? const Center(child: Text("No pending requests"))
                  : ListView.builder(
                      itemCount: _requests.length,
                      itemBuilder: (ctx, i) {
                        final req = _requests[i];
                        final sender = req['sender']; 
                        return ListTile(
                          title: Text(sender != null ? sender['full_name'] : "Unknown"),
                          subtitle: const Text("Wants to connect"),
                          trailing: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              IconButton(
                                icon: const Icon(Icons.check, color: Colors.green),
                                onPressed: () => _respond(req['id'], true),
                              ),
                              IconButton(
                                icon: const Icon(Icons.close, color: Colors.red),
                                onPressed: () => _respond(req['id'], false),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
              // Friends Tab
              _connections.isEmpty
                  ? const Center(child: Text("No connections yet"))
                  : ListView.builder(
                      itemCount: _connections.length,
                      itemBuilder: (ctx, i) {
                        final conn = _connections[i];
                        // Identify the other user (could be sender or receiver)
                        // In real app, we check current user ID. 
                        // Simplified: Backend usually returns 'friend' object or we parse it.
                        // For MVP: we display connection ID or inspect raw JSON to find 'other'.
                        // Let's assume Backend sends populated fields.
                        return ListTile(
                          leading: const Icon(Icons.person),
                          title: Text("Responded/Connected (ID: ${conn['id']})"),
                          subtitle: const Text("You can now chat!"),
                        );
                      },
                    ),
            ],
          ),
        ),
      ],
    );
  }
}
