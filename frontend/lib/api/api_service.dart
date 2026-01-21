import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  // Use 10.0.2.2 for Android Emulator, localhost for Web/iOS
  // For Real Device, use your PC's local IP (e.g., 192.168.1.x)
  static const String baseUrl = "http://127.0.0.1:8000"; 
  
  String? _token;

  Future<void> loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString('jwt_token');
  }

  Future<void> saveToken(String token) async {
    _token = token;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('jwt_token', token);
  }

  Future<void> logout() async {
    _token = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('jwt_token');
  }

  Map<String, String> get _headers {
    final headers = {"Content-Type": "application/json"};
    if (_token != null) {
      headers["Authorization"] = "Bearer $_token";
    }
    return headers;
  }

  // Auth
  Future<bool> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {"Content-Type": "application/x-www-form-urlencoded"},
      body: {"username": email, "password": password},
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      await saveToken(data['access_token']);
      return true;
    }
    return false;
  }

  Future<bool> signup(String email, String password, String fullName, String city, String area) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/signup'),
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "email": email,
        "password": password,
        "full_name": fullName,
        "city": city,
        "area": area,
        "intent": "Friendship", // Default
        "hobbies": []
      }),
    );
    return response.statusCode == 200;
  }

  Future<Map<String, dynamic>?> getProfile() async {
    final response = await http.get(Uri.parse('$baseUrl/auth/me'), headers: _headers);
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return null;
  }

  Future<bool> updateProfile(Map<String, dynamic> updates) async {
    final response = await http.put(
      Uri.parse('$baseUrl/users/profile'),
      headers: _headers,
      body: jsonEncode(updates),
    );
    return response.statusCode == 200;
  }

  // Discovery
  Future<List<dynamic>> discoverPeople() async {
    final response = await http.get(Uri.parse('$baseUrl/users/discover'), headers: _headers);
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return [];
  }

  // Connections
  Future<bool> sendRequest(int userId) async {
    final response = await http.post(Uri.parse('$baseUrl/connections/request/$userId'), headers: _headers);
    return response.statusCode == 200;
  }

  Future<List<dynamic>> getConnections() async {
    final response = await http.get(Uri.parse('$baseUrl/connections'), headers: _headers);
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return [];
  }

  Future<List<dynamic>> getRequests() async {
    final response = await http.get(Uri.parse('$baseUrl/connections/requests'), headers: _headers);
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return [];
  }
  
  Future<bool> respondToRequest(int connectionId, bool accept) async {
    final action = accept ? 'accept' : 'reject';
    final response = await http.put(Uri.parse('$baseUrl/connections/$action/$connectionId'), headers: _headers);
    return response.statusCode == 200;
  }

  // Chat History
  Future<List<dynamic>> getChatHistory(int otherUserId) async {
    final response = await http.get(Uri.parse('$baseUrl/chat/history/$otherUserId'), headers: _headers);
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return [];
  }
}
