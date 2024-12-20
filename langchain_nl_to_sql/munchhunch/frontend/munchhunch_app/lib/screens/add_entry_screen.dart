import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/food_provider.dart';
import '../widgets/chat_input.dart';

class AddEntryScreen extends ConsumerStatefulWidget {
  final String? initialText;

  const AddEntryScreen({
    super.key,
    this.initialText,
  });

  @override
  ConsumerState<AddEntryScreen> createState() => _AddEntryScreenState();
}

class _AddEntryScreenState extends ConsumerState<AddEntryScreen> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _itemController;
  bool _isProcessing = false;
  String _processingStatus = '';

  @override
  void initState() {
    super.initState();
    _itemController = TextEditingController(text: widget.initialText);
  }

  @override
  void dispose() {
    _itemController.dispose();
    super.dispose();
  }

  Future<void> _processEntry() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isProcessing = true;
      _processingStatus = 'Identifying food items...';
    });

    try {
      await Future.delayed(const Duration(milliseconds: 2000));
      setState(() => _processingStatus = 'Looking up nutritional information...');
      
      await Future.delayed(const Duration(milliseconds: 2000));
      setState(() => _processingStatus = 'Validating data...');

      await Future.delayed(const Duration(milliseconds: 2000));
      setState(() => _processingStatus = 'Finishing up...');

      await Future.delayed(const Duration(milliseconds: 2000));
      setState(() => _processingStatus = 'Yum Yum...');
      
      await ref.read(addFoodEntryProvider(_itemController.text).future);
      
      setState(() => _processingStatus = 'Storing entry...');
      
      if (mounted) {
        ref.refresh(foodEntriesProvider);
        Navigator.of(context).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Food entry added successfully!')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: ${e.toString()}')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isProcessing = false;
          _processingStatus = '';
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Add Food Entry'),
      ),
      body: Stack(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Expanded(
                    child: Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Tips:',
                              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 8),
                            const Text('• Include the quantity of food'),
                            const Text('• Mention when you ate it'),
                            const Text('• Be as specific as possible'),
                            const Text('• Example: "2 slices of pepperoni pizza at 1pm"'),
                          ],
                        ),
                      ),
                    ),
                  ),
                  ChatInput(
                    onSubmit: (text) {
                      _itemController.text = text;
                      _processEntry();
                    },
                  ),
                ],
              ),
            ),
          ),
          if (_isProcessing)
            Container(
              color: Colors.black54,
              child: Center(
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const CircularProgressIndicator(),
                        const SizedBox(height: 16),
                        Text(_processingStatus),
                      ],
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
