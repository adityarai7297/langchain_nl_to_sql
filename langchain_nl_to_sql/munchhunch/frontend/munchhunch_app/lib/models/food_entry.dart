class FoodEntry {
  final int? id;
  final String item;
  final String quantity;
  final DateTime timeEaten;
  final int calories;
  final double protein;
  final double carbs;
  final double fats;
  final double fiber;

  FoodEntry({
    this.id,
    required this.item,
    required this.quantity,
    required this.timeEaten,
    required this.calories,
    required this.protein,
    required this.carbs,
    required this.fats,
    required this.fiber,
  });

  factory FoodEntry.fromJson(Map<String, dynamic> json) {
    return FoodEntry(
      id: json['id'],
      item: json['item'],
      quantity: json['quantity'],
      timeEaten: DateTime.parse(json['time_eaten']),
      calories: json['calories'],
      protein: json['protein'].toDouble(),
      carbs: json['carbs'].toDouble(),
      fats: json['fats'].toDouble(),
      fiber: json['fiber'].toDouble(),
    );
  }
} 