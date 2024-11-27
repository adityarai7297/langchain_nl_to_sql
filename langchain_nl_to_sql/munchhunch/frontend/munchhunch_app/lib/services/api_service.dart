import 'package:dio/dio.dart';
import '../models/food_entry.dart';

class ApiService {
  final Dio _dio;

  ApiService() : 
    _dio = Dio() {
    _dio.options.baseUrl = 'http://localhost:8006/api';
    _dio.options.headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
  }

  Future<List<FoodEntry>> processFoodEntry(String input) async {
    try {
      final response = await _dio.post('/food-entries', 
        data: {'input_text': input}
      );
      
      return (response.data as List)
          .map((json) => FoodEntry.fromJson(json))
          .toList();
    } catch (e) {
      throw Exception('Failed to process food entry: $e');
    }
  }

  Future<List<FoodEntry>> getFoodEntries() async {
    try {
      final response = await _dio.get('/food-entries');
      
      return (response.data as List)
          .map((json) => FoodEntry.fromJson(json))
          .toList();
    } catch (e) {
      throw Exception('Failed to fetch food entries: $e');
    }
  }
} 