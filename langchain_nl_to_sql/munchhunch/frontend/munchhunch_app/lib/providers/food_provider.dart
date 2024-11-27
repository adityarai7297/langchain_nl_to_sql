import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/food_entry.dart';
import '../services/api_service.dart';

final apiServiceProvider = Provider((ref) => ApiService());

final foodEntriesProvider = FutureProvider<List<FoodEntry>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  return apiService.getFoodEntries();
});

final addFoodEntryProvider = FutureProvider.family<List<FoodEntry>, String>(
  (ref, input) async {
    final apiService = ref.watch(apiServiceProvider);
    return apiService.processFoodEntry(input);
  }
); 