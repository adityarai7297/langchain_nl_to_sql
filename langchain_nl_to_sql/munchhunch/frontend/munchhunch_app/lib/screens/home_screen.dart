import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/food_provider.dart';
import '../models/food_entry.dart';
import 'add_entry_screen.dart';
import '../services/audio_service.dart';
import '../widgets/voice_input_button.dart';

class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final entriesAsync = ref.watch(foodEntriesProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('MunchHunch'),
        actions: [
          VoiceInputButton(
            onTranscribed: (text) {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (context) => AddEntryScreen(initialText: text),
                ),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.refresh(foodEntriesProvider),
          ),
        ],
      ),
      body: entriesAsync.when(
        data: (entries) => FoodEntriesList(entries: entries),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(
          child: Text('Error: ${error.toString()}'),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => Navigator.of(context).push(
          MaterialPageRoute(
            builder: (context) => const AddEntryScreen(),
          ),
        ),
        child: const Icon(Icons.add),
      ),
    );
  }
}

class FoodEntriesList extends StatelessWidget {
  final List<FoodEntry> entries;

  const FoodEntriesList({
    super.key,
    required this.entries,
  });

  @override
  Widget build(BuildContext context) {
    if (entries.isEmpty) {
      return const Center(
        child: Text('No entries yet. Add your first meal!'),
      );
    }

    return ListView.builder(
      itemCount: entries.length,
      itemBuilder: (context, index) {
        final entry = entries[index];
        return FoodEntryCard(entry: entry);
      },
    );
  }
}

class FoodEntryCard extends StatelessWidget {
  final FoodEntry entry;

  const FoodEntryCard({
    super.key,
    required this.entry,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    entry.item,
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                ),
                Text(
                  '${entry.quantity}',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'Time: ${_formatDateTime(entry.timeEaten)}',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 8),
            MacroNutrientsRow(entry: entry),
          ],
        ),
      ),
    );
  }

  String _formatDateTime(DateTime dateTime) {
    return '${dateTime.hour.toString().padLeft(2, '0')}:'
           '${dateTime.minute.toString().padLeft(2, '0')} - '
           '${dateTime.day}/${dateTime.month}/${dateTime.year}';
  }
}

class MacroNutrientsRow extends StatelessWidget {
  final FoodEntry entry;

  const MacroNutrientsRow({
    super.key,
    required this.entry,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      children: [
        MacroNutrient(
          label: 'Calories',
          value: entry.calories.toString(),
          unit: 'kcal',
          color: Colors.red,
        ),
        MacroNutrient(
          label: 'Protein',
          value: entry.protein.toStringAsFixed(1),
          unit: 'g',
          color: Colors.blue,
        ),
        MacroNutrient(
          label: 'Carbs',
          value: entry.carbs.toStringAsFixed(1),
          unit: 'g',
          color: Colors.orange,
        ),
        MacroNutrient(
          label: 'Fats',
          value: entry.fats.toStringAsFixed(1),
          unit: 'g',
          color: Colors.yellow,
        ),
      ],
    );
  }
}

class MacroNutrient extends StatelessWidget {
  final String label;
  final String value;
  final String unit;
  final Color color;

  const MacroNutrient({
    super.key,
    required this.label,
    required this.value,
    required this.unit,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall,
        ),
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 8,
              height: 8,
              decoration: BoxDecoration(
                color: color,
                shape: BoxShape.circle,
              ),
            ),
            const SizedBox(width: 4),
            Text(
              '$value$unit',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        ),
      ],
    );
  }
}
